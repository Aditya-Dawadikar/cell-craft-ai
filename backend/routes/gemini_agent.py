import os
import traceback
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from session_management_2 import (apply_transform_and_checkpoint,
                                  branch_from_commit)
import json
import re
import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
from controllers.SessionController import (get_session_by_session_id,
                                           update_session)
from controllers.CommitController import (create_commit,
                                          get_commits_by_session_id,
                                          update_commit)
from s3_init import get_s3
from storage.storage_utils import (upload_commit_folder)
from models.requestModels.commit import GeneratedFile

from google import genai

import dotenv
dotenv.load_dotenv()

from services.langchain_chain import transform_chain

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Load your API key (from .env or hardcoded for testing)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)


router = APIRouter()

@router.post("/transform_csv/")
async def transform_csv(session_id: str = Form(...), query: str = Form(...)):
    try:
        session = await get_session_by_session_id(session_id=session_id)

        if not session:
            return JSONResponse(content={"error": "Invalid session ID"}, status_code=400)
    
        # 2. Ensure latest CSV is downloaded
        s3_key = session.last_csv_path  # e.g., session_files/<session_id>/<commit_id>/<commit_id>.csv
        local_path = os.path.join("session_files", s3_key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        s3 = get_s3()

        if not os.path.exists(local_path):
            s3.download_file(BUCKET_NAME, s3_key, local_path)

        df = pd.read_csv(local_path)

        # 3. Get commit history from DB
        all_commits = await get_commits_by_session_id(session_id)
        history = sorted(
            [c for c in all_commits if c.success],
            key=lambda c: c.timestamp
        )

        key_step_changelog = "\n".join(
            [f"- {c.commit_id}:{c.key_steps}" for c in history if c.key_steps]
        )

        df_preview = df.head(5).to_csv(index=False)

        inputs = {
            "preview": df_preview,
            "context": key_step_changelog,   # <- directly reused
            "query": query
        }

        response = await transform_chain.ainvoke(inputs)
        response_text = response.content
        
        cleaned = re.sub(r"^```json|```$", "", response_text, flags=re.IGNORECASE).strip()

        fixed = re.sub(r'f"({.*?})"', lambda m: '"' + m.group(1).replace('{', '{{').replace('}', '}}') + '"', cleaned)

        # Safely load the JSON
        try:
            parsed = json.loads(fixed)
        except json.JSONDecodeError:
            return JSONResponse(content={"error": "Failed to parse LLM response as JSON"}, status_code=400)

        if parsed["mode"] == "CHAT":
            # handle chat response
            return await handle_chat_response(session_id, session, query, parsed)
        elif parsed["mode"] == "CODE":
            # handle code response
            return await handle_code_response(session_id, session, query, parsed, df)
        elif parsed["mode"] == "CONTEXT":
            return await handle_context_change(session_id, parsed)
        else:
            # invalid LLM response
            return JSONResponse(content={"error": "Invalid LLM response"}, status_code=400)

    except Exception as e:
        traceback.print_exc()
        print(e)
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

async def handle_code_response(session_id, session, query, parsed, df):
    key_steps = parsed["key_steps"]
    code = parsed["executable_code"]
    response = parsed["response"]

    # Prepare commit ID and folder
    parent_commit = session.head

    # Step 1: Create commit document early
    commit_doc = await create_commit(
        session_id=session_id,
        parent_commit=parent_commit,
        query=query,
        mode="CODE",
        key_steps=key_steps,
        response=response,
        code=code,
        generated_files=[],
        success=True,
        error=None
    )
    commit_id = str(commit_doc.commit_id)

    # Step 2: Prepare commit directory (local)
    commit_dir = os.path.join("session_files", session_id, commit_id)
    os.makedirs(commit_dir, exist_ok=True)

    # Step 3: Execute the LLM code
    try:
        safe_globals = {
            "__builtins__": __builtins__,
            "pd": pd,
            "np": np,
            "sklearn": sklearn,
            "plt": plt,
            "sns": sns
        }
        local_vars = {
            "df": df,
            "commit_dir": commit_dir
        }

        exec(code, safe_globals, local_vars)
        df = local_vars["df"]

        # Step 4: Save transformed CSV
        csv_name = f"{commit_id}.csv"
        csv_path = os.path.join(commit_dir, csv_name)
        df.to_csv(csv_path, index=False)

        # Step 5: Upload all generated files in commit folder
        uploaded_files = await upload_commit_folder(
            bucket=BUCKET_NAME,
            local_folder_path=commit_dir,
            session_id=session_id,
            commit_id=commit_id
        )

        # Step 6: Update commit with file metadata
        generated_files = [
            GeneratedFile(**f) for f in uploaded_files
        ]
        await update_commit(commit_id, generated_files=generated_files)

        # Step 7: Update session head and last_csv_path
        await update_session(
            session_id=session_id,
            head=commit_id,
            last_csv_path=uploaded_files[0]["url"]  # CSV path
        )

        return JSONResponse(content={
            "success": True,
            "mode": "CODE",
            "response": response,
            "code": code,
            "key_steps": key_steps,
            # "df_head": df_head.to_dict(orient="records"),
            "generated_files": uploaded_files,
            "commit_data": {
                "commit_id": commit_id,
                "parent_id": parent_commit,
                "timestamp": commit_doc.timestamp
            }
        })

    except Exception as exec_err:
        traceback.print_exc()

        # Update commit as failed
        await update_commit(commit_id, success=False, error=str(exec_err))

        return JSONResponse(content={
            "success": False,
            "mode": "CODE",
            "response": response,
            "error": str(exec_err),
            "code": code,
            "key_steps": key_steps
        }, status_code=500)

async def handle_chat_response(session_id, session, query, parsed):
    try:
        llm_response_text = parsed["response"]

        commit_doc = await create_commit(
            session_id=session_id,
            parent_commit=str(session.head),
            query=query,
            mode="CHAT",
            key_steps=None,
            response=llm_response_text,
            code=None,
            generated_files=[],
            success=True,
            error=None
        )
        
        # 2. Update session HEAD
        await update_session(
            session_id=session_id,
            head=str(commit_doc.commit_id)
        )

        # 3. Return response
        return JSONResponse(content={
            "success": True,
            "mode": "CHAT",
            "response": llm_response_text,
            "code": None,
            "key_steps": None,
            "generated_files": [],
            "head": str(commit_doc.commit_id)
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "error": str(e)
        }, status_code=500)

async def handle_context_change(session_id: str, parsed):
    try:
        action = parsed.get("action")
        commit_id = parsed.get("target_commit_id")
        response = parsed["response"]

        if action == "checkout":
            # Move HEAD to a previous commit
            await update_session(session_id=session_id, head=commit_id)
            return JSONResponse(content={
                "success": True,
                "mode": "CONTEXT",
                "response": response,
                "action": "checkout",
                "message": f"HEAD moved to commit {commit_id}"
            })

        elif action == "branch":
            # Fork from a previous commit
            _, new_commit = await branch_from_commit(session_id, commit_id)
            return JSONResponse(content={
                "success": True,
                "mode": "CONTEXT",
                "response": response,
                "action": "branch",
                "new_head": str(new_commit.commit_id),
                "message": f"Branched from commit {commit_id}"
            })

        return JSONResponse(content={
            "success": False,
            "mode": "CONTEXT",
            "response": response,
            "error": "Invalid context action"
        }, status_code=400)

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "mode": "CONTEXT",
            "error": str(e)
        }, status_code=500)
