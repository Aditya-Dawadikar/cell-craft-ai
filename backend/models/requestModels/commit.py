from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class GeneratedFile(BaseModel):
    type: str
    title: str
    url: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CommitCreateRequest(BaseModel):
    session_id: str
    query: str
    mode: str
    timestamp: Optional[str] = None
    response: Optional[str] = None
    key_steps: Optional[str] = None
    code: Optional[str] = None
    parent_commit: Optional[str] = None
    generated_files: Optional[List[GeneratedFile]] = None
    success: bool = True
    error: Optional[str] = None

class CommitUpdateRequest(BaseModel):
    query: Optional[str] = None
    mode: Optional[str] = None
    response: Optional[str] = None
    key_steps: Optional[str] = None
    code: Optional[str] = None
    parent_commit: Optional[str] = None
    generated_files: Optional[List[GeneratedFile]] = None
    success: Optional[bool] = None
    error: Optional[str] = None
