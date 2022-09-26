from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .company import Company  # noqa: F401


class AI_Sequence(Base):
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id"), index=True)
    company = relationship("Company", backref=backref("ai_sequences", cascade="all, delete-orphan"))
