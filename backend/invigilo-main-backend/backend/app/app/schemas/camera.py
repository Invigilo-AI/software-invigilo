from typing import List, Optional, Union

from pydantic import BaseModel
from app.schemas.cam_ai_mapping import Cam_AI_Mapping, Cam_AI_MappingCreate, Cam_AI_MappingUpdate
from app.schemas.cam_frame import CameraFrame
from app.schemas.cam_server import CamServerInfo
from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel


class CameraInfo(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CameraFilters(QueryModel):
    cam_server_id: Optional[int]
    cam_server__name: Optional[str]
    name: Optional[str]
    location: Optional[str]
    description: Optional[str]


# Shared properties
class CameraBase(CoreModel):
    name: str = None
    location: Optional[str] = ''
    description: Optional[str] = ''
    connection: Optional[str] = ''
    is_active: Optional[bool] = False
    cam_server_id: int = None


# Properties to receive on Camera creation
class CameraCreate(CameraBase):
    name: str
    cam_server_id: int
    ai_mapping: List[Cam_AI_MappingCreate] = []


# Properties to receive on Camera update
class CameraUpdate(CameraBase):
    name: Optional[str]
    cam_server_id: Optional[int]
    ai_mapping: List[Union[Cam_AI_MappingCreate, Cam_AI_MappingUpdate]] = []


class CameraStatus(CoreModel):
    is_live: bool = False


# Properties shared by models stored in DB
class CameraInDBBase(CameraBase, IDModelMixin, DateTimeModelMixin):
    name: str
    cam_server_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Camera(CameraInDBBase):
    is_live: Optional[bool] = None

# fmt: off
from app.schemas.incident import Incident
# fmt: on


class CameraStats(CoreModel):
    activity: Optional[float] = 0
    objects: Optional[int] = 0
    people: Optional[int] = 0


class CameraExtra(Camera):
    cam_server: CamServerInfo
    # frames: List[CameraFrame]
    last_frame: Optional[CameraFrame]
    last_incident: Optional[Incident]
    stats: Optional[CameraStats] = None


class CameraExtended(CameraExtra):
    ai_mapping: List[Cam_AI_Mapping]


# Properties properties stored in DB
class CameraInDB(CameraInDBBase):
    pass
