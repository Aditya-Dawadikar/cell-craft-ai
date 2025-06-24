import os
import traceback
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from uuid import uuid4
from store import session_cache
from session_management import (create_new_session,
                                apply_transform_and_checkpoint,
                                update_history,
                                branch_from_commit,
                                set_head)

import json
import re
import pandas as pd
import numpy as np
import sklearn

from google import genai

import dotenv
dotenv.load_dotenv()

# Load your API key (from .env or hardcoded for testing)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)


router = APIRouter()

@router.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        session_info = create_new_session(file_bytes)

        session_id = session_info["session_id"]
        session_cache[session_id] = session_info

        return {"session_id": session_id}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/transform_csv/")
async def transform_csv(session_id: str = Form(...), query: str = Form(...)):
    session = session_cache.get(session_id)
    if not session:
        return JSONResponse(content={"error": "Invalid session ID"}, status_code=400)

    try:
        df = pd.read_csv(session["last_csv_path"])

        # Build changelog from history
        try:
            with open(session["history_path"], "r") as f:
                history = json.load(f)
        except:
            history = []

        key_step_changelog = "\n".join(
            [f"- {item['key_steps']}" for item in history if item.get("success")]
        )

        df_preview = df.head(5).to_csv(index=False)
        prompt = f"""
                    You are a data cleaning assistant. The user gave you this preview:
                    {df_preview}

                    Previous steps:
                    {key_step_changelog}

                    User says: "{query}"

                    Respond in JSON.

                    If replying in text only:
                    {{
                    "mode": "CHAT",
                    "response": "<your message>"
                    }}

                    If applying transformation:
                    {{
                    "mode": "CODE",
                    "key_steps": "<summary>",
                    "executable_code": "<python pandas code>"
                    }}

                    You can also manage which CSV version you're working on.
                    If the user says "undo", "redo", or "start over from commit XYZ", respond in `CONTEXT` mode.

                    Use this format:

                    If changing HEAD:
                    {{
                    "mode": "CONTEXT",
                    "action": "checkout",
                    "target_commit_id": "<commit_id>"
                    }}

                    If creating a new branch from older commit:
                    {{
                    "mode": "CONTEXT",
                    "action": "branch",
                    "target_commit_id": "<commit_id>"
                    }}

                    Return ONLY valid JSON.
                """

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()
        parsed = json.loads(cleaned)

        if parsed["mode"] == "CHAT":
            # handle chat response
            return handle_chat_response(session_id, session, query, parsed)
        elif parsed["mode"] == "CODE":
            # handle code response
            return handle_code_response(session_id, session, query, parsed, df)
        elif parsed["mode"] == "CONTEXT":
            return handle_context_change(session_id, session, parsed)
        else:
            # invalid LLM response
            pass

    except Exception as e:
        traceback.print_exc()
        print(e)
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

def handle_code_response(session_id, session, query, parsed, df):
        key_steps = parsed["key_steps"]
        code = parsed["executable_code"]

        # Prepare execution
        safe_globals = {"__builtins__": __builtins__, "pd": pd, "np": np, "sklearn": sklearn}
        local_vars = {"df": df}

        try:
            exec(code, safe_globals, local_vars)
            df = local_vars["df"]

            step = {
                "query": query,
                "mode": "CODE",
                "response": None,
                "key_steps": key_steps,
                "code": code,
                "success": True,
                "error": None
            }

            # Save updated session data + checkpoint
            updated_session = apply_transform_and_checkpoint(session, df, step)
            session_cache[session_id] = updated_session

            head_preview = df.head(5).to_dict(orient="records") if not df.empty else []
            return JSONResponse(content={
                "success": True,
                "mode": "CODE",
                "response": None,
                "code": code,
                "key_steps": key_steps,
                "head": head_preview
            })

        except Exception as exec_err:
            traceback.print_exc()
            print(exec_err)
            
            step = {
                "query": query,
                "mode": "CODE",
                "response": None,
                "key_steps": key_steps,
                "code": code,
                "success": False,
                "error": str(exec_err)
            }
            _ = apply_transform_and_checkpoint(session, df, step)

            return JSONResponse(content={
                "success": False,
                "mode": "CODE",
                "response": None,
                "error": str(exec_err),
                "code": code,
                "key_steps": key_steps
            }, status_code=500)

def handle_chat_response(session_id, session, query, parsed):
    try:
        llm_response_text = parsed["response"]

        step = {
                    "query": query,
                    "mode": "CHAT",
                    "response": llm_response_text,
                    "key_steps": None,
                    "code": None,
                    "success": True,
                    "error": None
                }
        
        _ = update_history(session, step)

        return JSONResponse(content={
                    "success": True,
                    "mode": "CHAT",
                    "response": llm_response_text,
                    "code": None,
                    "key_steps": None,
                    "head": None
                })
    except Exception as e:
        traceback.print_exc()
        print(e)

def handle_context_change(session_id, session, parsed):
    try:
        action = parsed.get("action")
        commit_id = parsed.get("target_commit_id")

        if action == "checkout":
            updated_session = set_head(session, commit_id)
            session_cache[session_id] = updated_session
            return JSONResponse(content={
                "success": True,
                "mode": "CONTEXT",
                "action": "checkout",
                "message": f"HEAD moved to commit {commit_id}"
            })

        elif action == "branch":
            updated_session = branch_from_commit(session, commit_id)
            session_cache[session_id] = updated_session
            return JSONResponse(content={
                "success": True,
                "mode": "CONTEXT",
                "action": "branch",
                "new_head": updated_session["head"],
                "message": f"Branched from commit {commit_id}"
            })

        return JSONResponse(content={
            "success": False,
            "mode": "CONTEXT",
            "error": "Invalid context action"
        }, status_code=400)
    except Exception as e:
        traceback.print_exc()
        print(e)
