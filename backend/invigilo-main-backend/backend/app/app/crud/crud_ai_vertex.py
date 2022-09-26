from typing import List, Any, Tuple, Dict, Union

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app import crud
from app.models.ai_edge import AI_Edge
from app.models.ai_vertex import AI_Vertex
from app.schemas.ai_edge import AI_EdgeCreate
from app.schemas.ai_vertex import AI_VertexCreate, AI_VertexUpdate


class CRUD_AI_Vertex(CRUDBase[AI_Vertex, AI_VertexCreate, AI_VertexUpdate]):
    def create_multiple(self, db: Session, sequence_id: int, list_in: List[AI_VertexCreate]) -> Tuple[Dict[int, AI_Vertex], List[AI_Vertex]]:
        ai_vertexes = {}
        ai_vertexes_results = []

        for vertex in list_in:
            ai_vertex = super().create(db, obj_in=AI_VertexCreate(
                name=vertex.name,
                types=vertex.types,
                meta=vertex.meta,
                server_id=vertex.server_id,
                sequence_id=sequence_id,
            ))

            ai_vertexes[vertex.unique_id] = ai_vertex
            ai_vertexes_results.append(ai_vertex)

        return (ai_vertexes, ai_vertexes_results)

    def update_multiple(self, db: Session, sequence_id: int, list_in: List[Union[AI_VertexCreate, AI_VertexUpdate]], old_vertexes: List[AI_Vertex]) -> Tuple[List[AI_Vertex], List[AI_Edge]]:
        ai_vertexes = {}
        ai_vertexes_results = []
        ai_vertexes_ids = []
        exclude_fields = ['unique_id', 'source', 'destination']

        for vertex in list_in:
            db_obj = None
            if hasattr(vertex, 'id'):
                db_obj = super().get(db, vertex.id)
            if db_obj:
                obj_in = AI_VertexUpdate(
                    **jsonable_encoder(vertex, exclude_unset=True, exclude_none=True, exclude=exclude_fields)
                )
                ai_vertex = super().update(db, db_obj=db_obj, obj_in=obj_in)
            else:
                obj_in = AI_VertexCreate(
                    sequence_id=sequence_id,
                    **jsonable_encoder(vertex, exclude_unset=True, exclude_none=True, exclude=exclude_fields)
                )
                ai_vertex = super().create(db, obj_in=obj_in)

            ai_vertexes[vertex.unique_id] = ai_vertex
            ai_vertexes_ids.append(ai_vertex.id)
            ai_vertexes_results.append(ai_vertex)

        for vertex in old_vertexes:
            if not (vertex.id in ai_vertexes_ids):
                crud.ai_vertex.remove(db, id=vertex.id)

        return (ai_vertexes, ai_vertexes_results)


ai_vertex = CRUD_AI_Vertex(AI_Vertex)
