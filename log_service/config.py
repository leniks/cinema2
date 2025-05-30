import os
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int

    ELASTICSEARCH_HOST: str
    ELASTICSEARCH_PORT: int
    ELASTICSEARCH_USERNAME: str
    ELASTICSEARCH_PASSWORD: str

    KIBANA_HOST: str
    KIBANA_PORT: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Log Service Settings loaded:")
        logger.info(f"DB_HOST: {self.DB_HOST}")
        logger.info(f"REDIS_HOST: {self.REDIS_HOST}")
        logger.info(f"ELASTICSEARCH_HOST: {self.ELASTICSEARCH_HOST}")
        logger.info(f"KIBANA_HOST: {self.KIBANA_HOST}")


settings = Settings()


def get_db_url():
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}


def get_redis_settings():
    return {"host": settings.REDIS_HOST, "port": settings.REDIS_PORT}


def get_elasticsearch_settings():
    return {
        "host": settings.ELASTICSEARCH_HOST,
        "port": settings.ELASTICSEARCH_PORT,
        "username": settings.ELASTICSEARCH_USERNAME,
        "password": settings.ELASTICSEARCH_PASSWORD
    }


def get_kibana_settings():
    return {
        "host": settings.KIBANA_HOST,
        "port": settings.KIBANA_PORT
    } 