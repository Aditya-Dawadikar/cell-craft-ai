from beanie import Document
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from models.DocumentMetaData import MetaData
from models.requestModels.commit import GeneratedFile
from bson import ObjectId


class Commit(Document):
    commit_id: ObjectId = Field(default_factory=ObjectId)
    session_id: ObjectId
    parent_commit: Optional[str] = None
    timestamp: str

    query: str
    mode: Literal["CODE","CHAT","CONTEXT"]
    response: Optional[str] = None
    key_steps: Optional[str] = None
    code: Optional[str] = None
    generated_files: List[GeneratedFile] = []

    success: bool
    error: Optional[str] = None

    is_deleted: bool = False

    meta_data: MetaData

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "commits"
