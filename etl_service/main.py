from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from etl_service.services.etl_orchestrator import ETLOrchestrator
from etl_service.schemas.movie_schema import ETLJobRequest, ETLJobStatus
from shared.tracing.tracer import get_tracer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация трейсинга
tracer = get_tracer("etl_service", "1.0.0")
tracer.initialize()

app = FastAPI(
    title="Cinema ETL Service",
    description="Сервис для извлечения, трансформации и загрузки данных о фильмах",
    version="1.0.0"
)

# Инструментирование приложения для трейсинга
tracer.instrument_all(app=app)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр оркестратора
orchestrator = ETLOrchestrator()

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    try:
        await orchestrator.initialize()
        logger.info("ETL Service запущен успешно")
    except Exception as e:
        logger.error(f"Ошибка запуска ETL Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка ресурсов при завершении работы"""
    await orchestrator.close()
    logger.info("ETL Service остановлен")

@app.get("/")
async def root():
    """Главная страница ETL сервиса"""
    return {
        "service": "Cinema ETL Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/etl/start", response_model=dict)
async def start_etl_job(request: ETLJobRequest):
    """Запуск новой ETL задачи"""
    try:
        job_id = await orchestrator.start_etl_job(request)
        return {
            "job_id": job_id,
            "status": "started",
            "message": "ETL задача запущена успешно"
        }
    except Exception as e:
        logger.error(f"Ошибка запуска ETL задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/etl/jobs", response_model=List[ETLJobStatus])
async def get_all_jobs():
    """Получение списка всех ETL задач"""
    try:
        jobs = await orchestrator.get_all_jobs()
        return jobs
    except Exception as e:
        logger.error(f"Ошибка получения списка задач: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/etl/jobs/{job_id}", response_model=ETLJobStatus)
async def get_job_status(job_id: str):
    """Получение статуса конкретной ETL задачи"""
    try:
        job_status = await orchestrator.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="ETL задача не найдена")
        return job_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения статуса задачи {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/etl/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Отмена ETL задачи"""
    try:
        success = await orchestrator.cancel_job(job_id)
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Задача не может быть отменена (не найдена или уже завершена)"
            )
        return {"message": "ETL задача отменена"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка отмены задачи {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/etl/tmdb/popular")
async def start_tmdb_popular_import(
    page_start: int = 1,
    page_end: int = 5,
    update_existing: bool = False
):
    """Быстрый запуск импорта популярных фильмов из TMDB"""
    request = ETLJobRequest(
        source="tmdb",
        page_start=page_start,
        page_end=page_end,
        update_existing=update_existing
    )
    
    try:
        job_id = await orchestrator.start_etl_job(request)
        return {
            "job_id": job_id,
            "message": f"Запущен импорт популярных фильмов (страницы {page_start}-{page_end})",
            "pages": f"{page_start}-{page_end}",
            "estimated_movies": (page_end - page_start + 1) * 20
        }
    except Exception as e:
        logger.error(f"Ошибка запуска импорта популярных фильмов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/etl/tmdb/movies")
async def start_tmdb_specific_movies(
    movie_ids: List[int],
    update_existing: bool = False
):
    """Импорт конкретных фильмов по TMDB ID"""
    if not movie_ids:
        raise HTTPException(status_code=400, detail="Список ID фильмов не может быть пустым")
    
    if len(movie_ids) > 100:
        raise HTTPException(status_code=400, detail="Максимум 100 фильмов за раз")
    
    request = ETLJobRequest(
        source="tmdb",
        movie_ids=movie_ids,
        update_existing=update_existing
    )
    
    try:
        job_id = await orchestrator.start_etl_job(request)
        return {
            "job_id": job_id,
            "message": f"Запущен импорт {len(movie_ids)} фильмов",
            "movie_ids": movie_ids
        }
    except Exception as e:
        logger.error(f"Ошибка запуска импорта конкретных фильмов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Проверяем подключение к Redis
        if orchestrator.redis_client:
            await orchestrator.redis_client.ping()
        
        from shared.tracing.tracer import get_trace_id
        return {
            "status": "healthy",
            "service": "etl_service",
            "redis": "connected" if orchestrator.redis_client else "disconnected",
            "trace_id": get_trace_id()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/stats")
async def get_stats():
    """Получение статистики ETL сервиса"""
    try:
        jobs = await orchestrator.get_all_jobs()
        
        stats = {
            "total_jobs": len(jobs),
            "completed_jobs": len([j for j in jobs if j.status == "completed"]),
            "failed_jobs": len([j for j in jobs if j.status == "failed"]),
            "running_jobs": len([j for j in jobs if j.status == "running"]),
            "pending_jobs": len([j for j in jobs if j.status == "pending"]),
        }
        
        if jobs:
            total_processed = sum(j.processed_items for j in jobs)
            total_failed = sum(j.failed_items for j in jobs)
            stats.update({
                "total_processed_items": total_processed,
                "total_failed_items": total_failed,
                "success_rate": round(total_processed / (total_processed + total_failed) * 100, 2) if (total_processed + total_failed) > 0 else 0
            })
        
        return stats
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 