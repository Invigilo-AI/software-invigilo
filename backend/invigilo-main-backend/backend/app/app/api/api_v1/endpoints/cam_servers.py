from typing import Any, List

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas.core import QueryParams

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[schemas.Cam_Server])
@router.get("/extra", response_model=List[schemas.Cam_ServerExtra])
def read_servers(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: schemas.CamServerFilters = Depends(
        deps.get_multi_filters(schemas.CamServerFilters)),
    current_user: models.User = Depends(deps.get_current_active_user),
    company_id: int = None,
) -> Any:
    """
    Retrieve servers.

    When `superuser` receive all, or
    only records by own company
    """

    as_company_id = current_user.company_id
    if current_user.is_superuser and company_id:
        as_company_id = company_id

    if crud.user.is_superuser(current_user) and not as_company_id:
        servers = crud.cam_server.get_multi(db, params=params, filters=filters)
    else:
        servers = crud.cam_server.get_multi_by_company(
            db=db, company_id=as_company_id,
            params=params, filters=filters
        )
    return servers


@router.post("/", response_model=schemas.Cam_Server)
def create_server(
    *,
    db: Session = Depends(deps.get_db),
    server_in: schemas.Cam_ServerCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new server.
    """
    return crud.cam_server.create(db=db, obj_in=server_in)


@router.put("/{id}", response_model=schemas.Cam_Server)
@router.put("/{id}/extra", response_model=schemas.Cam_ServerExtra)
async def update_server(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    server_in: schemas.Cam_ServerUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a server.
    """
    server = crud.cam_server.get(db=db, id=id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    if not crud.user.is_superuser(current_user):
        if server.company_id != current_user.company_id:
            raise HTTPException(status_code=400, detail="Not enough permissions")
        levels = server_in.meta['levels'] if 'levels' in server_in.meta else None
        if levels is not None:
            for idx, level in enumerate(levels):
                if 'image' in level and 'file_name' in level['image']:
                    image = level['image']['file_name']
                    if image.startswith('temp/'):
                        level_image = f'server_{id}/level_{idx}'
                        moved = await crud.upload.move_temporary_upload(image, level_image)
                        if moved:
                            level['image']['file_name'] = level_image
            server_in = schemas.Cam_ServerUpdate(meta={
                **(server.meta if server.meta else {}),
                'levels': levels
            })
        else:
            server_in = schemas.Cam_ServerUpdate()

    server = crud.cam_server.update(db=db, db_obj=server, obj_in=server_in)
    return server


@router.get("/me", response_model=schemas.Cam_Server, tags=['bridge'])
def read_server_me(
    *, db: Session = Depends(deps.get_db),
    current_server: models.User = Depends(deps.get_current_server),
):
    """
    Get server by Access-Token.
    """
    server = crud.cam_server.get(db=db, id=current_server.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.get("/{id:int}", response_model=schemas.Cam_Server)
def read_server(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get server by ID.
    """
    server = crud.cam_server.get(db=db, id=id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    if not crud.user.is_superuser(current_user) and (server.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return server


@router.delete("/{id}", response_model=schemas.Cam_Server)
def delete_server(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a server.
    """
    server = crud.cam_server.get(db=db, id=id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    server = crud.cam_server.remove(db=db, id=id)
    return server
