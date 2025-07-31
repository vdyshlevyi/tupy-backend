from app.db.database import DatabaseSessionManager
from app.dependencies.settings import get_settings

settings = get_settings()

db_session_manager = DatabaseSessionManager(settings.DATABASE_URI)
