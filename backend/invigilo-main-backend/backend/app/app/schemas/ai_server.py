from typing import List, Optional

from pydantic import BaseModel
from app.models.ai_server import AI_ServerType
from app.models.ai_vertex import AI_VertexTypes

from app.schemas.company import CompanyInfo
from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel


class AIServerFilters(QueryModel):
    name: Optional[str]
    location: Optional[str]
    description: Optional[str]
    company_id: Optional[int]
    company__name: Optional[str]


class AIServerInfo(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Shared properties


class AI_ServerBase(CoreModel):
    name: str = None
    location: Optional[str] = ''
    description: Optional[str] = ''
    connection: Optional[str] = ''
    vertex_types: Optional[List[int]] = None
    # type: Optional[AI_ServerType] = None
    is_active: Optional[bool] = False
    company_id: Optional[int] = None


# Properties to receive on AI_Server creation
class AI_ServerCreate(AI_ServerBase):
    name: str


# Properties to receive on AI_Server update
class AI_ServerUpdate(AI_ServerBase):
    name: Optional[str]
    company_id: Optional[int]


# Properties shared by models stored in DB
class AI_ServerInDBBase(AI_ServerBase, IDModelMixin, DateTimeModelMixin):
    name: str
    company_id: Optional[int]

    class Config:
        orm_mode = True

# Properties to return to client


class AI_Server(AI_ServerInDBBase):
    pass
# Properties to return to client with extra


class AI_ServerExtra(AI_Server):
    company: Optional[CompanyInfo]


# Properties properties stored in DB
class AI_ServerInDB(AI_ServerInDBBase):
    pass
