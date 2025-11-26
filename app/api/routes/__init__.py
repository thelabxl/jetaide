from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.goals import router as goals_router

__all__ = ["auth_router", "chat_router", "goals_router"]
