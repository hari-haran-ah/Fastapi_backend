from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        print("Database connection established")
        yield db
    finally:
        db.close()
        print("Database connection closed")

