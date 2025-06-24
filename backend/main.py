from fastapi import FastAPI, File, UploadFile, Form
import os
from uuid import uuid4
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import time
from google import genai
import json
import re
import sklearn
import dotenv

dotenv.load_dotenv()

def cleanup_old_files(folder, expiry_secs=3600):
    now = time.time()
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > expiry_secs:
            os.remove(fpath)

# Load your API key (from .env or hardcoded for testing)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "temp_sessions")
os.makedirs(UPLOAD_DIR, exist_ok=True)
session_cache = {}

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        session_id = str(uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{session_id}.csv")

        # Save file to disk directly
        with open(file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # Read 1MB at a time
                f.write(chunk)

        session_cache[session_id] = {
            "file_path": file_path,
            "transform_history": []
        }

        return {"session_id": session_id}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/transform_csv/")
async def transform_csv(session_id: str = Form(...), query: str = Form(...)):
    session = session_cache.get(session_id)
    if not session:
        return JSONResponse(content={"error": "Invalid session ID"}, status_code=400)

    file_path = session["file_path"]
    history = session["transform_history"]

    try:
        df = pd.read_csv(file_path)

        key_step_changelog = "\n".join(
            [f"- {item['key_steps']}" for item in history if item.get("success")]
        )

        # Build prompt for Gemini
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

        try:
            # Remove leading/trailing backticks and code block markers
            cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

            try:
                parsed = json.loads(cleaned)
            except Exception as parse_err:
                return JSONResponse(content={
                    "success": False,
                    "error": f"Failed to parse LLM output as JSON: {parse_err}",
                    "raw_output": response.text
                }, status_code=500)

            key_steps = parsed["key_steps"]
            code = parsed["executable_code"]
        except Exception as parse_err:
            return JSONResponse(content={
                "success": False,
                "error": f"Failed to parse LLM output as JSON: {parse_err}",
                "raw_output": response.text
            }, status_code=500)

        safe_globals = {"__builtins__": __builtins__,
                        "pd": pd,
                        "np": np,
                        "sklearn": sklearn}
        local_vars = {"df": df}

        try:
            exec(code, safe_globals, local_vars)
            df = local_vars["df"]
            df.to_csv(file_path, index=False)
            head_preview = df.head(5).to_dict(orient="records") if not df.empty else []

            history.append({
                "query": query,
                "key_steps": key_steps,
                "code": code,
                "success": True,
                "error": None
            })

            return JSONResponse(content={
                "success": True,
                "code": code,
                "key_steps": key_steps,
                "head": head_preview
            })

        except Exception as exec_err:
            history.append({
                "query": query,
                "key_steps": key_steps,
                "code": code,
                "success": False,
                "error": str(exec_err)
            })

            return JSONResponse(content={
                "success": False,
                "error": str(exec_err),
                "code": code,
                "key_steps": key_steps
            }, status_code=500)

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
