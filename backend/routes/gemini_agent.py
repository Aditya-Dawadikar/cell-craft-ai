import os
import traceback
from fastapi import APIRouter, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from uuid import uuid4
from store import session_cache
from session_management import (create_new_session,
                                apply_transform_and_checkpoint,
                                update_history,
                                branch_from_commit,
                                set_head,
                                generate_commit_id)
import ast
import json
import re
import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from routes.version_history import get_commit_file_urls

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

                    You operate in an isolated Python environment. You are allowed to:
                    - Use ONLY the following libraries: pandas, numpy, matplotlib (as plt), seaborn (as sns)
                    - Answer only questions about the data provided in the CSV
                    - Politely decline unrelated questions and suggest asking questions about the dataset

                    When visualizing data (using matplotlib/seaborn), DO NOT show or display the plot. Instead, save the chart to a file using `plt.savefig("<filename>")`.
                    When describing data (using pandas), DO NOT print or display the data. Instead, save the response as markdown or txt file.
                    
                    You must respond using one of the following JSON formats:

                    If replying in plain text:
                    {{
                    "mode": "CHAT",
                    "response": "<your message>"
                    }}

                    If applying transformation:
                    {{
                    "mode": "CODE",
                    "key_steps": "<summary>",
                    "executable_code": "<python pandas code>",
                    "response": "<acknowledgement of transforms>"
                    }}

                    You can also manage which CSV version you're working on.
                    If the user says "undo", "redo", or "start over from commit XYZ", respond in CONTEXT mode.

                    If changing HEAD:
                    {{
                    "mode": "CONTEXT",
                    "action": "checkout",
                    "target_commit_id": "<commit_id>",
                    "response": "<acknowledgement of context change>"
                    }}

                    If creating a new branch from an older commit:
                    {{
                    "mode": "CONTEXT",
                    "action": "branch",
                    "target_commit_id": "<commit_id>",
                    "response": "<acknowledgement of context change>"
                    }}

                    IMPORTANT:
                    - All output must be a single valid JSON object.
                    - Never include code outside the "executable_code" field.
                    - Do not attempt to write files to directories other than the current working directory.

                    When saving files like charts or summaries, use the variable commit_dir as the output folder. Example:
                    plt.savefig(f"{{commit_dir}}/myplot.png")
                    or
                    with open(f"{{commit_dir}}/summary.md", "w") as f: f.write(summary)

                    You are provided the DataFrame as a variable named `df`. 
                    - Do NOT use `pd.read_csv()` or try to load 'df.csv'.
                    - The DataFrame is already available in memory.
                    - Any cleaned or transformed result should overwrite the existing `df` variable.

                    Return ONLY valid JSON.
                """


        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        response_text = response.candidates[0].content.parts[0].text
        cleaned = re.sub(r"^```json|```$", "", response_text, flags=re.IGNORECASE).strip()

        fixed = re.sub(r'f"({.*?})"', lambda m: '"' + m.group(1).replace('{', '{{').replace('}', '}}') + '"', cleaned)

        # Safely load the JSON
        parsed = json.loads(fixed)

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

@router.get("/download_csv")
def download_csv(session_id: str = Query(...), commit_id: str = Query(...)):
    session = session_cache.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Invalid session ID"})

    session_dir = session.get("session_dir")
    if not session_dir:
        return JSONResponse(status_code=500, content={"error": "Session directory missing"})

    file_name = f"{commit_id}.csv"
    file_path = os.path.join(session_dir, file_name)

    if not os.path.isfile(file_path):
        return JSONResponse(status_code=404, content={"error": f"CSV file for commit {commit_id} not found"})

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="text/csv"
    )

def handle_code_response(session_id, session, query, parsed, df):
    key_steps = parsed["key_steps"]
    code = parsed["executable_code"]
    response = parsed["response"]

    # Prepare commit ID and folder
    parent_commit = session.get("head")
    commit_content = json.dumps(parsed, sort_keys=True)
    commit_id = generate_commit_id(commit_content)

    commit_folder = os.path.join(session["session_dir"], commit_id)
    os.makedirs(commit_folder, exist_ok=True)

    # Track files before exec
    existing_files = set(os.listdir(commit_folder))

    # Globals and locals for exec
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
        "commit_dir": commit_folder  # LLM will use this for saving files
    }

    try:
        exec(code, safe_globals, local_vars)

        new_files = get_commit_file_urls(session, commit_id)

        df = local_vars["df"]

        step = {
            "query": query,
            "mode": "CODE",
            "response": response,
            "key_steps": key_steps,
            "code": code,
            "generated_files": new_files,
            "success": True,
            "error": None
        }

        updated_session, commit_data = apply_transform_and_checkpoint(session, df, step, commit_id)
        session_cache[session_id] = updated_session

        df_head = df.head(5).copy()
        df_head = df_head.applymap(lambda x: str(x) if isinstance(x, (pd.Timestamp, datetime.datetime)) else x)

        # head_preview = df.head(5).to_dict(orient="records") if not df.empty else []

        return JSONResponse(content={
            "success": True,
            "mode": "CODE",
            "response": response,
            "code": code,
            "key_steps": key_steps,
            "df_head": df_head.to_dict(orient="records"),
            "generated_files": new_files,
            "commit_data": {
                "commit_id": commit_data["commit_id"],
                "parent_id": commit_data["parent_commit"],
                "timestamp": commit_data["timestamp"]
            }
        })

    except Exception as exec_err:
        traceback.print_exc()

        step = {
            "query": query,
            "mode": "CODE",
            "response": response,
            "key_steps": key_steps,
            "code": code,
            "success": False,
            "error": str(exec_err)
        }

        _, _ = apply_transform_and_checkpoint(session, df, step)

        return JSONResponse(content={
            "success": False,
            "mode": "CODE",
            "response": response,
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
                    "generated_files": [],
                    "head": None
                })
    except Exception as e:
        traceback.print_exc()
        print(e)

def handle_context_change(session_id, session, parsed):
    try:
        action = parsed.get("action")
        commit_id = parsed.get("target_commit_id")
        response = parsed["response"]

        if action == "checkout":
            updated_session = set_head(session, commit_id)
            session_cache[session_id] = updated_session
            return JSONResponse(content={
                "success": True,
                "mode": "CONTEXT",
                "response": response,
                "action": "checkout",
                "message": f"HEAD moved to commit {commit_id}"
            })

        elif action == "branch":
            updated_session = branch_from_commit(session, commit_id)
            session_cache[session_id] = updated_session
            return JSONResponse(content={
                "success": True,
                "mode": "CONTEXT",
                "response": response,
                "action": "branch",
                "new_head": updated_session["head"],
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
        print(e)
