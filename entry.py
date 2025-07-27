#!venv/bin/python
import uvicorn

from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        app="app.main:fastapi_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
