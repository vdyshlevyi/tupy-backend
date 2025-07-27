import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import register_routes

settings = get_settings()


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the default log level to INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent

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


register_routes(fastapi_app=fastapi_app)
