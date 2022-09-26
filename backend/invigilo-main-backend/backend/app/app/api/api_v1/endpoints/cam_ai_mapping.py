from typing import Any, List

from fastapi import Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.api_v1.endpoints.utils import event_source_response
from app.schemas.core import QueryParams

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[schemas.Cam_AI_Mapping])
def read_cam_ai_mapping(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve Camera AI mapping.
    """
    if crud.user.is_superuser(current_user):
        cam_ai_mapping = crud.cam_ai_mapping.get_multi(db, params)
    elif current_user.company_id:
        cam_ai_mapping = crud.cam_ai_mapping.get_multi(
            db, params=params, company_id=current_user.company_id)
    else:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return cam_ai_mapping


@router.post("/", response_model=schemas.Cam_AI_Mapping)
def create_cam_ai_mapping(
    *,
    db: Session = Depends(deps.get_db),
    cam_ai_mapping_in: schemas.Cam_AI_MappingCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new Camera AI Mapping.
    """
    obj_in = schemas.Cam_AI_MappingCreate(**jsonable_encoder(cam_ai_mapping_in))
    camera = crud.camera.get(db, obj_in.camera_id)
    ai_sequence = crud.ai_sequence.get(db, obj_in.sequence_id)
    if not camera or not (crud.user.is_superuser(current_user) or camera.cam_server.company_id == current_user.company_id):
        raise HTTPException(status_code=404, detail="Camera not found")
    if not ai_sequence or not (crud.user.is_superuser(current_user) or ai_sequence.company_id == current_user.company_id):
        raise HTTPException(status_code=404, detail="AI Sequence not found")

    cam_ai_mapping = crud.cam_ai_mapping.create(db=db, obj_in=obj_in)

    return cam_ai_mapping


@router.put("/{id}", response_model=schemas.Cam_AI_Mapping)
def update_cam_ai_mapping(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    cam_ai_mapping_in: schemas.Cam_AI_MappingUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a Camera AI Mapping.
    """
    cam_ai_mapping = crud.cam_ai_mapping.get(db=db, id=id)
    if not cam_ai_mapping:
        raise HTTPException(status_code=404, detail="Camera AI Mapping not found")

    camera = crud.camera.get(db, cam_ai_mapping.camera_id)
    ai_sequence = crud.ai_sequence.get(db, cam_ai_mapping.sequence_id)

    if not camera or not crud.user.is_superuser(current_user) or (camera.cam_server.company_id != current_user.company_id):
        raise HTTPException(status_code=404, detail="Camera not found")
    if not ai_sequence or not crud.user.is_superuser(current_user) or (ai_sequence.company_id != current_user.company_id):
        raise HTTPException(status_code=404, detail="AI Sequence not found")

    cam_ai_mapping = crud.cam_ai_mapping.update(
        db=db, db_obj=cam_ai_mapping, obj_in=cam_ai_mapping_in)
    return cam_ai_mapping


@router.get("/{id:int}", response_model=schemas.Cam_AI_Mapping)
def read_cam_ai_mapping(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get Camera AI Mapping by ID.
    """
    cam_ai_mapping = crud.cam_ai_mapping.get(db=db, id=id)
    if not cam_ai_mapping:
        raise HTTPException(status_code=404, detail="Camera AI Mapping not found")
    if not crud.user.is_superuser(current_user) and (cam_ai_mapping.sequence.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return cam_ai_mapping


@router.delete("/{id}", response_model=schemas.Cam_AI_Mapping)
def delete_cam_ai_mapping(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a Camera AI Mapping.
    """
    cam_ai_mapping = crud.cam_ai_mapping.get(db=db, id=id)
    if not cam_ai_mapping:
        raise HTTPException(status_code=404, detail="Camera AI Mapping not found")
    if not crud.user.is_superuser(current_user) or cam_ai_mapping.sequence.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    cam_ai_mapping = crud.cam_ai_mapping.remove(db=db, id=id)
    return cam_ai_mapping


@router.get("/link", response_model=List[schemas.Cam_AI_Mapping], tags=['bridge'])
def read_camera_ai_mapping_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.Cam_Server = Depends(deps.get_current_server),
):
    """
    Get camera AI mapping by server through Access-Token.
    """
    return crud.cam_ai_mapping.get_multi_by_link(
        db, cam_server_id=current_server.id
    )


@router.get("/stream/link", response_model=Any, tags=['bridge'])
def stream_camera_ai_mapping_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.Cam_Server = Depends(deps.get_current_server),
    request: Request
):
    """
    Stream camera AI mapping by server through Access-Token.
    """

    return event_source_response(
        db=db, request=request,
        pull_fn=crud.cam_ai_mapping.get_multi_by_link,
        show_fields=['types', 'name', 'sequence_id', 'camera_id'],
        cam_server_id=current_server.id,
    )
