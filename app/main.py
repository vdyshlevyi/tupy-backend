import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.responses import JSONResponse

from app.dependencies.settings import get_settings
from app.exceptions import FastAPIHttpError
from app.routes import register_routes

BASE_DIR = Path(__file__).parent.parent


settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the default log level to INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

fastapi_app = FastAPI(title=settings.TITLE, version=settings.VERSION)
fastapi_app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# custom exception handler
@fastapi_app.exception_handler(FastAPIHttpError)
async def unicorn_api_exception_handler(_: Request, exc: FastAPIHttpError) -> JSONResponse:
    content = {"detail": exc.detail}
    if exc.errors:
        content["errors"] = exc.errors
    return JSONResponse(status_code=exc.status_code, content=content)


@fastapi_app.exception_handler(Exception)
async def unicorn_app_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(str(exc))
    content = {"details": "Server Error. Please, try again"}
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


register_routes(fastapi_app=fastapi_app)
