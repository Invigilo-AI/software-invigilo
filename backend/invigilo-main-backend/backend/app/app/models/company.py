from typing import TYPE_CHECKING

from sqlalchemy import Column, String

from app.db.base_class import Base

class Company(Base):
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    logo = Column(String, nullable=True)
