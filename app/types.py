from dependency_injector.containers import DeclarativeContainer
from fastapi import FastAPI


class FastAPIWithContainer(FastAPI):
    container: DeclarativeContainer | None = None
