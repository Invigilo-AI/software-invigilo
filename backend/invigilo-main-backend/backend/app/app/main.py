from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
# from fastapi_pagination import add_pagination

from app.api.api_v1.api import api_router, tags_meta
from app.core.config import settings

app = FastAPI(openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
# add_pagination(app)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="0.1",
        description="API documentation for Invigilio",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://invigilo.ai/wp-content/uploads/2022/01/cropped-Invigilo-Side-Text-Logo-768x160.png"
    }
    openapi_schema['tags']=tags_meta
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
