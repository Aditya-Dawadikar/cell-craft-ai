# controllers/SessionController.py

from models.session import Session
from typing import Optional, List
from bson import ObjectId
from models.DocumentMetaData import MetaData
from datetime import datetime
from beanie.operators import RegEx
from pymongo import ASCENDING, DESCENDING


# === Create a new session ===
async def create_session(
    session_name: str,
    head: Optional[str] = None,
    last_csv_path: Optional[str] = None,
    history_path: Optional[str] = None,
    session_dir: Optional[str] = None
) -> Session:
    now = datetime.utcnow()
    meta_data = MetaData(created_at=now, last_updated_at=now)
    oid = ObjectId()

    session = Session(
        id=oid,  # MongoDB _id
        session_id=oid,  # Explicit field in model
        session_name=session_name,
        head=head,
        last_csv_path=last_csv_path,
        history_path=history_path,
        session_dir=session_dir,
        meta_data=meta_data
    )
    return await session.insert()


# === Get a session by session_id (custom ObjectId field) ===
async def get_session_by_session_id(session_id: str) -> Optional[Session]:
    try:
        oid = ObjectId(session_id)
        return await Session.find_one(Session.session_id == oid)
    except Exception:
        return None

# === Update a session ===
async def update_session(
    session_id: str,
    session_name: Optional[str]=None,
    head: Optional[str] = None,
    last_csv_path: Optional[str] = None,
    history_path: Optional[str] = None,
    session_dir: Optional[str] = None
) -> Optional[Session]:
    session = await get_session_by_session_id(session_id)
    if not session:
        return None

    if session_name is not None:
        session.session_name = session_name
    if head is not None:
        session.head = head
    if last_csv_path is not None:
        session.last_csv_path = last_csv_path
    if history_path is not None:
        session.history_path = history_path
    if session_dir is not None:
        session.session_dir = session_dir

    session.meta_data.last_updated_at = datetime.utcnow()
    await session.save()
    return session


# === Soft delete a session ===
async def delete_session(session_id: str) -> bool:
    session = await get_session_by_session_id(session_id)
    if not session:
        return False
    
    session.is_deleted = True
    session.meta_data.deleted_at = datetime.utcnow()

    await session.save()
    return True


# === Query sessions ===
async def query_sessions(
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    search: Optional[str] = None,
    order_by: str = "session_name",
    descending: bool = False,
    skip: int = 0,
    limit: int = 20,
    include_deleted: bool = False
) -> List[Session]:
    query = {}

    if session_id:
        try:
            query["session_id"] = ObjectId(session_id)
        except Exception:
            return []

    if session_name:
        query["session_name"] = session_name

    if search:
        query["session_name"] = RegEx(f".*{search}.*", options="i")


    query["is_deleted"] = False
    if include_deleted is True:
        del query["is_deleted"]

    ordering = [(order_by, DESCENDING if descending else ASCENDING)]

    return await Session.find(query).sort(ordering).skip(skip).limit(limit).to_list()
