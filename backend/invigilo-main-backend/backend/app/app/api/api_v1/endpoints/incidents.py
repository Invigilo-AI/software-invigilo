from datetime import datetime, timedelta
from typing import Any, List, Optional
from xmlrpc.client import boolean

from fastapi import Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app import crud
from app.api.api_v1.endpoints.utils import event_source_response
from app.models import User, Cam_Server
from app.schemas import Incident, IncidentExtra, IncidentCreate, IncidentUpdate, IncidentFilters
from app.core.config import settings
from app.api import deps
from app.core.notification_bot import notification_bot
from app.schemas import QueryParams

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[Incident])
@router.get("/extra", response_model=List[IncidentExtra])
def read_incidents(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    # create docs, List wont work in FiltersModel
    type: Optional[List[int]] = Query(None),
    filters: IncidentFilters = Depends(IncidentFilters),
    current_user: User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    """
    Retrieve incidents.

    When `superuser` receive all, or
    only records by own company
    """
    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id
    if type:
        filters.type = ('string_array_contains', [str(t) for t in type])

    if crud.user.is_superuser(current_user) and not as_company_id:
        incidents = crud.incident.get_multi(db, params=params, filters=filters)
    else:
        incidents = crud.incident.get_multi(
            db=db,
            company_id=as_company_id,
            params=params, filters=filters
        )
    return incidents


@router.post("/", response_model=Incident, tags=['bridge'])
def create_incident(
    *,
    db: Session = Depends(deps.get_db),
    incident_in: IncidentCreate,
    current_server: Cam_Server = Depends(deps.get_current_active_server),
) -> Any:
    """
    Create new incident by Access-Token.
    """
    ai_mapping = crud.cam_ai_mapping.get(db=db, id=incident_in.ai_mapping_id)
    if ai_mapping:
        camera = crud.camera.get(db=db, id=ai_mapping.camera_id)
    if not ai_mapping or not camera:
        raise HTTPException(status_code=404, detail="References mapping not found")
    if camera.cam_server_id != current_server.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    incident = crud.incident.create(db=db, obj_in=incident_in)
    notification_bot.server_notification_incident(current_server, incident, db=db)
    return incident


@router.put("/{id:int}", response_model=Incident, tags=['bridge'])
def update_incident(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    incident_in: IncidentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a incident.

    Only for `superuser`
    """
    incident = crud.incident.get(db=db, id=id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.camera.cam_server.company_id == current_user.company_id:
        obj_in = IncidentUpdate(meta={
            **incident.meta,
            'note': incident_in.meta['note'] if 'note' in incident_in.meta else None
        })
    elif crud.user.is_superuser(current_user):
        obj_in = IncidentUpdate(
            acknowledged=True if incident.acknowledged else False,
            inaccurate=incident.inaccurate
        )

        if incident_in.acknowledged:
            obj_in.acknowledged = datetime.utcnow()
        else:
            obj_in.acknowledged = None
        if incident_in.inaccurate:
            obj_in.inaccurate = incident_in.inaccurate
    else:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    incident = crud.incident.update(db=db, db_obj=incident, obj_in=obj_in)
    return incident


@router.get("/{id:int}", response_model=Incident)
def read_incident(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get incident by ID.
    """
    incident = crud.incident.get(db=db, id=id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not crud.user.is_superuser(current_user) and (incident.camera.cam_server.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return incident


@router.delete("/{id:int}", response_model=Incident)
def delete_incident(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a incident.
    """
    incident = crud.incident.get(db=db, id=id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    incident = crud.incident.remove(db=db, id=id)
    return incident


@router.get("/{id:int}/acknowledged", response_model=Incident, tags=['bridge'])
def mark_incident_acknowledged(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark as acknowledged
    """
    incident = crud.incident.get(db=db, id=id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not crud.user.is_superuser(current_user) and incident.camera.cam_server.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if incident.created_at + timedelta(seconds=settings.NOTIFICATION_TIME_WINDOW) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Action expired")
    incident = crud.incident.mark_acknowledged(db, id, current_user.id)
    return incident


@router.get("/{id:int}/inaccurate", response_model=Incident, tags=['bridge'])
def mark_incident_inaccurate(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark as inaccurate
    """
    incident = crud.incident.get(db=db, id=id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not crud.user.is_superuser(current_user) and incident.camera.cam_server.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if incident.created_at + timedelta(seconds=settings.NOTIFICATION_TIME_WINDOW) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Action expired")
    incident = crud.incident.mark_inaccurate(db, id, current_user.id)
    return incident


@router.get("/stream/link", response_model=Any, tags=['bridge'])
def stream_incidents_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: Cam_Server = Depends(deps.get_current_server),
    request: Request
):
    """
    Stream incidents updated by server through Access-Token.
    """

    return event_source_response(
        db=db, request=request,
        pull_fn=crud.incident.get_multi_updated_by_link,
        show_fields=['uuid', 'ai_mapping_id', 'camera_id', 'acknowledged',
                     'inaccurate', 'extra', 'created_at', 'updated_at'],
        cam_server_id=current_server.id,
    )
