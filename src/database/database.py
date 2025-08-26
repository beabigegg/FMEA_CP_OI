from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create the SQLAlchemy engine using the URL from our settings
engine = create_engine(settings.DATABASE_URL)

# Create a SessionLocal class. Each instance of a SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models. All models will inherit from this class.
Base = declarative_base()

# Dependency to get a DB session. This will be used in FastAPI endpoints.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
