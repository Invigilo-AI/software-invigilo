from typing import Dict, Optional, List, Union

from pydantic import Json
from app.models.ai_vertex import AI_VertexTypes

from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin


# Shared properties
class AI_VertexBase(CoreModel):
    name: str = ''
    types: List[int] = None
    meta: Optional[Union[Dict, Json]] = None
    server_id: int = None
    sequence_id: int = None
    


# Properties to receive on item creation
class AI_VertexCreate(AI_VertexBase):
    id: Optional[int]
    name: str
    unique_id: Optional[str]
    server_id: int
    types: List[int]
    source: Optional[List[str]] = None
    destination: Optional[List[str]] = None

# Properties to receive on item update
class AI_VertexUpdate(AI_VertexBase):
    id: Optional[int]
    unique_id: Optional[str]
    types: Optional[List[int]]
    source: Optional[List[str]] = None
    destination: Optional[List[str]] = None


# Properties shared by models stored in DB
class AI_VertexInDBBase(AI_VertexBase, IDModelMixin, DateTimeModelMixin):
    id: Optional[int]
    name: str
    types: List[int]
    server_id: int


# Properties to return to client
class AI_Vertex(AI_VertexInDBBase):
    server_id: Optional[int] = None
    types: Optional[List[int]] = []


# Properties properties stored in DB
class AI_VertexInDB(AI_VertexInDBBase):
    pass
