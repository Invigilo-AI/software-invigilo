from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base_class import Base

if TYPE_CHECKING:
    from .company import Company  # noqa: F401


class Cam_Server(Base):
    name = Column(String, index=True)
    location = Column(String, index=True)
    description = Column(String)
    connection = Column(String, index=True)
    access_token = Column(String, index=True, unique=True, nullable=True)
    is_active = Column(Boolean(), default=False)
    is_live = Column(Boolean(), default=False)
    company_id = Column(Integer, ForeignKey("company.id"), index=True, nullable=True)
    company = relationship("Company", backref="cam_servers")
    # `notification_bot_type`: [{title: 'Chat title', 'chat_id': int, [disabled: bool]}]
    meta = Column(JSONB, nullable=True)
