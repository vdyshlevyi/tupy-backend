#!venv/bin/python

import uvicorn

from app.dependencies.settings import get_settings

settings = get_settings()


def main():
    uvicorn.run(
        app="app.main:fastapi_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
