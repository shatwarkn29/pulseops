from fastapi import FastAPI
from sqlalchemy import text 


from app.core.settings import settings
from app.db.database import engine
from app.api.v1.router import api_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

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
