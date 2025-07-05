import os
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from controllers.SessionController import (get_session_by_session_id)
from controllers.CommitController import (query_commits, get_commit_by_id)
from storage.storage_utils import get_file_list, generate_presigned_get_url
from cache.signed_url_cache import get_signed_url

router = APIRouter()

@router.get("/chat-history")
async def get_chat_history(session_id: str, last_10: bool=True):
    session = await get_session_by_session_id(session_id)

    if session is None:
        return JSONResponse({
            "success": False,
            "msg": f"session_id {session_id} not found"
        })
    
    history = await query_commits(session_id=session_id, descending=False)
    
    commit_dicts = [commit.model_dump(mode="json") for commit in history]

    res = {
            "session_id": session_id,
            "chat_history": commit_dicts
        }

    return JSONResponse(res)



@router.get("/version-history")
async def get_version_history(session_id:str):
    session = await get_session_by_session_id(session_id)

    if session is None:
        return JSONResponse({
            "success": False,
            "msg": f"session_id {session_id} not found"
        })

    history = await query_commits(session_id=session_id, descending=False)

    commit_dicts = [commit.model_dump(mode="json") for commit in history]

    res = {
        "session_id": session_id,
        "head": session.head,
        "commits": commit_dicts
    }

    return JSONResponse(res)

@router.get("/list_commit_files")
async def list_commit_files(session_id: str = Query(...), commit_id: str = Query(...)):
    try:
        # 1. Confirm session exists
        session = await get_session_by_session_id(session_id)
        commit = await get_commit_by_id(commit_id)
        if not session:
            return JSONResponse(status_code=404, content={"error": "Invalid session ID"})

        # 2. List all files under commit in S3
        s3_keys = await get_file_list(bucket=os.getenv("S3_BUCKET_NAME"), session_id=session_id, commit_id=commit_id)

        if not s3_keys:
            return JSONResponse(status_code=404, content={"error": "No files found in this commit"})

        # 3. Generate signed GET URLs
        files = []

        for file in commit.generated_files:
            files.append({
                "title": file.title,
                "type": file.type,
                "url": await get_signed_url(bucket=os.getenv("S3_BUCKET_NAME"), s3_file_path=file.url)
            })
        
        return JSONResponse(content={
            "commit_id": commit_id,
            "files": files
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
