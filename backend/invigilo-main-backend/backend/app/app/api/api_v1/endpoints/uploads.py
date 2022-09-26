from typing import Any, List, Optional

from fastapi import Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.schemas import TemporaryUpload

from app.api.api_v1.router import APIRouter

router = APIRouter()

@router.get("/")
async def get_upload(
    object_id: str = Query(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload temporary
    """
    response =  await crud.upload.fetch_upload(object_id)
    if not response:
        raise HTTPException(status_code=404, detail="Upload not found")
    return response

@router.post("/", response_model=TemporaryUpload)
async def temporary_upload(
    file: Optional[UploadFile] = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload temporary
    """
    return await crud.upload.temporary_upload(file)



@router.delete("/", response_model=TemporaryUpload)
async def delete_temporary_upload(
    *,
    object_id: str = Query(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a temporary upload.
    """
    return await crud.upload.remove_temporary_upload(object_id)
