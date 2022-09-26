from typing import Optional
from pydantic import BaseModel

class Upload(BaseModel):
    object_id: str
    object_url: Optional[str]

class TemporaryUpload(Upload):
    pass