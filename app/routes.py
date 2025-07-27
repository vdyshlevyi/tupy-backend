from fastapi import APIRouter, FastAPI

from app.api.common.views import router as common_router
from app.api.root.views import router as root_router


def register_routes(fastapi_app: FastAPI):
    """Function to register all API routers in one place."""
    # versions level
    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(common_router)

    # root level
    fastapi_app.include_router(root_router)
    fastapi_app.include_router(v1_router)
