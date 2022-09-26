from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    ai_servers,
    cam_ai_mapping,
    cam_servers,
    hooks,
    login,
    users,
    utils,
    companies,
    cameras,
    incidents,
    ai_sequences,
    ai_types,
    uploads,
    reports
)

tags_meta = [
    {"name": "login", "description": "Authentication"},
    {"name": "users", "description": "Users"},
    {"name": "companies", "description": "Companies"},
    {"name": "servers", "description": "Servers"},
    {"name": "cameras", "description": "Cameras"},
    {"name": "incidents", "description": "Incidents"},
    {"name": "ai_sequences", "description": "AI sequences"},
    {"name": "ai_servers", "description": "AI servers"},
    {"name": "ai_types", "description": "AI types"},
    {"name": "ai_mapping", "description": "Camera to AI mapping"},
    {"name": "bridge", "description": "Used by AI bridge script"},
    {"name": "utils", "description": "Utils to test the system"},
    {"name": "hooks", "description": "Webhook"},
    {"name": "uploads", "description": "Uploads"},
    {"name": "reports", "description": "Reports"},
]

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(cam_servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(ai_servers.router, prefix="/ai/servers", tags=["ai_servers"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(ai_sequences.router, prefix="/ai/sequences", tags=["ai_sequences"])
api_router.include_router(cam_ai_mapping.router, prefix="/ai/mapping", tags=["ai_mapping"])
api_router.include_router(ai_types.router, prefix="/ai/types", tags=["ai_types"])
api_router.include_router(hooks.router, prefix="/hooks", tags=["hooks"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
