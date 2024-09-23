__all__ = ["Database", ]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.configuration import config
from .models import Base
from .repositories import KeysRepository


class Database:
    """
    All in one database class.
    """
    engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    __session_maker = sessionmaker(bind=engine)

    keys_repo: KeysRepository = KeysRepository(__session_maker)
