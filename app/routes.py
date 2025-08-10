from fastapi import APIRouter, FastAPI

from app.api.authentication.views import router as authentication_router
from app.api.common.views import router as common_router
from app.api.orders.views import router as orders_router
from app.api.root.views import router as root_router
from app.api.users.views import router as users_router


def register_routes(fastapi_app: FastAPI):
    """Function to register all API routers in one place."""
    # versions level
    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(authentication_router)
    v1_router.include_router(common_router)
    v1_router.include_router(orders_router)
    v1_router.include_router(users_router)

    # root level
    fastapi_app.include_router(root_router)
    fastapi_app.include_router(v1_router)
