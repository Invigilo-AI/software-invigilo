from enum import IntEnum
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates, backref
from sqlalchemy_utils import ScalarListType
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base_class import Base

if TYPE_CHECKING:
    from .ai_sequence import AI_Sequence  # noqa: F401
    from .cam_server import Cam_Server  # noqa: F401

# TODO the class isn't used anymore, find a way to check with the model `AI_Type`
class AI_VertexTypes(IntEnum):
    SOCIAL_DISTANCING = 1   # Social distancing
    MASK_ABSENCE = 2        # Absence of mask
    PPE_COMPLIANCE = 3      # PPE non-compliance
    PROXIMITY_MACHINE = 4   # Proximity to dangerous machines
    INTRUSION = 5           # Intrusion alerts
    DETECTION_6 = 6         # TODO TBD

    def __str__(self):
        return str(self.value)


class AI_Vertex(Base):
    name = Column(String)
    description = Column(String, nullable=True)
    types = Column(ScalarListType())
    meta = Column(JSONB, nullable=True)
    server_id = Column(Integer, ForeignKey("ai_server.id"), index=True)
    server = relationship("AI_Server", backref=backref(
        "ai_vertexes", cascade="all, delete-orphan"))
    sequence_id = Column(Integer, ForeignKey("ai_sequence.id"), index=True)
    sequence = relationship("AI_Sequence", backref=backref(
        "vertexes",
        primaryjoin="and_(AI_Sequence.id==AI_Vertex.sequence_id, AI_Vertex.deleted!=True)",
        cascade="all, delete-orphan"
    ))

    # @validates('types')
    # def validate_types(self, key, types):
    #     # TODO check server for available detector type work with Errors
    #     valid_types = [item.value for item in AI_VertexTypes]
    #     if not all(type in valid_types for type in types):
    #         # raise ValueError("Invalid type")
    #         pass
    #     return list(set([type for type in types if type in valid_types]))
