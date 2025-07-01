from beanie import Document
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId
from datetime import datetime
from models.DocumentMetaData import MetaData

class Session(Document):
    session_id: ObjectId = Field(default_factory=ObjectId)  # ← Explicit ID field

    session_name: str
    head: str
    last_csv_path: str
    history_path: str
    session_dir: str
    meta_data: MetaData

    is_deleted: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "sessions"
