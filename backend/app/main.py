from fastapi import FastAPI
from sqlalchemy import text 
from contextlib import asynccontextmanager

from app.core.settings import settings
from app.db.database import engine
from app.api.v1.router import api_router
from app.services.scheduler_service import start_scheduler, stop_scheduler


# 1. Define the lifespan function FIRST
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic 
    print("Starting PulseOps Scheduler...")
    start_scheduler()
    
    yield  # The FastAPI application runs while yielded
    
    # Shutdown Logic
    print("Shutting down PulseOps Scheduler...")
    stop_scheduler()


# 2. Create the FastAPI app exactly ONCE, attaching the lifespan here
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# 3. Add all your routers and endpoints to the app
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database_host": settings.DATABASE_HOST,
    }

@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "result": result.scalar(),
        }