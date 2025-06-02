import asyncio
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from etl_service.services.tmdb_extractor import TMDBExtractor
from etl_service.services.data_transformer import DataTransformer
from etl_service.services.postgres_loader import PostgresLoader
from etl_service.schemas.movie_schema import ETLJobStatus, ETLJobRequest, TransformedMovie
from etl_service.config import config
import redis.asyncio as redis
import json

logger = logging.getLogger(__name__)

class ETLOrchestrator:
    """Главный сервис для координации ETL процесса"""
    
    def __init__(self):
        self.extractor = TMDBExtractor()
        self.transformer = DataTransformer()
        self.postgres_loader = PostgresLoader()
        self.redis_client = None
        self.jobs: Dict[str, ETLJobStatus] = {}
    
    async def initialize(self):
        """Инициализация сервиса"""
        try:
            self.redis_client = redis.from_url(config.redis_url)
            await self.redis_client.ping()
            logger.info("ETL Orchestrator инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации ETL Orchestrator: {e}")
            raise
    
    async def close(self):
        """Закрытие соединений"""
        if self.redis_client:
            await self.redis_client.close()
        await self.postgres_loader.close()
    
    async def start_etl_job(self, request: ETLJobRequest) -> str:
        """Запуск ETL задачи"""
        job_id = str(uuid.uuid4())
        
        job_status = ETLJobStatus(
            job_id=job_id,
            status="pending",
            started_at=datetime.now().isoformat()
        )
        
        self.jobs[job_id] = job_status
        
        asyncio.create_task(self._run_etl_job(job_id, request))
        
        logger.info(f"ETL задача запущена: {job_id}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[ETLJobStatus]:
        """Получение статуса ETL задачи"""
        return self.jobs.get(job_id)
    
    async def _run_etl_job(self, job_id: str, request: ETLJobRequest):
        """Выполнение ETL задачи"""
        job_status = self.jobs[job_id]
        
        try:
            job_status.status = "running"
            await self._publish_job_status(job_status)
            
            if request.source == "tmdb":
                await self._run_tmdb_etl(job_id, request)
            else:
                raise ValueError(f"Неподдерживаемый источник данных: {request.source}")
            
            job_status.status = "completed"
            job_status.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Ошибка выполнения ETL задачи {job_id}: {e}")
            job_status.status = "failed"
            job_status.error_message = str(e)
            job_status.completed_at = datetime.now().isoformat()
        
        await self._publish_job_status(job_status)
    
    async def _run_tmdb_etl(self, job_id: str, request: ETLJobRequest):
        """Выполнение ETL из TMDB"""
        job_status = self.jobs[job_id]
        
        async with self.extractor:
            if request.movie_ids:
                await self._process_specific_movies(job_id, request.movie_ids)
            else:
                await self._process_popular_movies(job_id, request.page_start, request.page_end)
    
    async def _process_specific_movies(self, job_id: str, movie_ids: List[int]):
        """Обработка конкретных фильмов по ID"""
        job_status = self.jobs[job_id]
        job_status.total_items = len(movie_ids)
        
        for movie_id in movie_ids:
            try:
                movie_data = await self.extractor.get_movie_details(movie_id)
                if not movie_data:
                    logger.warning(f"Не удалось получить данные фильма {movie_id}")
                    job_status.failed_items += 1
                    continue
                
                cast_data = await self.extractor.get_movie_cast(movie_id)
                
                transformed_movie = self.transformer.transform_movie(movie_data, cast_data)
                
                if not self.transformer.validate_movie_data(transformed_movie):
                    logger.warning(f"Данные фильма {movie_id} не прошли валидацию")
                    job_status.failed_items += 1
                    continue
                
                result = await self.postgres_loader.load_movie(transformed_movie)
                if result:
                    job_status.processed_items += 1
                    await self._publish_movie_update(transformed_movie)
                else:
                    job_status.failed_items += 1
                
                await self._publish_job_status(job_status)
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Ошибка обработки фильма {movie_id}: {e}")
                job_status.failed_items += 1
    
    async def _process_popular_movies(self, job_id: str, page_start: int, page_end: int):
        """Обработка популярных фильмов по страницам"""
        job_status = self.jobs[job_id]
        
        all_movies = []
        for page in range(page_start, page_end + 1):
            movies = await self.extractor.get_popular_movies(page)
            all_movies.extend(movies)
            await asyncio.sleep(0.3)
        
        job_status.total_items = len(all_movies)
        await self._publish_job_status(job_status)
        
        batch_size = config.BATCH_SIZE
        for i in range(0, len(all_movies), batch_size):
            batch = all_movies[i:i + batch_size]
            await self._process_movies_batch(job_id, batch)
    
    async def _process_movies_batch(self, job_id: str, movies_batch: List):
        """Обработка пакета фильмов"""
        job_status = self.jobs[job_id]
        transformed_movies = []
        
        for movie_data in movies_batch:
            try:
                detailed_movie = await self.extractor.get_movie_details(movie_data.id)
                if not detailed_movie:
                    job_status.failed_items += 1
                    continue
                
                cast_data = await self.extractor.get_movie_cast(movie_data.id)
                
                transformed_movie = self.transformer.transform_movie(detailed_movie, cast_data)
                
                if self.transformer.validate_movie_data(transformed_movie):
                    transformed_movies.append(transformed_movie)
                else:
                    job_status.failed_items += 1
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Ошибка обработки фильма {movie_data.id}: {e}")
                job_status.failed_items += 1
        
        if transformed_movies:
            results = await self.postgres_loader.load_movies_batch(transformed_movies)
            job_status.processed_items += results["success"]
            job_status.failed_items += results["failed"]
            
            for movie in transformed_movies:
                await self._publish_movie_update(movie)
        
        await self._publish_job_status(job_status)
    
    async def _publish_job_status(self, job_status: ETLJobStatus):
        """Публикация статуса задачи в Redis"""
        if self.redis_client:
            try:
                await self.redis_client.publish(
                    "etl_job_status",
                    json.dumps(job_status.dict())
                )
            except Exception as e:
                logger.error(f"Ошибка публикации статуса задачи: {e}")
    
    async def _publish_movie_update(self, movie: TransformedMovie):
        """Публикация обновления фильма в Redis"""
        if self.redis_client:
            try:
                movie_data = {
                    "action": "movie_updated",
                    "movie_id": movie.tmdb_id,
                    "title": movie.title,
                    "timestamp": datetime.now().isoformat()
                }
                await self.redis_client.publish(
                    "movie_cache_update",
                    json.dumps(movie_data)
                )
            except Exception as e:
                logger.error(f"Ошибка публикации обновления фильма: {e}")
    
    async def get_all_jobs(self) -> List[ETLJobStatus]:
        """Получение всех ETL задач"""
        return list(self.jobs.values())
    
    async def cancel_job(self, job_id: str) -> bool:
        """Отмена ETL задачи"""
        if job_id in self.jobs:
            job_status = self.jobs[job_id]
            if job_status.status in ["pending", "running"]:
                job_status.status = "cancelled"
                job_status.completed_at = datetime.now().isoformat()
                await self._publish_job_status(job_status)
                return True
        return False 