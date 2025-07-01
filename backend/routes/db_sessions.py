from fastapi import APIRouter, HTTPException
from controllers.SessionController import *
from models.DocumentMetaData import MetaData
from typing import Optional
from models.requestModels.session import (SessionCreateRequest, SessionUpdateRequest)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/")
async def create_new_session(payload: SessionCreateRequest):
    return await create_session(
        session_name=payload.session_name,
        head=payload.head,
        last_csv_path=payload.last_csv_path,
        history_path=payload.history_path,
        session_dir=payload.session_dir
    )

@router.get("/{session_id}")
async def get_session(session_id: str):
    session = await get_session_by_session_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{session_id}")
async def update_session_metadata(session_id: str, payload: SessionUpdateRequest):
    session = await update_session(
        session_id,
        session_name=payload.session_name,
        head=payload.head,
        last_csv_path=payload.last_csv_path,
        history_path=payload.history_path,
        session_dir=payload.session_dir
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}") 
async def remove_session(session_id: str):
    if not await delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}

@router.get("/")
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
