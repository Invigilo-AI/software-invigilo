from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
from fastapi import HTTPException


class CoreModel(BaseModel):
    pass


class QueryParams(BaseModel):
    limit: Optional[int] = 10
    skip: Optional[int] = 0
    order_by: Optional[str] = '-id'


class QueryModel(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                error["loc"] = ("query",) + error["loc"]
            raise HTTPException(422, detail=errors)


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @validator("created_at", "updated_at", pre=True)
    def default_datetime(cls, value: datetime) -> datetime:
        return value or datetime.utcnow()

    class Config:
        orm_mode = True


class IDModelMixin(BaseModel):
    id: int


class SoftDeleteModelMixin(BaseModel):
    deleted: bool = False
