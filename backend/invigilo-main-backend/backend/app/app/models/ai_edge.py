from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .ai_sequence import AI_Sequence  # noqa: F401
    from .ai_vertex import AI_Vertex  # noqa: F401


class AI_Edge(Base):
    sequence_id = Column(Integer, ForeignKey("ai_sequence.id"), index=True)
    source_id = Column(Integer, ForeignKey("ai_vertex.id"), index=True, nullable=True)
    destination_id = Column(Integer, ForeignKey(
        "ai_vertex.id"), index=True, nullable=True)

    # source = relationship(
    #     "AI_Vertex",
    #     # "AI_Vertex", backref=backref("sources", cascade="all, delete-orphan")
    #     primaryjoin="AI_Edge.source_id==AI_Vertex.id",
    #     lazy="joined"
    # )
    # destination = relationship(
    #     "AI_Vertex",
    #     # "AI_Vertex", backref=backref("destinations", cascade="all, delete-orphan")
    #     primaryjoin="AI_Edge.source_id==AI_Vertex.id",
    #     lazy="joined"
    # )
    sequence = relationship("AI_Sequence", backref=backref(
        "edges", 
        primaryjoin="and_(AI_Sequence.id==AI_Edge.sequence_id, AI_Edge.deleted!=True)",
        cascade="all, delete-orphan"
        ))
