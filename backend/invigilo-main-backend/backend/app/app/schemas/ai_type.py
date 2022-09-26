from typing import Optional

from pydantic import Field

from app.schemas.core import CoreModel, IDModelMixin, QueryModel, SoftDeleteModelMixin, DateTimeModelMixin


class AITypeFilters(QueryModel):
    index: Optional[int]
    severity: Optional[int]
    name: Optional[str]
    description: Optional[str]

# Shared properties


class AI_TypeBase(CoreModel):
    index: int
    severity: int = Field(50, ge=0, le=100)
    name: str
    description: Optional[str] = ''


# Properties to receive on AI_Type creation
class AI_TypeCreate(AI_TypeBase):
    pass


# Properties to receive on AI_Type update
class AI_TypeUpdate(AI_TypeBase):
    index: Optional[int]
    severity: Optional[int]
    name: Optional[str]
    description: Optional[str]


# Properties shared by models stored in DB
class AI_TypeInDBBase(AI_TypeBase, IDModelMixin, SoftDeleteModelMixin, DateTimeModelMixin):
    pass


# Properties to return to client
class AI_Type(AI_TypeInDBBase):
    pass

# Properties to return to client


class AI_TypeSimple(AI_TypeBase, IDModelMixin):
    pass


# Properties properties stored in DB
class AI_TypeInDB(AI_TypeInDBBase):
    pass
