from datetime import datetime
from sqlalchemy.orm import Session
from typing import Any, List
from app.models.ai_sequence import AI_Sequence
from app.models.cam_server import Cam_Server
from app.models.camera import Camera
from app.schemas.cam_ai_mapping import Cam_AI_MappingCreate

from app.crud.base import CRUDBase
from app.models.cam_ai_mapping import Cam_AI_Mapping
from app.schemas.cam_ai_mapping import Cam_AI_MappingCreate, Cam_AI_MappingUpdate
from app.schemas.core import QueryParams


class CRUD_Cam_AI_Mapping(CRUDBase[Cam_AI_Mapping, Cam_AI_MappingCreate, Cam_AI_MappingUpdate]):
    def get_multi(
        self, db: Session, 
        params: QueryParams = None,
        company_id: dict = None
    ) -> List[Cam_AI_Mapping]:
        query = (db
                 .query(self.model)
                 .filter_by(deleted = False)
                 )
        if company_id:
            query = query.outerjoin(AI_Sequence, AI_Sequence.id == self.model.sequence_id and AI_Sequence.company_id == company_id)
        query = self.query_limit(query, params)
        return query.all()

    def get_multi_by_link(
        self, db: Session, 
        params: QueryParams = None,
        cam_server_id: int = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[Any]:
        query = (db.query(self.model)
                 .filter(self.model.deleted == False)
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


cam_ai_mapping = CRUD_Cam_AI_Mapping(Cam_AI_Mapping)
