from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cam_frame import Cam_Frame
from app.schemas.cam_frame import CameraFrameCreate, CameraFrameUpdate


class CRUDCam_Frame(CRUDBase[Cam_Frame, CameraFrameCreate, CameraFrameUpdate]):
    pass


cam_frame = CRUDCam_Frame(Cam_Frame)
