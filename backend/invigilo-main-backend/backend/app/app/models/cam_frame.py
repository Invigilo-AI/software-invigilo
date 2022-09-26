from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, Interval, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base_class import Base

if TYPE_CHECKING:
    from .camera import Camera  # noqa: F401

class Cam_Frame(Base):
    duration = Column(Interval, nullable=True, default=None)
    camera_id = Column(Integer, ForeignKey("camera.id"), index=True)
    meta = Column(JSONB, nullable=True, default=None)
    image = Column(String, nullable=True, default=None)
    video = Column(String, nullable=True, default=None)
