from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship, validates, backref
from sqlalchemy_utils import ScalarListType

from app.db.base_class import Base
from app.models.ai_vertex import AI_VertexTypes


if TYPE_CHECKING:
    from .company import Company  # noqa: F401

class AI_ServerType(IntEnum):
    PROCESS = 1
    NETWORK = 2
    REMOTE = 3


class AI_Server(Base):
    name = Column(String, index=True)
    location = Column(String, index=True)
    description = Column(String)
    connection = Column(String, index=True)
    vertex_types = Column(ScalarListType(), nullable=True)
    # type = Column(Enum(AI_ServerType), default=AI_ServerType.PROCESS)
    is_active = Column(Boolean(), default=False)
    is_live = Column(Boolean(), default=False)
    company_id = Column(Integer, ForeignKey("company.id"), index=True, nullable=True)
    company = relationship("Company", backref=backref("ai_servers", cascade="all, delete-orphan"))

    # @validates('vertex_types')
    # def validate_types(self, key, types):
    #     # TODO check server for available detector type work with Errors
    #     valid_types = [item.value for item in AI_VertexTypes]
    #     if not all(type in valid_types for type in types):
    #         # raise ValueError("Invalid type")
    #         pass
    #     return list(set([type for type in types if type in valid_types]))