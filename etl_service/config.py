import os
from typing import Optional

class ETLConfig:
    """Конфигурация для ETL сервиса"""
    
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "cinema")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "cinema")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Elasticsearch settings
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT: int = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    
    # MinIO settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "cinema-files")
    
    # TMDB API settings
    TMDB_API_KEY: Optional[str] = os.getenv("TMDB_API_KEY")
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"
    TMDB_BACKDROP_BASE_URL: str = "https://image.tmdb.org/t/p/w1280"
    
    # ETL settings
    BATCH_SIZE: int = int(os.getenv("ETL_BATCH_SIZE", "10"))
    MAX_RETRIES: int = int(os.getenv("ETL_MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("ETL_RETRY_DELAY", "5"))
    
    @property
    def database_url(self) -> str:
        """Строка подключения к PostgreSQL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """Строка подключения к Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def elasticsearch_url(self) -> str:
        """Строка подключения к Elasticsearch"""
        return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

# Глобальный экземпляр конфигурации
config = ETLConfig() 