from typing import Dict, Optional, List, Union

from pydantic import Json
from app.models import ai_sequence
from app.schemas.ai_sequence import AI_Sequence

from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin


# Shared properties
class Cam_AI_MappingBase(CoreModel):
    name: str
    meta: Optional[Union[Dict, Json]] = None
    sequence_id: int
    camera_id: int


# Properties to receive on item creation
class Cam_AI_MappingCreate(Cam_AI_MappingBase):
    pass

# Properties to receive on item update


class Cam_AI_MappingUpdate(Cam_AI_MappingBase):
    name: Optional[str]
    sequence_id: Optional[int]
    camera_id: Optional[int]


# Properties shared by models stored in DB
class Cam_AI_MappingInDBBase(Cam_AI_MappingBase, IDModelMixin, DateTimeModelMixin):
    id: Optional[int]
    camera_id: Optional[int]
    sequence_id: Optional[int]


# Properties to return to client
class Cam_AI_Mapping(Cam_AI_MappingInDBBase):
    meta: Optional[Union[Dict, Json]]

class Cam_AI_MappingExtra(Cam_AI_Mapping):
    ai_sequence: List[AI_Sequence]


# Properties properties stored in DB
class Cam_AI_MappingInDB(Cam_AI_MappingInDBBase):
    pass
