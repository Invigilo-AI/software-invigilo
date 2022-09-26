from typing import Any, List

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.api_v1.endpoints.utils import event_source_response
from app.schemas.core import QueryParams

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[schemas.AI_Server])
@router.get("/extra", response_model=List[schemas.AI_ServerExtra])
def read_ai_servers(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: schemas.AIServerFilters = Depends(deps.get_multi_filters(schemas.AIServerFilters)),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve servers.

    When `superuser` receive all, or
    only records by own company
    """
    if crud.user.is_superuser(current_user):
        servers = crud.ai_server.get_multi(db, params=params, filters=filters)
    else:
        servers = crud.ai_server.get_multi_by_company(
            db=db, company_id=current_user.company_id, params=params, filters=filters
        )
    return servers


@router.post("/", response_model=schemas.AI_Server)
def create_ai_server(
    *,
    db: Session = Depends(deps.get_db),
    server_in: schemas.AI_ServerCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new server.
    """
    return crud.ai_server.create(db=db, obj_in=server_in)


@router.put("/{id}", response_model=schemas.AI_Server)
def update_ai_server(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    server_in: schemas.AI_ServerUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a server.
    """
    server = crud.ai_server.get(db=db, id=id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    server = crud.ai_server.update(db=db, db_obj=server, obj_in=server_in)
    return server


@router.get("/me", response_model=schemas.AI_Server, tags=['bridge'])
def read_server_me(
    *, db: Session = Depends(deps.get_db),
    current_server: models.User = Depends(deps.get_current_server),
):
    """
    Get server by Access-Token.
    """
    server = crud.ai_server.get(db=db, id=current_server.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.get("/{id:int}", response_model=schemas.AI_Server)
@router.get("/{id:int}/extra", response_model=schemas.AI_ServerExtra)
def read_ai_server(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get server by ID.
    """
    server = crud.ai_server.get(db=db, id=id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    if not crud.user.is_superuser(current_user) and (server.company_id != current_user.company_id and server.company_id != None):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return server


@router.delete("/{id}", response_model=schemas.AI_Server)
def delete_ai_server(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a server.
    """
    server = crud.ai_server.get(db=db, id=id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    server = crud.ai_server.remove(db=db, id=id)
    return server


@router.get("/link", response_model=List[schemas.AI_Server], tags=['bridge'])
def read_ai_server_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.Cam_Server = Depends(deps.get_current_server)
):
    """
    Get AI servers by server through Access-Token.
    """
    return crud.ai_server.get_multi_by_link(db, cam_server_id=current_server.id, company_id=current_server.company_id)


@router.get("/stream/link", response_model=schemas.AI_Server, tags=['bridge'])
def stream_ai_server_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.Cam_Server = Depends(deps.get_current_server),
    request: Request
):
    """
    Stream AI servers by server through Access-Token.
    """

    return event_source_response(
        db=db, request=request,
        pull_fn=crud.ai_server.get_multi_by_link,
        show_fields=['vertex_types', 'name', 'location', 'connection', 'is_active'],
        cam_server_id=current_server.id,
        company_id=current_server.company_id
    )
