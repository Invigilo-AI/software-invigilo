from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import crud
from app.crud.base import CRUDBase
from app.models.camera import Camera
from app.schemas.cam_ai_mapping import Cam_AI_MappingCreate, Cam_AI_MappingUpdate
from app.schemas.camera import CameraCreate, CameraExtended, CameraFilters, CameraStatus, CameraUpdate
from app.schemas import QueryParams


class CRUDCamera(CRUDBase[Camera, CameraCreate, CameraUpdate]):
    def get_multi_by_cam_server(
        self, db: Session,
        cam_server_id: int, 
        params: QueryParams = None,
        updated_before: datetime = None,
        updated_after: datetime = None,
        count: bool = False
    ) -> List[Camera]:
        query = (db.query(self.model)
                 .filter(self.model.deleted == False)
                 .filter(self.model.cam_server_id == cam_server_id)
                 )
        if updated_before:
            query = query.filter(self.model.updated_at <= updated_before)
        if updated_after:
            query = query.filter(self.model.updated_at > updated_after)
        if count:
            return query.count()

        query = self.query_limit(query, params)

        return query.all()

    def get_multi_by_company(
        self, db: Session,
        company_id: int,
        params: QueryParams = None,
        filters: CameraFilters = None
    ) -> List[Camera]:
        return super().get_multi(db, params=params, filters={**filters.dict(), 'cam_server__company_id': company_id})

    def create(self, db: Session, *, obj_in: CameraCreate) -> Camera:
        ai_mapping = obj_in.ai_mapping
        del(obj_in.ai_mapping)

        camera = super().create(db, obj_in=obj_in)

        if camera:
            for map in ai_mapping:
                crud.cam_ai_mapping.create(db, obj_in=Cam_AI_MappingCreate(
                    **jsonable_encoder(map, exclude_unset=True, exclude_defaults=True),
                    camera_id=camera.id
                ))

        return camera

    def update_status(self, db: Session, *, db_obj: Camera, obj_in: CameraStatus) -> Camera:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Camera, obj_in: CameraUpdate) -> CameraExtended:
        map_exclude_fields = ['camera_id']
        ai_mapping = obj_in.ai_mapping
        old_ai_mapping = db_obj.ai_mapping
        del(obj_in.ai_mapping)

        camera = super().update(db, db_obj=db_obj, obj_in=obj_in)

        mapping_ids = []
        for map in ai_mapping:
            map_obj = None
            if hasattr(map, 'id'):
                map_obj = crud.cam_ai_mapping.get(db, map.id)
            if map_obj:
                ai_map = crud.cam_ai_mapping.update(db, db_obj=map_obj, obj_in=Cam_AI_MappingUpdate(
                    **jsonable_encoder(map, exclude_unset=True, exclude_defaults=True, exclude=map_exclude_fields),
                    camera_id=camera.id
                ))
            else:
                ai_map = crud.cam_ai_mapping.create(db, obj_in=Cam_AI_MappingCreate(
                    **jsonable_encoder(map, exclude_unset=True, exclude_defaults=True, exclude=map_exclude_fields),
                    camera_id=camera.id
                ))
            mapping_ids.append(ai_map.id)

        for map in old_ai_mapping:
            if not (map.id in mapping_ids):
                crud.cam_ai_mapping.remove(db, id=map.id)

        return camera

    def remove(self, db: Session, *, id: int) -> CameraExtended:
        camera = self.get(db, id=id)
        for mapping in camera.ai_mapping:
            crud.cam_ai_mapping.remove(db, id=mapping.id)
        return super().remove(db, id=id)


camera = CRUDCamera(Camera)
