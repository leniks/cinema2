from fastapi import FastAPI, Request
from main_service.routers.movies_router import router as movies_router
from fastapi.responses import JSONResponse
from main_service.services.redis_listener_service import redis_listener
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Запускает прослушивание Redis при старте приложения"""
    asyncio.create_task(redis_listener.start_listening())

@app.on_event("shutdown")
async def shutdown_event():
    """Останавливает прослушивание Redis при завершении работы приложения"""
    await redis_listener.stop_listening()

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

@app.get("/")
def home_page():
    return {"message": "Cinema main"}

app.include_router(movies_router)