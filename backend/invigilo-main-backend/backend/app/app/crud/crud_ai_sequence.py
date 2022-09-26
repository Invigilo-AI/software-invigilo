from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from app.models.cam_ai_mapping import Cam_AI_Mapping
from app.models.cam_server import Cam_Server
from app.models.camera import Camera

from app.crud.base import CRUDBase
from app import crud
from app.models.ai_sequence import AI_Sequence
from app.schemas.ai_sequence import AI_SequenceCreate, AI_SequenceExtra, AI_SequenceInDB, AI_SequenceOut, AI_SequenceUpdate
from app.schemas.core import QueryParams


class CRUD_AI_Sequence(CRUDBase[AI_Sequence, AI_SequenceCreate, AI_SequenceUpdate]):
    def create(self, db: Session, obj_in: AI_SequenceCreate) -> AI_SequenceOut:
        vertexes = obj_in.vertexes

        del(obj_in.vertexes)

        ai_sequence = super().create(db, obj_in=obj_in)
        ai_vertexes, ai_vertexes_results = crud.ai_vertex.create_multiple(
            db, ai_sequence.id, vertexes)
        ai_edges, ai_edges_results = crud.ai_edge.create_multiple(
            db, ai_sequence.id, vertexes, ai_vertexes)

        return AI_SequenceOut(
            id=ai_sequence.id,
            name=ai_sequence.name,
            description=ai_sequence.description,
            company_id=ai_sequence.company_id,
            vertexes=ai_vertexes_results,
            edges=ai_edges_results
        )

    def update(self, db: Session, *, db_obj: AI_SequenceInDB, obj_in: AI_SequenceUpdate) -> AI_SequenceOut:
        vertexes = obj_in.vertexes
        old_vertexes = db_obj.vertexes
        old_edges = db_obj.edges
        del(obj_in.vertexes)

        ai_sequence = super().update(db, db_obj=db_obj, obj_in=obj_in)
        ai_vertexes, ai_vertexes_results = crud.ai_vertex.update_multiple(
            db, ai_sequence.id, vertexes, old_vertexes)
        ai_edges, ai_edges_results = crud.ai_edge.update_multiple(db, ai_sequence.id, vertexes, ai_vertexes, old_edges)

        return AI_SequenceOut(
            id=ai_sequence.id,
            name=ai_sequence.name,
            description=ai_sequence.description,
            company_id=ai_sequence.company_id,
            vertexes=ai_vertexes_results,
            edges=ai_edges_results
        )

    def get_multi_by_link(
        self, db: Session,
        cam_server_id: int = None,
        params: QueryParams = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[AI_SequenceOut]:
        query = (db.query(self.model)
                 .filter(self.model.deleted == False)
                 .join(Cam_AI_Mapping, AI_Sequence.id == Cam_AI_Mapping.sequence_id, isouter=True)
                 .join(Camera, Camera.id == Cam_AI_Mapping.camera_id, isouter=True)
                 .join(Cam_Server, Cam_Server.id == Camera.cam_server_id, isouter=True)
                 .filter(Cam_Server.id == cam_server_id)
                 )
        if updated_before:
            query = query.filter(self.model.updated_at <= updated_before)
        if updated_after:
            query = query.filter(self.model.updated_at > updated_after)
        if count:
            return query.count()

        query = self.query_limit(query, params)
        
        return query.all()

    def remove(self, db: Session, *, id: int) -> AI_SequenceExtra:
        sequence = self.get(db, id=id)
        for edge in sequence.edges:
            crud.ai_edge.remove(db, id=edge.id)
        for vertex in sequence.vertexes:
            crud.ai_vertex.remove(db, id=vertex.id)
        return super().remove(db, id=id)


ai_sequence = CRUD_AI_Sequence(AI_Sequence)
