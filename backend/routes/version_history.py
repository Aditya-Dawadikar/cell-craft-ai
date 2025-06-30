import os
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, FileResponse
from store import session_cache
from session_management import list_commits
import posixpath
import json

router = APIRouter()

@router.get("/chat-history")
def get_chat_history(session_id: str, last_10: bool=True):
    session = session_cache.get(session_id, None)

    if session is None:
        return JSONResponse({
            "success": False,
            "msg": f"session_id {session_id} not found"
        })
    
    with open(session["history_path"], "r") as f:
        history = json.load(f)

        if last_10 is True:
            history = history[-10:]

        res = {
            "session_id": session_id,
            "chat_history": history
        }

        return JSONResponse(res)
    
    return JSONResponse({
        "success": False,
        "message": "Some error occured while loading conversation history."
    })


@router.get("/version-history")
def get_version_history(session_id:str):
    session_data = session_cache.get(session_id, None)

    if session_data is None:
        return JSONResponse({
            "success": False,
            "msg": f"session_id {session_id} not found"
        })

    version_history = list_commits(session_data)

    session = session_cache.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Invalid session ID"})

    for version in version_history:
        version["generated_files"] = get_commit_file_urls(session, version.get("commit_id"))

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


    try:
        static_urls = get_commit_file_urls(session, commit_id)
    except Exception as e:
        return JSONResponse(status_code=404, content=e)

    return JSONResponse(content={"commit_id": commit_id, "files": static_urls})

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

def get_commit_file_urls(session, commit_id):
    commit_folder = os.path.join(session["session_dir"], commit_id)
    if not os.path.exists(commit_folder):
        raise Exception({"error": "Commit folder not found"})

    static_base_path = os.getenv("SESSION_ROOT", "session_data")
    
    static_urls = []

    print(os.listdir(commit_folder))

    for fname in os.listdir(commit_folder):
        abs_path = os.path.join(commit_folder, fname)
        rel_path = os.path.relpath(abs_path, start=static_base_path)
        url_path = posixpath.join("/static", *rel_path.split(os.sep))  # normalize to forward slashes

        file_type = ""

        ext = url_path.split('.')[-1]
        if ext == 'csv':
            file_type = "dataframe"
        elif ext in ['png','jpg','jpeg']:
            file_type = 'chart'
        elif ext == 'md':
            file_type = "readme"
        else:
            file_type = ext

        file_name = url_path.split('/')[-1]

        url_object = {
            "type": file_type,
            "title": file_name,
            "url": url_path 
        }

        static_urls.append(url_object)
    
    return static_urls