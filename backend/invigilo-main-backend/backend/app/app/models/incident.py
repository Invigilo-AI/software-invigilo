from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy_utils import ScalarListType

from app.db.base_class import Base

if TYPE_CHECKING:
    from .cam_ai_mapping import Cam_AI_Mapping  # noqa: F401
    from .camera import Camera  # noqa: F401


class Incident(Base):
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), index=True, default=uuid4)
    type = Column(ScalarListType(), index=True)
    ai_mapping_id = Column(Integer, ForeignKey("cam_ai_mapping.id"), index=True)
    ai_mapping = relationship("Cam_AI_Mapping", backref="incidents")
    camera_id = Column(Integer, ForeignKey("camera.id"), index=True)
    camera = relationship("Camera", viewonly=True)
    location = Column(String)
    acknowledged = Column(DateTime, nullable=True)
    inaccurate = Column(Boolean, default=False)

    # meta data
    meta = Column(JSONB, nullable=True)
    extra = Column(JSONB, nullable=True)
    count = Column(Integer)
    frame = Column(String, nullable=True)
    video = Column(String, nullable=True)
    people = Column(Integer, default=0)
    objects = Column(Integer, default=0)
