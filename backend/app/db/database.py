from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from app.core.settings import settings

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
    database=settings.DATABASE_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)