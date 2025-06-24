import os

from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from uuid import uuid4
from store import session_cache
from session_management import (create_new_session,
                                apply_transform_and_checkpoint)

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

            Respond in JSON with two fields:
            - "key_steps": a 1-line summary of what the transformation does
            - "executable_code": Python Pandas code to perform the transformation

            Return ONLY valid JSON. Do not include explanation or any other text.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()
        parsed = json.loads(cleaned)

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
                "code": code,
                "key_steps": key_steps,
                "head": head_preview
            })

        except Exception as exec_err:
            step = {
                "query": query,
                "key_steps": key_steps,
                "code": code,
                "success": False,
                "error": str(exec_err)
            }
            _ = apply_transform_and_checkpoint(session, df, step)

            return JSONResponse(content={
                "success": False,
                "error": str(exec_err),
                "code": code,
                "key_steps": key_steps
            }, status_code=500)

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
