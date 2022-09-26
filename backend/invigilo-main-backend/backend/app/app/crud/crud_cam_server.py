from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cam_server import Cam_Server
from app.schemas.cam_server import Cam_ServerCreate, Cam_ServerUpdate, CamServerFilters
from app.schemas.core import QueryParams


class CRUD_Cam_Server(CRUDBase[Cam_Server, Cam_ServerCreate, Cam_ServerUpdate]):
    def get_multi_by_company(
        self, db: Session,
        company_id: int,
        params: QueryParams = None,
        filters: CamServerFilters = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[Cam_Server]:
        query = db.query(self.model)

        if filters:
            filters.company_id = company_id
        else:
            query = query.filter(self.model.company_id == company_id)

        query = self.query_filters(query, filters)
        query = self.query_order_by(query, params)
        if updated_before:
            query = query.filter(self.model.updated_at <= updated_before)
        if updated_after:
            query = query.filter(self.model.updated_at > updated_after)
        if count:
            return query.count()

        query = self.query_limit(query, params)

        return (
            query
            .all()
        )

    def get_multi_by_link(
        self, db: Session,
        link_id: int,
        params: QueryParams = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[Cam_Server]:
        query = (db.query(self.model)
                 .filter(self.model.deleted == False)
                 .filter(self.model.company_id == link_id)
                 )
        if updated_before:
            query = query.filter(self.model.updated_at <= updated_before)
        if updated_after:
            query = query.filter(self.model.updated_at > updated_after)
        if count:
            return query.count()

        query = self.query_limit(query, params)

        return query.all()

    def get_by_access_token(
        self, db: Session, *, access_token: str
    ) -> Cam_Server:
        return (
            db.query(self.model)
            .filter(Cam_Server.access_token == access_token)
            .first()
        )

    def is_active(self, server: Cam_Server) -> bool:
        return server.is_active


cam_server = CRUD_Cam_Server(Cam_Server)
