from typing import Optional, List, Union
from app.schemas.ai_edge import AI_Edge
from app.schemas.ai_vertex import AI_Vertex, AI_VertexCreate, AI_VertexUpdate
from app.schemas.company import CompanyInfo

from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel


class AISequenceFilters(QueryModel):
    name: Optional[str]
    description: Optional[str]
    company__name: Optional[str]
    company_id: Optional[int]

# Shared properties


class AI_SequenceBase(CoreModel):
    name: str = None
    description: Optional[str] = ''
    company_id: int = None


# Properties to receive on item creation
class AI_SequenceCreate(AI_SequenceBase):
    name: str
    company_id: int
    vertexes: List[AI_VertexCreate] = []

# Properties to receive on item update


class AI_SequenceUpdate(AI_SequenceBase):
    vertexes: List[Union[AI_VertexCreate, AI_VertexUpdate]] = []
    pass


# Properties shared by models stored in DB
class AI_SequenceInDBBase(AI_SequenceBase, IDModelMixin, DateTimeModelMixin):
    pass


# Properties to return to client
class AI_Sequence(AI_SequenceInDBBase):
    pass

# Properties to receive on item create


class AI_SequenceOut(AI_Sequence):
    vertexes: Optional[List[AI_Vertex]]
    edges: Optional[List[AI_Edge]]


class AI_SequenceExtra(AI_SequenceOut):
    company: Optional[CompanyInfo]


# Properties properties stored in DB
class AI_SequenceInDB(AI_SequenceInDBBase):
    pass
