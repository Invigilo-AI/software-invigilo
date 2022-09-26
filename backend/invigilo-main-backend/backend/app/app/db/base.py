# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.company import Company  # noqa
from app.models.cam_server import Cam_Server  # noqa
from app.models.ai_server import AI_Server  # noqa
from app.models.camera import Camera  # noqa
from app.models.incident import Incident  # noqa
from app.models.ai_sequence import AI_Sequence  # noqa
from app.models.ai_vertex import AI_Vertex  # noqa
from app.models.ai_edge import AI_Edge  # noqa
from app.models.ai_type import AI_Type  # noqa
