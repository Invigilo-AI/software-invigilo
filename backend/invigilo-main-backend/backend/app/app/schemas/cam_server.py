from typing import Dict, Optional, Union

from pydantic import BaseModel, Json, root_validator, validator

from app.schemas.company import CompanyInfo
from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel
from app.crud.crud_upload import upload

class CamServerFilters(QueryModel):
    name: Optional[str]
    description: Optional[str]
    location: Optional[str]
    company_id: Optional[int]
    company__name: Optional[str]


class CamServerInfo(BaseModel):
    id: int
    name: str
    location: str

    class Config:
        orm_mode = True
        validate_assignment = True

    @validator("location", pre=True, always=True)
    def set_location(cls, location):
        return location or "Without location"

# Shared properties


class Cam_ServerBase(CoreModel):
    name: str = None
    location: Optional[str] = ''
    description: Optional[str] = ''
    connection: Optional[str] = ''
    is_active: Optional[bool] = False
    company_id: Optional[int] = None
    access_token: Optional[str] = None
    meta: Optional[Union[Dict, Json]] = None


# Properties to receive on Server creation
class Cam_ServerCreate(Cam_ServerBase):
    name: str
    company_id: int


# Properties to receive on Server update
class Cam_ServerUpdate(Cam_ServerBase):
    name: Optional[str]
    company_id: Optional[int]


# Properties shared by models stored in DB
class Cam_ServerInDBBase(Cam_ServerBase, IDModelMixin, DateTimeModelMixin):
    name: str
    company_id: int = None
    access_token: Optional[str]

    class Config:
        orm_mode = True

# Properties to return to client


class Cam_Server(Cam_ServerInDBBase):
    pass


class Cam_ServerExtra(Cam_Server):
    company: Optional[CompanyInfo]

    @root_validator
    def signed_fields(cls, values):
        meta = values['meta']
        if meta and 'levels' in meta:
            for level in meta['levels']:
                if 'image' in level and 'file_name' in level['image']:
                    level['image_url'] = upload.sign_url(level['image']['file_name'])

        return values

# Properties properties stored in DB


class Cam_ServerInDB(Cam_ServerInDBBase):
    pass
