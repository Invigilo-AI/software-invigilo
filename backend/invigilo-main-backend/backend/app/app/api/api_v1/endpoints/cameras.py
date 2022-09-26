from datetime import datetime, timedelta
from typing import Any, List

from fastapi import Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_

from app.core.config import settings
from app import crud, models, schemas
from app.api import deps
from app.api.api_v1.endpoints.utils import event_source_response
from app.schemas import QueryParams
from app.schemas.cam_ai_mapping import Cam_AI_MappingCreate, Cam_AI_MappingUpdate

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[schemas.Camera])
def read_cameras(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: schemas.CameraFilters = Depends(schemas.CameraFilters),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve cameras.

    When `superuser` receive all, or
    Only records by own company
    """
    if crud.user.is_superuser(current_user):
        cameras = crud.camera.get_multi(db, params=params, filters=filters)
    else:
        cameras = crud.camera.get_multi_by_company(
            db, current_user.company_id, params=params, filters=filters
        )

    return cameras


@router.get("/extra", response_model=List[schemas.CameraExtra])
def read_cameras_extra(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: schemas.CameraFilters = Depends(schemas.CameraFilters),
    with_incident_only: bool = False,
    current_user: models.User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    """
    Retrieve cameras with statistics

    Only records by own company
    """
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id

    if not as_company_id:
        raise HTTPException(status_code=404, detail="Cameras for company not found")
    else:
        filter_dict = {
            **filters.dict(),
            'cam_server__company_id': as_company_id
        }
        cameras_query = crud.camera.get_multi_count(
            db, filters=filter_dict, as_query=True)

        # TODO: use last_frame meta for statistics
        INCIDENT_FROM = datetime.utcnow() - timedelta(seconds=settings.CAMERA_ACTIVITY_INTERVAL)
        incidents_count = (
            cameras_query
            .join(models.Incident).with_entities(models.Incident.id)
            .filter(models.Incident.created_at > INCIDENT_FROM)
        ).count()

        if with_incident_only:
            cameras_query = cameras_query.join(models.Incident, and_(
                models.Incident.deleted == False, models.Incident.camera_id == models.Camera.id))
        cameras = crud.camera.query_limit(cameras_query, params).all()
        if cameras:
            result = []
            for camera in cameras:
                camera_extra = schemas.CameraExtra(
                    **jsonable_encoder(camera),
                    cam_server=camera.cam_server,
                    last_frame=camera.last_frame,
                    last_incident=camera.last_incident,
                )
                camera_extra.stats = schemas.CameraStats()
                if camera.last_incident:
                    camera_extra.stats.objects = camera.last_incident.objects
                    camera_extra.stats.people = camera.last_incident.people

                    if incidents_count:
                        camera_incidents_count = camera.incidents.with_entities(models.Incident.id).filter(
                            models.Incident.created_at > INCIDENT_FROM
                        ).count()
                        camera_extra.stats.activity = (
                            camera_incidents_count / incidents_count) * 100
                result.append(camera_extra)
            return result

    return cameras


@router.post("/", response_model=schemas.Camera)
def create_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_in: schemas.CameraCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new camera.
    """
    server = None
    if camera_in.cam_server_id:
        filters = {}
        if not crud.user.is_superuser(current_user):
            filters['company_id'] = current_user.company_id
        server = crud.cam_server.get(db=db, id=camera_in.cam_server_id, filters=filters)
    if not server:
        raise HTTPException(status_code=404, detail="Camera Server not found")
    camera = crud.camera.create(db=db, obj_in=camera_in)
    return camera


@router.put("/{id}", response_model=schemas.Camera)
def update_camera(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    camera_in: schemas.CameraUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a camera.
    """
    camera = crud.camera.get(db=db, id=id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not crud.user.is_superuser(current_user) and current_user.company_id != camera.cam_server.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if camera_in.cam_server_id:
        filters = {}
        if not crud.user.is_superuser(current_user):
            filters['company_id'] = camera.cam_server.company_id
        server = crud.cam_server.get(db=db, id=camera_in.cam_server_id, filters=filters)
        if not server:
            raise HTTPException(status_code=404, detail="Camera Server not found")
    if hasattr(camera_in, 'ai_mapping'):
        try:
            for (i, map) in enumerate(camera_in.ai_mapping):
                if hasattr(map, 'id'):
                    Cam_AI_MappingUpdate(
                        **jsonable_encoder(map, exclude_unset=True, exclude_defaults=True),
                        camera_id=camera.id
                    )
                else:
                    Cam_AI_MappingCreate(
                        **jsonable_encoder(map, exclude_unset=True, exclude_defaults=True),
                        camera_id=camera.id
                    )
        except ValueError as e:
            detail = e.errors()
            for error in detail:
                error['loc'] = ('body', 'ai_mapping', i) + error['loc']
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": detail}),
            )   
    camera = crud.camera.update(db=db, db_obj=camera, obj_in=camera_in)
    return camera


@router.put("/{id:int}/status", response_model=schemas.Camera, tags=['bridge'])
def update_camera_status(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    status_in: schemas.CameraStatus,
    current_server: models.Cam_Server = Depends(deps.get_current_active_server),
) -> Any:
    camera = crud.camera.get(db=db, id=id)
    if not camera or camera.cam_server_id != current_server.id:
        raise HTTPException(status_code=404, detail="Camera not found")
    return crud.camera.update_status(db, db_obj=camera, obj_in=status_in)


@router.post("/{id:int}/frame", response_model=schemas.CameraFrame, tags=['bridge'])
def create_camera_frame(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    frame_in: schemas.CameraFrameCreate,
    current_server: models.Cam_Server = Depends(deps.get_current_active_server),
) -> Any:
    camera = crud.camera.get(db=db, id=id)
    if not camera or camera.cam_server_id != current_server.id:
        raise HTTPException(status_code=404, detail="Camera not found")
    frame_in.camera_id = camera.id
    return crud.cam_frame.create(db, obj_in=frame_in)


@router.get("/{id:int}/extra", response_model=schemas.CameraExtra)
@router.get("/{id:int}/extended", response_model=schemas.CameraExtended)
@router.get("/{id:int}", response_model=schemas.Camera)
def read_camera(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    # current_user: models.User = Depends(deps.get_current_active_user),
    current_user_or_server=Depends(deps.get_user_or_server)
) -> Any:
    """
    Get camera by ID.
    """
    current_user, current_server = current_user_or_server

    camera = crud.camera.get(db=db, id=id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not crud.user.is_superuser(current_user) and (camera.cam_server.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return camera


@router.delete("/{id}", response_model=schemas.Camera)
def delete_camera(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a camera.
    """
    camera = crud.camera.get(db=db, id=id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    if not crud.user.is_superuser(current_user) and (camera.cam_server.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    camera = crud.camera.remove(db=db, id=id)
    return camera


@router.get("/link", response_model=List[schemas.Camera], tags=['bridge'])
def read_cameras_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.User = Depends(deps.get_current_server),
):
    """
    Get cameras by server through Access-Token.
    """
    return crud.camera.get_multi_by_cam_server(db, cam_server_id=current_server.id)


@router.get("/stream/link", response_model=Any, tags=['bridge'])
def stream_cameras_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.User = Depends(deps.get_current_server),
    request: Request
):
    """
    Stream cameras by server through Access-Token.
    """
    return event_source_response(
        db=db, request=request,
        pull_fn=crud.camera.get_multi_by_cam_server,
        show_fields=['name', 'connection', 'is_active', 'location', 'company_id'],
        cam_server_id=current_server.id
    )
