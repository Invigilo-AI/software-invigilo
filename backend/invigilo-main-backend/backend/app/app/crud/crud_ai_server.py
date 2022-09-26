from datetime import datetime
from typing import Any, List
from warnings import filters

from sqlalchemy.orm import Session

from app.models import AI_Vertex, AI_Sequence, Cam_AI_Mapping, Camera, Cam_Server
from app.crud.base import CRUDBase
from app.models.ai_server import AI_Server
from app.schemas.ai_server import AI_ServerCreate, AI_ServerUpdate, AIServerFilters
from app.schemas.core import QueryParams


class CRUD_AI_Server(CRUDBase[AI_Server, AI_ServerCreate, AI_ServerUpdate]):
    # TODO: create/update `company_id` is valid company
    def get_multi_by_company(
        self, db: Session, *, 
        company_id: int, 
        params: QueryParams = None,
        filters: AIServerFilters = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[AI_Server]:
        query = db.query(self.model)
        filters.company_id = company_id
        query = self.query_filters(query, filters)
        query = self.query_order_by(query, params)
        
        if updated_before:
            query = query.filter(self.model.updated_at <= updated_before)
        if updated_after:
            query = query.filter(self.model.updated_at > updated_after)
        if count:
            return query.count()
        return (
            query
            .offset(params.skip)
            .limit(params.limit)
            .all()
        )

    def get_multi_by_link(
        self, db: Session,
        params: QueryParams = None,
        cam_server_id: int = None,
        company_id: int = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[Any]:
        query = (db.query(self.model)
                 .filter(self.model.deleted == False)
                 .join(AI_Vertex, AI_Vertex.server_id == self.model.id, isouter=True)
                 .join(AI_Sequence, AI_Sequence.id == AI_Vertex.sequence_id and AI_Sequence.company_id == company_id, isouter=True)
                 .join(Cam_AI_Mapping, Cam_AI_Mapping.sequence_id == AI_Sequence.id, isouter=True)
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

    def is_active(self, server: AI_Server) -> bool:
        return server.is_active


ai_server = CRUD_AI_Server(AI_Server)
