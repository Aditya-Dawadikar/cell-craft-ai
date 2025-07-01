import os
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from store import session_cache
from session_management_2 import (create_new_session)
from controllers.SessionController import (query_sessions)
from typing import Optional

router = APIRouter()

@router.get("/session-list")
async def search_sessions(session_id: Optional[str] = None,
                          session_name: Optional[str] = None,
                          search: Optional[str] = None,
                          order_by: str = "session_name",
                          descending: bool = False,
                          skip: int = 0,
                          limit: int = 20,
                          include_deleted:bool=False):
    return await query_sessions(session_id,
                                session_name,
                                search,
                                order_by,
                                descending,
                                skip,
                                limit,
                                include_deleted)

@router.post("/create-session/")
async def create_session(file: UploadFile = File(...),
                         session_name: str = Form(default="Untitled Session")):
    try:
        file_bytes = await file.read()
        return await create_new_session(file_bytes, session_name)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
