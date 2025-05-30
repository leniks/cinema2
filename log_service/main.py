from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from log_service.services.redis_listener_service import redis_listener
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Starts Redis listener when application starts"""
    asyncio.create_task(redis_listener.start_listening())

@app.on_event("shutdown")
async def shutdown_event():
    """Stops Redis listener when application shuts down"""
    await redis_listener.stop_listening()

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

@app.get("/")
def home_page():
    return {"message": "Log service"} 