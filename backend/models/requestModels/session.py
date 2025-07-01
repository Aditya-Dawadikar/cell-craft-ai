from pydantic import BaseModel
from typing import Optional

class SessionCreateRequest(BaseModel):
    session_name: str
    head: Optional[str] = None
    last_csv_path: Optional[str] = None
    history_path: Optional[str] = None
    session_dir: Optional[str] = None

class SessionUpdateRequest(BaseModel):
    session_name: Optional[str] = None
    head: Optional[str] = None
    last_csv_path: Optional[str] = None
    history_path: Optional[str] = None
    session_dir: Optional[str] = None
