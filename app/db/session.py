from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# The check_same_thread: False config is necessary to work with SQLite - 
# this is a common gotcha because FastAPI can access the database with multiple 
# threads during a single request, so SQLite needs to be configured to allow that.

engine = create_engine(  # 2
    settings.SQLALCHEMY_DATABASE_URI,
    # required for sqlite
    connect_args={"check_same_thread": False},  # 3
)
# ORM-specific. Session object is main access point to DB.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # 4