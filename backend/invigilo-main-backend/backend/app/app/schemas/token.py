from typing import List, Optional

from pydantic import BaseModel

from .user import User


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    scopes: List[str] = []
