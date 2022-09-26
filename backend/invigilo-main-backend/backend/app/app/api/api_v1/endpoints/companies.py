import mimetypes
from typing import Any, List, Optional
from uuid import uuid4
import boto3
from botocore.exceptions import NoCredentialsError

from fastapi import Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.api import deps
from app.schemas import CompanyFilters, QueryParams

from app.api.api_v1.router import APIRouter

router = APIRouter()


@router.get("/", response_model=List[schemas.Company])
def read_companies(
    db: Session = Depends(deps.get_db),
    params: QueryParams = Depends(deps.get_multi_params()),
    filters: CompanyFilters = Depends(CompanyFilters),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve companies.
    """
    return crud.company.get_multi(db, params=params, filters=filters)


@router.post("/", response_model=schemas.Company)
async def create_company(
    *,
    db: Session = Depends(deps.get_db),
    company_in: schemas.CompanyCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new company.
    """
    if company_in.logo:
        company_logo = company_in.logo.replace('temp', 'company_logo')
        moved = await crud.upload.move_temporary_upload(company_in.logo, company_logo)
        if moved:
            company_in.logo = company_logo
        else:
            company_in.logo = None
    return crud.company.create(db=db, obj_in=company_in)


@router.put("/{id}", response_model=schemas.Company)
async def update_company(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    company_in: schemas.CompanyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a company.
    """
    company = crud.company.get(db=db, id=id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if not crud.user.is_superuser(current_user) and (company.id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if company.logo != company_in.logo:
        if company_in.logo:
            company_logo = company_in.logo.replace('temp', 'company_logo')
            moved = await crud.upload.move_temporary_upload(company_in.logo, company_logo)
            if moved:
                company_in.logo = company_logo
            else:
                company_in.logo = company.logo
        else:
            company_in.logo = None
    company = crud.company.update(db=db, db_obj=company, obj_in=company_in)
    return company


@router.get("/{id}", response_model=schemas.Company)
def read_company(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get company by ID.
    """
    company = crud.company.get(db=db, id=id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if not crud.user.is_superuser(current_user) and (company.id != current_user.company_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return company


@router.delete("/{id}", response_model=schemas.Company)
def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a company.
    """
    company = crud.company.get(db=db, id=id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    company = crud.company.remove(db=db, id=id)
    return company
