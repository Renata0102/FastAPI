'''Making a local database with SQLite'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..utils.config import settings



engine = create_engine(
    settings.DB_URL,
    connect_args={'check_same_thread':False}
)

session_local = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()
