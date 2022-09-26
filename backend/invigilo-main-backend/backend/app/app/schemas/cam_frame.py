from typing import Dict, Optional, Union
from datetime import timedelta

from pydantic import Json, root_validator

from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin
from app.crud.crud_upload import upload

# Shared properties
class CameraFrameBase(CoreModel):
    camera_id: Optional[int]
    image: Optional[str]
    duration: Optional[timedelta] = None
    video: Optional[str] = None
    meta: Optional[Union[Dict, Json]] = None


# Properties to receive on Camera Frame creation
class CameraFrameCreate(CameraFrameBase):
    pass



# Properties to receive on Camera Frame creation
class CameraFrameUpdate(CameraFrameBase):
    pass


# Properties shared by models stored in DB
class CameraFrameInDBBase(CameraFrameBase, IDModelMixin, DateTimeModelMixin):
    id: Optional[int]
    pass


# Properties to return to client
class CameraFrame(CameraFrameInDBBase):
    image_url: str = None
    video_url: str = None

    @root_validator
    def signed_fields(cls, values):
        image_url = None
        image = values['image']
        if image:
            image_url = upload.sign_url(image)
        values['image_url'] = image_url

        video_url = None
        video = values['video']
        if video:
            video_url = upload.sign_url(video)
        values['video_url'] = video_url

        return values


# Properties properties stored in DB
class CameraFrameInDB(CameraFrameInDBBase):
    pass
