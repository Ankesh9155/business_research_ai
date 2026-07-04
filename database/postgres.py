from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Add it to your .env file. Example:\n"
        "  DATABASE_URL=mysql+pymysql://root:root@localhost:3306/business_research_ai"
    )


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
