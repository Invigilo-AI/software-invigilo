from datetime import datetime
from typing import Dict, Optional, List, Union

from pydantic import UUID4, BaseModel, Json, root_validator

from app.schemas.camera import CameraInfo
from app.crud.crud_upload import upload
from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel


class DateTimeInterval(BaseModel):
    start: Optional[datetime]
    end: Optional[datetime]

class IncidentFilters(QueryModel):
    uuid: Optional[str]
    type: Optional[List[int]]
    camera__name: Optional[str]
    camera_id: Optional[int]
    camera__cam_server_id: Optional[int]
    location: Optional[str]
    acknowledged: Optional[bool]
    inaccurate: Optional[bool]
    created_at: Optional[Union[DateTimeInterval, datetime]]
    created_at_from: Optional[datetime]
    created_at_to: Optional[datetime]

# Shared properties
class IncidentBase(CoreModel):
    type: Optional[List[int]]
    meta: Optional[Union[Dict, Json]]
    extra: Optional[Union[Dict, Json]]
    count: Optional[int]
    frame: Optional[str]
    video: Optional[str]
    people: Optional[int]
    objects: Optional[int]


# Properties to receive on Incident creation
class IncidentCreate(IncidentBase):
    uuid: Optional[UUID4]
    type: List[int]
    ai_mapping_id: int

# Properties to receive on Incident update


class IncidentUpdate(IncidentBase):
    pass

# Properties shared by models stored in DB


class IncidentInDBBase(IncidentBase, IDModelMixin, DateTimeModelMixin):
    uuid: UUID4
    type: List[int]
    ai_mapping_id: int
    camera_id: Optional[int]
    acknowledged: Optional[datetime] = None
    inaccurate: Optional[bool] = False

    location: Optional[str] = None
    frame: Optional[str] = None
    video: Optional[str] = None
    count: Optional[int] = 0
    people: Optional[int] = 0
    objects: Optional[int] = 0

    class Config:
        orm_mode = True


# Properties to return to client
class Incident(IncidentInDBBase):
    uuid: UUID4
    frame_url: str = None
    video_url: str = None

    @root_validator
    def signed_fields(cls, values):
        frame_url = None
        frame = values['frame']
        if frame:
            frame_url = upload.sign_url(frame)
        values['frame_url'] = frame_url

        video_url = None
        video = values['video']
        if video:
            video_url = upload.sign_url(video)
        values['video_url'] = video_url

        return values


class IncidentExtra(Incident):
    camera: CameraInfo


# Properties properties stored in DB
class IncidentInDB(IncidentInDBBase):
    pass
