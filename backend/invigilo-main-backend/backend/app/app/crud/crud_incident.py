from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, List, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import Camera, Incident, Cam_Server
from app.crud.base import CRUDBase
from app.models.incident import Incident
from app.schemas import IncidentCreate, IncidentFilters, IncidentUpdate, IncidentFilters
from app.schemas.core import QueryParams


class CRUDIncident(CRUDBase[Incident, IncidentCreate, IncidentUpdate]):
    def create(
        self, db: Session, *, obj_in: IncidentCreate
    ) -> Incident:
        ai_mapping = crud.cam_ai_mapping.get(db=db, id=obj_in.ai_mapping_id)
        if ai_mapping:
            camera = crud.camera.get(db=db, id=ai_mapping.camera_id)
        if not ai_mapping or not camera:
            return None
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Incident(
            **obj_in_data,
            camera_id=camera.id,
            location=camera.location
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_camera(
        self, db: Session,
        camera_id: int,
        params: QueryParams = None
    ) -> List[Incident]:
        query = db.query(self.model).filter(Incident.camera_id == camera_id)

        query = self.query_limit(query, params)

        return query.all()

    def get_multi(
        self, db: Session,
        params: QueryParams = None,
        filters: IncidentFilters = None,
        company_id: int = None
    ) -> List[Incident]:
        query = db.query(Incident)

        if company_id:
            query = (
                query
                .outerjoin(Camera, Camera.id == Incident.camera_id)
                .outerjoin(Cam_Server, Cam_Server.id == Camera.cam_server_id)
                .filter(Cam_Server.company_id == company_id)
            )

        if filters.camera__cam_server_id:
            filters.camera_id = None
        if filters.acknowledged:
            filters.acknowledged = ('is_not_null',)
        if filters.created_at_from:
            filters.created_at = [('>=', filters.created_at_from)]
        if filters.created_at_to:
            filters.created_at.append(('<=', filters.created_at_to))

        query = self.query_filters(query, filters)
        query = self.query_order_by(query, params)
        query = self.query_limit(query, params)

        return query.all()

    def get_multi_updated_by_link(
        self, db: Session,
        params: QueryParams = None,
        cam_server_id: int = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[Any]:
        query = (db.query(self.model)
                 .filter(self.model.deleted == False)
                 .join(Camera, Camera.id == Incident.camera_id, isouter=True)
                 .join(Cam_Server, Cam_Server.id == Camera.cam_server_id, isouter=True)
                 .filter(Cam_Server.id == cam_server_id)
                 )
        # only incidents created in NOTIFICATION_TIME_WINDOW
        query = query.filter(self.model.created_at >= (
            datetime.utcnow() - timedelta(seconds=settings.NOTIFICATION_TIME_WINDOW)))

        if updated_before:
            query = query.filter(self.model.updated_at <= updated_before)
        if updated_after:
            query = query.filter(self.model.updated_at > updated_after)

        if count:
            return query.count()

        query = self.query_limit(query, params)

        return query.all()

    def mark_flag(self, db: Session, id: int, flag: str, value: Union[bool, datetime], by_user: str) -> Incident:
        incident = self.get(db, id)
        meta = None
        if incident.meta:
            meta = deepcopy(incident.meta)
        if by_user:
            if not meta:
                meta = {}
            meta['mark_by'] = by_user
        return super().update(db=db, db_obj=incident, obj_in={flag: value, 'meta': meta})

    def mark_acknowledged(self, db: Session, id: int, by_user: str) -> Incident:
        return self.mark_flag(db, id, 'acknowledged', datetime.utcnow(), by_user)

    def mark_inaccurate(self, db: Session, id: int, by_user: str) -> Incident:
        return self.mark_flag(db, id, 'inaccurate', True, by_user)


incident = CRUDIncident(Incident)
