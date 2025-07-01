from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MetaData(BaseModel):
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
