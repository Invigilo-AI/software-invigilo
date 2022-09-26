from typing import Any, List

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas.core import QueryParams

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[schemas.AI_Type])
@router.get("/index", response_model=List[schemas.AI_Type])
def read_ai_types(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: schemas.AITypeFilters = Depends(deps.get_multi_filters(schemas.AITypeFilters)),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve AI types.
    """
    return crud.ai_type.get_multi(db, params=params, filters=filters)


@router.post("/", response_model=schemas.AI_Type)
def create_ai_type(
    *,
    db: Session = Depends(deps.get_db),
    ai_type_in: schemas.AI_TypeCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new AI type.
    """
    ai_type = crud.ai_type.get_by_index(db, index=ai_type_in.index)
    if ai_type:
        raise HTTPException(
            status_code=400,
            detail="The AI type index already exists in the system.",
        )
    return crud.ai_type.create(db=db, obj_in=ai_type_in)


@router.put("/{id}", response_model=schemas.AI_Type)
def update_ai_type(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    ai_type_in: schemas.AI_TypeUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a AI type.
    """
    ai_type = crud.ai_type.get(db=db, id=id)
    if not ai_type:
        raise HTTPException(status_code=404, detail="AI type not found")

    if ai_type_in.index and ai_type.index != ai_type_in.index:
        if crud.ai_type.is_used_index(db, ai_type.index):
            raise HTTPException(
                status_code=400,
                detail="The AI type index already used in the system.",
            )
        ai_type_index = crud.ai_type.get_by_index(db, index=ai_type_in.index)
        if ai_type_index:
            raise HTTPException(
                status_code=400,
                detail="The AI type index already exists in the system.",
            )
    ai_type = crud.ai_type.update(db=db, db_obj=ai_type, obj_in=ai_type_in)
    return ai_type


@router.get("/{id:int}", response_model=schemas.AI_Type)
def read_ai_type(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get AI type by ID.
    """
    ai_type = crud.ai_type.get(db=db, id=id)
    if not ai_type:
        raise HTTPException(status_code=404, detail="AI type not found")
    return ai_type


@router.get("/index/{index:int}", response_model=schemas.AI_Type)
def read_ai_type_by_index(
    *,
    db: Session = Depends(deps.get_db),
    index: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get AI type by ID.
    """
    ai_type = crud.ai_type.get_by_index(db, index)
    if not ai_type:
        raise HTTPException(status_code=404, detail="AI type not found")
    return ai_type


@router.delete("/{id}", response_model=schemas.AI_Type)
def delete_ai_type(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a AI type.
    """
    ai_type = crud.ai_type.get(db=db, id=id)
    if not ai_type:
        raise HTTPException(status_code=404, detail="AI type not found")
    if not crud.ai_type.is_used_index(db, ai_type.index):
        ai_type = crud.ai_type.remove(db=db, id=id)
    return ai_type
