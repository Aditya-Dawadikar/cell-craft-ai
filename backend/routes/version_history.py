from fastapi import APIRouter
from fastapi.responses import JSONResponse
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
