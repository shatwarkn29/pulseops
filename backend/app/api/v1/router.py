from fastapi import APIRouter

from app.api.v1.websites import router as websites_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(websites_router)
