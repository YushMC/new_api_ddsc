from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

from src.conf.all_keys import ENV_KEYS

Base = declarative_base()

class DATABASE_CONNECTION:
    def __init__(self) -> None:
        self.__DB_HOST =os.getenv(ENV_KEYS.DB_HOST)
        self.__DB_USER=os.getenv(ENV_KEYS.DB_USER)
        self.__DB_PASSWORD=os.getenv(ENV_KEYS.DB_PASSWORD)
        self.__DB_NAME=os.getenv(ENV_KEYS.DB_NAME)
        self.__DB_PORT=os.getenv(ENV_KEYS.DB_PORT)

    @property
    def DB_URL(self):
        return f"mysql+pymysql://{self.__DB_USER}:{self.__DB_PASSWORD}@{self.__DB_HOST}:{self.__DB_PORT}/{self.__DB_NAME}"


# Singleton instance
_db_instance = None

def get_database_init():
    """Obtener instancia global de DATABASE_INIT"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DATABASE_INIT()
    return _db_instance


class DATABASE_INIT:
    def __init__(self) -> None:
        self.__db = DATABASE_CONNECTION()

    def create_engine(self):
        return create_engine(self.__db.DB_URL, pool_pre_ping=True)
    
    def __create_session(self):
        return sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.create_engine()
        )
    
    @property
    def BASE_TYPE(self)->Any:
        return Base
    
    def get_db(self):
        """Generator que proporciona sesión de BD para FastAPI Depends"""
        SessionLocal = self.__create_session()
        db = SessionLocal()

        try:
            yield db
        finally:
            db.close()
