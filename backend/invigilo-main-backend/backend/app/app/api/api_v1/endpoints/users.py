from typing import Any, List

from fastapi import Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.core.config import settings
from app.models.user import UserPermissions
from app.schemas import QueryParams, User, UserCreate, UserExtra, UserFilters, UserUpdate
from app.utils import send_new_account_email

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[User])
@router.get("/extra", response_model=List[UserExtra])
def read_users(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(QueryParams),
    filters: UserFilters = Depends(UserFilters),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    if crud.user.is_superuser(current_user):
        users = crud.user.get_multi(db, params=params, filters=filters)
    else:
        users = crud.user.get_multi_by_company(
            db, company_id=current_user.company_id, params=params, filters=filters)
    return users


@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    if not crud.user.is_superuser(current_user):
        user_in.company_id = current_user.company_id
        user_in.is_superuser = False
        # allow to assign only permissions that you have, no more
        if not (UserPermissions.ADMIN in current_user.permissions):
            user_in.permissions = [
                prm for prm in user_in.permissions if prm in current_user.permissions
            ]
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
        user_email = crud.user.get_by_email(db, email=email)
        if user_email:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=User)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{id}", response_model=User)
def read_user_by_id(
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user) and user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    user_in: UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user_email = crud.user.get_by_email(db, email=user_in.email)
    if user_email:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    if not crud.user.is_superuser(current_user) and user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    if not crud.user.is_superuser(current_user):
        user_in.company_id = current_user.company_id
        user_in.is_superuser = False
        # allow to assign only permissions that you have, no more
        if not (UserPermissions.ADMIN in current_user.permissions):
            user_in.permissions = [
                prm for prm in user_in.permissions if prm in current_user.permissions
            ]
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    user = crud.user.get(db, id=id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    if not crud.user.is_superuser(current_user) and not (
        user.company_id == current_user.company_id and UserPermissions.ADMIN in current_user.permissions
    ):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Hmmm... cunning you, you will need somebody else help to remove yourself :P"
        )
    return crud.user.remove(db, id=id)
