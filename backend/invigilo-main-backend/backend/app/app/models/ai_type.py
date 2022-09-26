from sqlalchemy import Column, Integer, String

from app.db.base_class import Base

class AI_Type(Base):
    index = Column(Integer, unique=True, index=True)
    severity = Column(Integer, default=50, nullable=False)
    name = Column(String)
    description = Column(String, nullable=True)

