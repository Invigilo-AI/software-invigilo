from typing import Optional

from pydantic import root_validator
from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin, QueryModel
from app.crud.crud_upload import upload


class CompanyInfo(CoreModel, IDModelMixin):
    name: str

    class Config:
        orm_mode = True


class CompanyFilters(QueryModel):
    name: Optional[str]
    description: Optional[str]

# Shared properties


class CompanyBase(CoreModel):
    name: str
    description: Optional[str] = ''
    logo: Optional[str] = None


# Properties to receive on Company creation
class CompanyCreate(CompanyBase):
    pass

# Properties to receive on Company update
class CompanyUpdate(CompanyBase):
    name: Optional[str]


# Properties shared by models stored in DB
class CompanyInDBBase(CompanyBase, IDModelMixin, DateTimeModelMixin):
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class Company(CompanyInDBBase):
    logo_url: str = None

    @root_validator
    def signed_fields(cls, values):
        logo_url = None
        logo = values['logo']
        if logo:
            logo_url = upload.sign_url(logo)
        values['logo_url'] = logo_url

        return values


# Properties properties stored in DB
class CompanyInDB(CompanyInDBBase):
    pass
