from typing import Optional

from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin


# Shared properties
class AI_EdgeBase(CoreModel):
    sequence_id: int
    source_id: Optional[int] = None
    destination_id: Optional[int] = None


# Properties to receive on item creation
class AI_EdgeCreate(AI_EdgeBase):
    pass

# Properties to receive on item update


class AI_EdgeUpdate(AI_EdgeBase):
    pass


# Properties shared by models stored in DB
class AI_EdgeInDBBase(AI_EdgeBase, IDModelMixin, DateTimeModelMixin):
    id: Optional[int]
    source_id: Optional[int]
    destination_id: Optional[int]
    sequence_id: Optional[int]
    pass


# Properties to return to client
class AI_Edge(AI_EdgeInDBBase):
    pass


# Properties properties stored in DB
class AI_EdgeInDB(AI_EdgeInDBBase):
    pass
