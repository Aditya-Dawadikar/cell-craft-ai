# routers/commits.py

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from models.commit import Commit, GeneratedFile
from models.DocumentMetaData import MetaData
from controllers.CommitController import *
from models.requestModels.commit import (CommitCreateRequest, CommitUpdateRequest)

router = APIRouter(prefix="/commits", tags=["commits"])

@router.post("/", response_model=Commit)
async def create_commit_api(payload: CommitCreateRequest):
    return await create_commit(
        session_id=payload.session_id,
        query=payload.query,
        mode=payload.mode,
        timestamp=payload.timestamp,
        response=payload.response,
        key_steps=payload.key_steps,
        code=payload.code,
        parent_commit=payload.parent_commit,
        generated_files=payload.generated_files,
        success=payload.success,
        error=payload.error
    )


@router.get("/{commit_id}", response_model=Commit)
async def get_commit_api(commit_id: str):
    commit = await get_commit_by_id(commit_id)
    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")
    return commit


@router.put("/{commit_id}", response_model=Commit)
async def update_commit_api(commit_id: str, payload: CommitUpdateRequest):
    commit = await update_commit(
        commit_id=commit_id,
        query=payload.query,
        mode=payload.mode,
        response=payload.response,
        key_steps=payload.key_steps,
        code=payload.code,
        parent_commit=payload.parent_commit,
        generated_files=payload.generated_files,
        success=payload.success,
        error=payload.error
    )
    if not commit:
        raise HTTPException(status_code=404, detail="Commit not found")
    return commit


@router.delete("/{commit_id}")
async def delete_commit_api(commit_id: str):
    deleted = await delete_commit(commit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Commit not found")
    return {"deleted": True}


@router.get("/", response_model=List[Commit])
async def query_commits_api(
    commit_id: Optional[str] = None,
    session_id: Optional[str] = None,
    parent_commit: Optional[str] = None,
    mode: Optional[str] = None,
    success: Optional[bool] = None,
    query_search: Optional[str] = None,
    order_by: str = "timestamp",
    descending: bool = True,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
):
    return await query_commits(
        commit_id=commit_id,
        session_id=session_id,
        parent_commit=parent_commit,
        mode=mode,
        success=success,
        query_search=query_search,
        order_by=order_by,
        descending=descending,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted
    )
