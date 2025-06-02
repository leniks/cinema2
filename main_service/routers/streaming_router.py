from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from main_service.database import async_session_maker
import aiohttp
import asyncio
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/streaming', tags=['Стриминг видео'])

async def get_movie_video_url(movie_id: int) -> Optional[str]:
    """Получает URL видео для фильма"""
    async with async_session_maker() as session:
        query = text("SELECT movie_url FROM movies WHERE id = :movie_id")
        result = await session.execute(query, {"movie_id": movie_id})
        row = result.fetchone()
        if row and row[0]:
            return row[0]
        return None

def parse_range_header(range_header: str, file_size: int) -> tuple:
    """Парсит Range header и возвращает start и end позиции"""
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        return 0, file_size - 1
    
    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
    
    return start, min(end, file_size - 1)

async def stream_from_url(url: str, start: int = 0, end: Optional[int] = None, chunk_size: int = 8192):
    """Стримит данные из URL с поддержкой Range requests"""
    headers = {}
    if end is not None:
        headers['Range'] = f'bytes={start}-{end}'
    elif start > 0:
        headers['Range'] = f'bytes={start}-'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status not in [200, 206]:
                    raise HTTPException(status_code=response.status, detail="Error streaming video")
                
                async for chunk in response.content.iter_chunked(chunk_size):
                    yield chunk
    except Exception as e:
        logger.error(f"Error streaming from URL {url}: {e}")
        raise HTTPException(status_code=500, detail="Error streaming video")

@router.get("/{movie_id}")
async def stream_movie(movie_id: int, request: Request):
    """Стримит видео фильма с поддержкой Range requests"""
    
    # Получаем URL видео из базы данных
    video_url = await get_movie_video_url(movie_id)
    if not video_url:
        raise HTTPException(status_code=404, detail="Video not found for this movie")
    
    # Для MinIO URL нужно добавить префикс если его нет
    if not video_url.startswith(('http://', 'https://')):
        # Предполагаем, что это относительный путь в MinIO
        video_url = f"http://minio:9000/{video_url}"
    elif "localhost:9000" in video_url:
        # Заменяем localhost на minio для внутреннего доступа в Docker
        video_url = video_url.replace("localhost:9000", "minio:9000")
    
    # Получаем размер файла
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(video_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=404, detail="Video file not found")
                file_size = int(response.headers.get('Content-Length', 0))
    except Exception as e:
        logger.error(f"Error getting file size for {video_url}: {e}")
        raise HTTPException(status_code=500, detail="Error accessing video file")
    
    # Обрабатываем Range header
    range_header = request.headers.get('Range')
    if range_header:
        start, end = parse_range_header(range_header, file_size)
        content_length = end - start + 1
        
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(content_length),
            'Content-Type': 'video/mp4'
        }
        
        return StreamingResponse(
            stream_from_url(video_url, start, end),
            status_code=206,
            headers=headers,
            media_type='video/mp4'
        )
    else:
        # Полная отдача файла
        headers = {
            'Content-Length': str(file_size),
            'Accept-Ranges': 'bytes',
            'Content-Type': 'video/mp4'
        }
        
        return StreamingResponse(
            stream_from_url(video_url),
            status_code=200,
            headers=headers,
            media_type='video/mp4'
        )

@router.get("/{movie_id}/info")
async def get_video_info(movie_id: int):
    """Получает информацию о видео (продолжительность, размер, и т.д.)"""
    video_url = await get_movie_video_url(movie_id)
    if not video_url:
        raise HTTPException(status_code=404, detail="Video not found for this movie")
    
    # Для MinIO URL
    if not video_url.startswith(('http://', 'https://')):
        video_url = f"http://minio:9000/{video_url}"
    elif "localhost:9000" in video_url:
        # Заменяем localhost на minio для внутреннего доступа в Docker
        video_url = video_url.replace("localhost:9000", "minio:9000")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(video_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=404, detail="Video file not found")
                
                file_size = int(response.headers.get('Content-Length', 0))
                content_type = response.headers.get('Content-Type', 'video/mp4')
                
                return {
                    "movie_id": movie_id,
                    "video_url": video_url,
                    "file_size": file_size,
                    "content_type": content_type,
                    "supports_range": "bytes" in response.headers.get('Accept-Ranges', '')
                }
    except Exception as e:
        logger.error(f"Error getting video info for {video_url}: {e}")
        raise HTTPException(status_code=500, detail="Error accessing video file") 