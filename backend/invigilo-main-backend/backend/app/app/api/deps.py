from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import crud, models, schemas
from app.core import security
from app.schemas.core import QueryModel, QueryParams
from app.core.config import settings
from app.db.session import SessionLocal

from fastapi_security_telegram_webhook import OnlyTelegramNetworkWithSecret


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    scopes={
        "admin": "Company admin",
        "inspector": "Manage incidents",
        "bridge": "Manage bridge",
        "update-stream": "Consume updates from event stream"
    },
)
telegram_webhook_token = OnlyTelegramNetworkWithSecret(
    real_secret=settings.TELEGRAM_WEBHOOK_TOKEN
)


def reusable_access_token(request: Request) -> Optional[str]:
    access_token: str = request.headers.get("Access-Token")
    return access_token


async def reusable_jwt_token(request: Request) -> Optional[str]:
    try:
        jwt_token = await reusable_oauth2(request)
    except Exception as e:
        jwt_token = None
    return jwt_token


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2), security_scopes: SecurityScopes = SecurityScopes(),
) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


def get_current_server(
    db: Session = Depends(get_db), access_token: str = Depends(reusable_access_token)
) -> models.Cam_Server:
    server = None
    if access_token:
        server = crud.cam_server.get_by_access_token(db, access_token=access_token)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return server


def get_user_or_server(db: Session = Depends(get_db), token: Optional[str] = Depends(reusable_jwt_token), access_token: Optional[str] = Depends(reusable_access_token)):
    user = None
    server = None
    if access_token:
        server = crud.cam_server.get_by_access_token(db, access_token=access_token)

    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = schemas.TokenPayload(**payload)
            user = crud.user.get(db, id=token_data.sub)
        except (jwt.JWTError, ValidationError):
            pass

    if not (user or server):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    else:
        return (user, server)


def get_current_active_server(
    current_server: models.Cam_Server = Depends(get_current_server),
) -> models.Cam_Server:
    if not crud.cam_server.is_active(current_server):
        raise HTTPException(status_code=400, detail="Inactive server")
    return current_server


def get_current_active_user(
    current_user: models.User = Security(get_current_user)
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_multi_params(params: QueryParams = None) -> QueryParams:
    return params


def get_multi_filters(filters: QueryModel = None) -> QueryModel:
    # TODO integrate QueryModel as List
    return filters
