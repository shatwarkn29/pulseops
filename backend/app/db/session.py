from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session

from app.core.settings import Settings


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=Settings().DATABASE_USER,
    password=Settings().DATABASE_PASSWORD,
    host=Settings().DATABASE_HOST,
    port=Settings().DATABASE_PORT,
    database=Settings().DATABASE_NAME,
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()