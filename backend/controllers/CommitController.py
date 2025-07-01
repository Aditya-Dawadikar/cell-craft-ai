# controllers/CommitController.py

from models.commit import Commit, GeneratedFile
from models.DocumentMetaData import MetaData
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from beanie.operators import RegEx
from pymongo import ASCENDING, DESCENDING

# === Create a commit ===
async def create_commit(
    session_id: str,
    query: str,
    mode: str,
    timestamp: Optional[str] = None,
    response: Optional[str] = None,
    key_steps: Optional[str] = None,
    code: Optional[str] = None,
    parent_commit: Optional[str] = None,
    generated_files: Optional[List[GeneratedFile]] = None,
    success: bool = True,
    error: Optional[str] = None
) -> Commit:
    now = datetime.utcnow()
    meta_data = MetaData(created_at=now, last_updated_at=now)
    oid = ObjectId()

    commit = Commit(
        id=oid,
        commit_id=oid,
        session_id=ObjectId(session_id),
        query=query,
        mode=mode,
        timestamp=timestamp or now.isoformat(),
        response=response,
        key_steps=key_steps,
        code=code,
        parent_commit=parent_commit,
        generated_files=generated_files or [],
        success=success,
        error=error,
        meta_data=meta_data
    )
    return await commit.insert()


# === Get commit by ID ===
async def get_commit_by_id(commit_id: str) -> Optional[Commit]:
    try:
        oid = ObjectId(commit_id)
    except Exception:
        return None
    return await Commit.find_one(Commit.commit_id == oid)


# === Update a commit ===
async def update_commit(
    commit_id: str,
    query: Optional[str] = None,
    mode: Optional[str] = None,
    response: Optional[str] = None,
    key_steps: Optional[str] = None,
    code: Optional[str] = None,
    parent_commit: Optional[str] = None,
    generated_files: Optional[List[GeneratedFile]] = None,
    success: Optional[bool] = None,
    error: Optional[str] = None
) -> Optional[Commit]:
    commit = await get_commit_by_id(commit_id)
    if not commit:
        return None

    if query is not None:
        commit.query = query
    if mode is not None:
        commit.mode = mode
    if response is not None:
        commit.response = response
    if key_steps is not None:
        commit.key_steps = key_steps
    if code is not None:
        commit.code = code
    if parent_commit is not None:
        commit.parent_commit = parent_commit
    if generated_files is not None:
        commit.generated_files = generated_files
    if success is not None:
        commit.success = success
    if error is not None:
        commit.error = error

    commit.meta_data.last_updated_at = datetime.utcnow()
    await commit.save()
    return commit


# === Soft delete a commit ===
async def delete_commit(commit_id: str) -> bool:
    commit = await get_commit_by_id(commit_id)
    if not commit:
        return False
    
    commit.is_deleted = True
    commit.meta_data.deleted_at = datetime.utcnow()

    await commit.save()
    return True

# === Query commits with filters, pagination, and sorting ===
async def query_commits(
    commit_id: Optional[str] = None,
    session_id: Optional[str] = None,
    parent_commit: Optional[str] = None,
    mode: Optional[str] = None,
    success: Optional[bool] = None,
    query_search: Optional[str] = None,  # partial match on user query
    order_by: str = "timestamp",
    descending: bool = True,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False
) -> List[Commit]:
    query = {}

    if commit_id:
        query["commit_id"] = ObjectId(commit_id)

    if session_id:
        query["session_id"] = ObjectId(session_id)

    if parent_commit:
        query["parent_commit"] = parent_commit

    if mode:
        query["mode"] = mode

    if success is not None:
        query["success"] = success

    if query_search:
        query["query"] = RegEx(f".*{query_search}.*", options="i")

    query["is_deleted"] = False
    if include_deleted is True:
        del query["is_deleted"]

    ordering = [(order_by, DESCENDING if descending else ASCENDING)]

    return await Commit.find(query).sort(ordering).skip(skip).limit(limit).to_list()

async def get_commits_by_session_id(session_id: str,
                                    descending: bool=True)->List[Commit]:
    query = {}

    if session_id:
        query["session_id"] = ObjectId(session_id)

    ordering = [("timestamp", DESCENDING if descending else ASCENDING)]

    return await Commit.find(query).sort(ordering).to_list()
