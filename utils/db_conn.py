import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

def get_db() -> Session:
    user = os.environ.get("DBUSER")
    password = os.environ.get("DBPASS")
    host = os.environ.get("DBHOST")
    db_name = os.environ.get("DBNAME")
    port = os.environ.get("DBPORT")
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
    )
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    return db