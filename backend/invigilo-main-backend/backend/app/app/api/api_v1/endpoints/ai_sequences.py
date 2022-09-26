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


@router.get("/", response_model=List[schemas.AI_Sequence])
@router.get("/extra", response_model=List[schemas.AI_SequenceExtra])
def read_ai_sequences(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: schemas.AISequenceFilters = Depends(
        deps.get_multi_filters(schemas.AISequenceFilters)),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve AI sequences.
    """
    if crud.user.is_superuser(current_user):
        ai_sequences = crud.ai_sequence.get_multi(db, params=params, filters=filters)
    elif current_user.company_id:
        ai_sequences = crud.ai_sequence.get_multi(
            db,
            params=params,
            filters={**filters.dict(), 'company_id': current_user.company_id}
        )
    else:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return ai_sequences


@router.post("/", response_model=schemas.AI_SequenceOut)
def create_ai_sequence(
    *,
    db: Session = Depends(deps.get_db),
    ai_sequence_in: schemas.AI_SequenceCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new AI sequence.
    """
    obj_in = schemas.AI_SequenceCreate(**jsonable_encoder(ai_sequence_in))
    company = crud.company.get(db, ai_sequence_in.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    ai_sequence = crud.ai_sequence.create(db=db, obj_in=obj_in)

    return ai_sequence


@router.put("/{id}", response_model=schemas.AI_Sequence)
def update_ai_sequence(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    ai_sequence_in: schemas.AI_SequenceUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a AI sequence.
    """
    ai_sequence = crud.ai_sequence.get(db=db, id=id)
    if not ai_sequence:
        raise HTTPException(status_code=404, detail="AI Sequence not found")
    if not crud.user.is_superuser(current_user) and (ai_sequence.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    ai_sequence = crud.ai_sequence.update(
        db=db, db_obj=ai_sequence, obj_in=ai_sequence_in)
    return ai_sequence


@router.get("/{id:int}", response_model=schemas.AI_Sequence)
@router.get("/{id:int}/extra", response_model=schemas.AI_SequenceExtra)
def read_ai_sequence(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI Sequence by ID.
    """
    ai_sequence = crud.ai_sequence.get(db=db, id=id)
    if not ai_sequence:
        raise HTTPException(status_code=404, detail="AI Sequence not found")
    if not crud.user.is_superuser(current_user) and (ai_sequence.company_id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return ai_sequence


@router.delete("/{id}", response_model=schemas.AI_Sequence)
def delete_ai_sequence(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a AI sequence.
    """
    ai_sequence = crud.ai_sequence.get(db=db, id=id)
    if not ai_sequence:
        raise HTTPException(status_code=404, detail="AI Sequence not found")
    if not crud.user.is_superuser(current_user) and ai_sequence.company_id != current_user.company_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    ai_sequence = crud.ai_sequence.remove(db=db, id=id)
    return ai_sequence


@router.get("/link", response_model=List[schemas.AI_SequenceOut], tags=['bridge'])
def read_ai_sequence_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.Cam_Server = Depends(deps.get_current_server),
):
    """
    Get AI sequences by server through Access-Token.
    """
    return crud.ai_sequence.get_multi_by_link(
        db, cam_server_id=current_server.id
    )


@router.get("/stream/link", response_model=Any, tags=['bridge'])
def stream_ai_sequence_by_link(
    *, db: Session = Depends(deps.get_db),
    current_server: models.Cam_Server = Depends(deps.get_current_server),
    request: Request
):
    """
    Stream AI sequences by server through Access-Token.
    """

    return event_source_response(
        db=db, request=request,
        pull_fn=crud.ai_sequence.get_multi_by_link,
        show_fields=[
            'name', 'description', 'company_id', 'edges', 'vertexes',
            'edges.source_id', 'edges.destination_id',
            'vertexes.name', 'vertexes.types', 'vertexes.meta', 'vertexes.server_id',
        ],
        cam_server_id=current_server.id
    )
