import os
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, FileResponse
from store import session_cache
from session_management import list_commits


router = APIRouter()

@router.get("/version-history")
def get_version_history(session_id:str):
    session_data = session_cache.get(session_id, None)

    if session_data is None:
        return JSONResponse({
            "success": False,
            "msg": f"session_id {session_id} not found"
        })

    version_history = list_commits(session_data)

    res = {
        "session_id": session_id,
        "head": session_data.get("head", None),
        "commits": version_history
    }

    return JSONResponse(res)

@router.get("/list_commit_files")
def list_commit_files(session_id: str = Query(...), commit_id: str = Query(...)):
    session = session_cache.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Invalid session ID"})

    commit_folder = os.path.join(session["session_dir"], commit_id)
    if not os.path.exists(commit_folder):
        return JSONResponse(status_code=404, content={"error": "Commit folder not found"})

    files = os.listdir(commit_folder)
    return JSONResponse(content={"commit_id": commit_id, "files": files})

@router.get("/download_commit_file")
def download_commit_file(
    session_id: str = Query(...),
    commit_id: str = Query(...),
    filename: str = Query(...)
):
    session = session_cache.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Invalid session ID"})

    file_path = os.path.join(session["session_dir"], commit_id, filename)

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found in commit folder"})

    return FileResponse(path=file_path, filename=filename)
