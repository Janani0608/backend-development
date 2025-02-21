from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE_URL

#Engine to make a connection to the PostgreSQL database
engine = create_engine(DATABASE_URL)

#To generate sessions to interact with the database
SessionLocal = sessionmaker(bind = engine, autocommit = False, autoflush = False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
