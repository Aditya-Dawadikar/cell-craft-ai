import os
from fastapi import APIRouter, Query, File, UploadFile, Form
from fastapi.responses import JSONResponse
from store import session_cache
from session_management import (create_new_session)

router = APIRouter()

@router.get("/session-list")
def get_session_list():
    sessions = []
    for key,value in session_cache.items():
        sessions.append({
            "session_id": key,
            "session_name": value.get("session_name", None) 
        })

    return JSONResponse({
        "success": True,
        "sessions": sessions
    })

@router.post("/create-session/")
async def create_session(file: UploadFile = File(...),
                         session_name: str = Form(default="Untitled Session")):
    try:
        file_bytes = await file.read()
        session_info = create_new_session(file_bytes, session_name)

        session_id = session_info["session_id"]
        session_cache[session_id] = session_info

        return {
                    "session_id": session_id,
                    "session_name": session_info["session_name"]
                }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
