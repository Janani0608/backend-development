from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+psycopg2-binary://jananikarthikeyan@localhost:5432/banking_db"

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
