from fastapi import APIRouter

from .auth import router as auth_router
# from .users import router as users_router
from .conversations import router as conversations_router
from .messages import router as messages_router
from .memories import router as memories_router
from .analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
# api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(conversations_router, prefix="/conversation", tags=["conversations"])
api_router.include_router(messages_router, prefix="/message", tags=["messages"])
api_router.include_router(memories_router, prefix="/memory", tags=["memories"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
