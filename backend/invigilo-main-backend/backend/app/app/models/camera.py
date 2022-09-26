from typing import TYPE_CHECKING

from sqlalchemy import event, inspect, orm
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base_class import Base
from app.models.cam_frame import Cam_Frame
from app import models

if TYPE_CHECKING:
    from .cam_server import Cam_Server  # noqa: F401
    from .cam_frame import Cam_Frame  # noqa: F401

class Camera(Base):
    name = Column(String, index=True)
    location = Column(String)
    description = Column(String)
    connection = Column(String)
    is_active = Column(Boolean(), default=False)
    is_live = Column(Boolean(), default=False)
    cam_server_id = Column(Integer, ForeignKey("cam_server.id"), index=True)
    cam_server = relationship("Cam_Server", backref=backref("cameras", cascade="all, delete-orphan"))
    frames = relationship("Cam_Frame", viewonly=True, lazy='dynamic')
    incidents = relationship("Incident", viewonly=True, lazy='dynamic')

    @hybrid_property
    def last_frame(self):
        query = self.frames.order_by(models.Cam_Frame.created_at.desc())
        frame = query.first()
        if frame:
            return frame

        return None

    @hybrid_property
    def last_incident(self):
        query = self.incidents.order_by(models.Incident.created_at.desc())
        incident = query.first()
        if incident:
            return incident
        return None

# skip to change `updated_at` when `is_live` is updated
@event.listens_for(Camera, 'before_update')
def receive_before_update(mapper, connection, target):
    flag_changed, _, _ = inspect(target).attrs.is_live.history
    if flag_changed:
        orm.attributes.flag_modified(target, 'updated_at')