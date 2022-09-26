from typing import Optional, List

from pydantic import EmailStr

from app.models.user import UserPermissions
from app.schemas.company import CompanyInfo
from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel


class UserFilters(QueryModel):
    email: Optional[str]
    full_name: Optional[str]
    company__name: Optional[str]

# Shared properties


class UserBase(CoreModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    company_id: Optional[int] = None
    permissions: Optional[List[UserPermissions]] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    is_active: Optional[bool]
    permissions: Optional[List[UserPermissions]] = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    permissions: Optional[List[UserPermissions]] = None


class UserInDBBase(UserBase, IDModelMixin, DateTimeModelMixin):
    pass

# Additional properties to return via API


class User(UserInDBBase):
    pass


class UserExtra(User):
    company: Optional[CompanyInfo]


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
