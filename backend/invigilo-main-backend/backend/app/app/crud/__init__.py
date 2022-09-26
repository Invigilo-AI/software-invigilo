from .base import CRUDBase
from .crud_user import user
from .crud_company import company
from .crud_cam_server import cam_server
from .crud_cam_frame import cam_frame
from .crud_ai_server import ai_server
from .crud_camera import camera
from .crud_incident import incident
from .crud_ai_sequence import ai_sequence
from .crud_ai_vertex import ai_vertex
from .crud_ai_edge import ai_edge
from .crud_ai_type import ai_type
from .crud_cam_ai_mapping import cam_ai_mapping
from .crud_upload import upload

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
