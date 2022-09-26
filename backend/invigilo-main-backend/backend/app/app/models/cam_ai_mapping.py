from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSON

from app.db.base_class import Base

if TYPE_CHECKING:
    from .ai_sequence import AI_Sequence  # noqa: F401
    from .camera import Camera  # noqa: F401


class Cam_AI_Mapping(Base):
    name = Column(String, nullable=True)
    meta = Column(JSON, nullable=True)
    sequence_id = Column(Integer, ForeignKey("ai_sequence.id"), index=True)
    sequence = relationship("AI_Sequence", backref=backref(
        "cam_mapping", cascade="all, delete-orphan"))
    camera_id = Column(Integer, ForeignKey("camera.id"), index=True)
    camera = relationship("Camera", backref=backref(
        "ai_mapping",
        primaryjoin="and_(Cam_AI_Mapping.camera_id==Camera.id, Cam_AI_Mapping.deleted!=True)",
        cascade="all, delete-orphan"
    ))
