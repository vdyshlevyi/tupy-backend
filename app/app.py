from app.containers import Container
from app.main import make_app

container = Container()
settings = container.settings()
app = make_app()
app.container = container
