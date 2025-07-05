from beanie import Document
from pydantic import BaseModel, Field, ConfigDict

from typing import Optional, List, Literal
from models.DocumentMetaData import MetaData
from bson import ObjectId

class Checkpoint(Document):
    checkpoint_id: ObjectId = Field(default_factory=ObjectId)
    session_id: ObjectId = Field(..., alias="session_id")
    timestamp: str
    parent_checkpoint: Optional[str] = None
    summary: str
    commit_ids: List[str]
    meta_data: MetaData

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "checkpoints"
