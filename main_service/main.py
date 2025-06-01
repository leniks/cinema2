from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from main_service.routers.movies_router import router as movies_router
from main_service.routers.files_router import router as files_router
from main_service.routers.actors import router as actors_router
from main_service.routers.streaming_router import router as streaming_router
from fastapi.responses import JSONResponse, HTMLResponse
from main_service.services.redis_listener_service import redis_listener
import asyncio
import os
import io

app = FastAPI()

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins для отладки
    allow_credentials=False,  # Отключаем credentials для отладки
    allow_methods=["*"],
    allow_headers=["*"],
)

# Дополнительный middleware для CORS (на случай если стандартный не работает)
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Подключаем статические файлы
static_dir = "/app/static"
if not os.path.exists(static_dir):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

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

@app.get("/proxy/poster/{movie_id}")
async def proxy_poster(movie_id: int):
    """Проксирует постеры из MinIO для избежания CORS проблем"""
    from fastapi.responses import StreamingResponse
    import aiohttp
    import logging
    from aiobotocore.session import get_session
    
    logger = logging.getLogger(__name__)
    
    try:
        # Используем aiobotocore для доступа к MinIO
        session = get_session()
        async with session.create_client(
            's3',
            endpoint_url='http://minio:9000',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin123',
            region_name='us-east-1'
        ) as s3_client:
            
            # Получаем объект из S3
            response = await s3_client.get_object(
                Bucket='cinema-files',
                Key=f'movies/{movie_id}/poster.jpg'
            )
            
            # Читаем содержимое
            content = await response['Body'].read()
            logger.info(f"Successfully fetched poster, size: {len(content)} bytes")
            
            return StreamingResponse(
                io.BytesIO(content),
                media_type="image/jpeg",
                headers={"Cache-Control": "max-age=3600"}
            )
            
    except Exception as e:
        logger.error(f"Error fetching poster: {e}")
    
    # Возвращаем placeholder SVG
    placeholder_svg = '''<svg width="300" height="400" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#333"/>
        <text x="50%" y="50%" font-family="Arial" font-size="18" fill="#fff" text-anchor="middle" dy=".3em">No Poster</text>
    </svg>'''
    
    return StreamingResponse(
        io.BytesIO(placeholder_svg.encode()),
        media_type="image/svg+xml"
    )

@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cinema Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { text-align: center; color: #ff6b6b; }
            .movie-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
            .movie-card { background: #2a2a2a; padding: 15px; border-radius: 10px; }
            .movie-poster { width: 100%; height: 400px; object-fit: cover; border-radius: 8px; }
            .movie-title { font-size: 18px; font-weight: bold; color: #ff6b6b; margin: 10px 0; }
            .movie-info { display: flex; justify-content: space-between; }
            .rating { background: #ff6b6b; padding: 4px 8px; border-radius: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Cinema - Фильмы с постерами</h1>
            <div id="movies" class="movie-grid"></div>
        </div>
        <script>
            fetch('/movies/')
                .then(r => r.json())
                .then(movies => {
                    const container = document.getElementById('movies');
                    movies.sort((a, b) => (b.poster_url ? 1 : 0) - (a.poster_url ? 1 : 0) || b.rating - a.rating)
                        .slice(0, 20)
                        .forEach(movie => {
                            const card = document.createElement('div');
                            card.className = 'movie-card';
                            const posterUrl = movie.poster_url ? 
                                `/proxy/poster/${movie.id}` : 
                                'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIFBvc3RlcjwvdGV4dD48L3N2Zz4=';
                            card.innerHTML = `
                                <img src="${posterUrl}" 
                                     alt="${movie.title}" class="movie-poster"
                                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIFBvc3RlcjwvdGV4dD48L3N2Zz4='">
                                <div class="movie-title">${movie.title}</div>
                                <div class="movie-info">
                                    <span>${new Date(movie.release_date).getFullYear()}</span>
                                    <span class="rating">${movie.rating}/10</span>
                                </div>
                            `;
                            container.appendChild(card);
                        });
                });
        </script>
    </body>
    </html>
    """

app.include_router(movies_router)
app.include_router(files_router)
app.include_router(actors_router)
app.include_router(streaming_router)