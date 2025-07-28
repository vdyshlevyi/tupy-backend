#!/usr/bin/env python

import uvicorn

from app.config import Settings

settings = Settings()  # type: ignore[call-arg]


def main():
    uvicorn.run(
        app="app.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
