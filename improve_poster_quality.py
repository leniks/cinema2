#!/usr/bin/env python3
"""
Скрипт для улучшения качества постеров
Загружает постеры в более высоком качестве
"""

import asyncio
import json
import os
from typing import List, Dict, Any
import aiohttp
import asyncpg
from aiobotocore.session import get_session
from PIL import Image
import io

# Настройки базы данных
DB_PARAMS = {
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "cinema"),
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "cinema"),
    "port": os.getenv("DB_PORT", "5432")
}

# Настройки S3 (MinIO)
S3_CONFIG = {
    "endpoint_url": "http://localhost:9000",
    "region_name": "us-east-1",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin123"
}

bucket_name = "cinema-files"
tmdb_api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NTc1OTEzZGNhYWZkYjFlZmQ1N2ZiZWZhNWE3NzNjZiIsIm5iZiI6MTczMjIxNDQyNS4zNDQsInN1YiI6IjY3M2Y3ZTk5ODcwODFjNzI1YTk3MjgwZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.suRKgHJCd6423Ol2JgXhJEP3Wog-FrY_KQQuPF3tRNU"

# Улучшенные настройки качества
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ на изображение (увеличено)
IMAGE_QUALITY = 95  # Высокое качество (увеличено с 75 до 95)
MIN_QUALITY = 85  # Минимальное качество (увеличено с 20 до 85)

# Глобальные счетчики
total_uploaded_size = 0
uploaded_files_count = 0


async def execute_query(query: str, *parameters) -> List[Dict[str, Any]]:
    """Выполняет запрос к базе данных"""
    connection = await asyncpg.connect(**DB_PARAMS)
    try:
        results = await connection.fetch(query, *parameters)
        return [dict(row) for row in results]
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []
    finally:
        await connection.close()


async def search_movie_in_tmdb(title: str, year: int = None) -> Dict[str, Any]:
    """Ищет фильм в TMDB по названию"""
    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {tmdb_api_key}"
        }
        
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {"query": title}
        if year:
            params["year"] = year
        
        try:
            async with session.get(search_url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        movie = results[0]
                        print(f"🔍 Found in TMDB: {movie.get('title')} ({movie.get('release_date', 'N/A')[:4]})")
                        return movie
                    else:
                        print(f"⚠️ Movie '{title}' not found in TMDB")
                        return {}
                else:
                    print(f"⚠️ TMDB search error: {resp.status}")
                    return {}
        except Exception as e:
            print(f"⚠️ Exception searching movie '{title}': {e}")
            return {}


def optimize_image_high_quality(image_data: bytes, max_size: int = MAX_IMAGE_SIZE) -> bytes:
    """Оптимизирует изображение с высоким качеством"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Начинаем с высокого качества
        quality = IMAGE_QUALITY
        while quality >= MIN_QUALITY:
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            optimized_data = output.getvalue()
            
            if len(optimized_data) <= max_size:
                print(f"📸 High quality image: {len(image_data)} -> {len(optimized_data)} bytes (quality: {quality}%)")
                return optimized_data
            
            quality -= 5  # Уменьшаем качество более плавно
        
        # Если все еще большое, немного уменьшаем размер, но сохраняем качество
        width, height = image.size
        if len(optimized_data) > max_size:
            # Уменьшаем размер на 10% за раз
            while len(optimized_data) > max_size and width > 300:
                width = int(width * 0.9)
                height = int(height * 0.9)
                resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                resized_image.save(output, format='JPEG', quality=MIN_QUALITY, optimize=True)
                optimized_data = output.getvalue()
            
            print(f"📸 Image resized for quality: {len(image_data)} -> {len(optimized_data)} bytes ({width}x{height})")
        
        return optimized_data
        
    except Exception as e:
        print(f"❌ Error optimizing image: {e}")
        return image_data[:max_size]


async def download_high_quality_image(image_url: str) -> bytes:
    """Скачивает изображение в высоком качестве"""
    # Заменяем w500 на w780 для лучшего качества
    hq_url = image_url.replace('/w500/', '/w780/')
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(hq_url) as img_resp:
                if img_resp.status == 200:
                    image_data = await img_resp.read()
                    print(f"📥 Downloaded HQ image: {len(image_data)} bytes from {hq_url}")
                    return optimize_image_high_quality(image_data)
                else:
                    print(f"⚠️ Error downloading HQ image, trying original: {img_resp.status}")
                    # Fallback к оригинальному URL
                    async with session.get(image_url) as fallback_resp:
                        if fallback_resp.status == 200:
                            image_data = await fallback_resp.read()
                            print(f"📥 Downloaded fallback image: {len(image_data)} bytes")
                            return optimize_image_high_quality(image_data)
                    return b""
        except Exception as e:
            print(f"⚠️ Exception downloading image: {e}")
            return b""


async def upload_to_s3(bucket: str, key: str, data: bytes, content_type: str = "image/jpeg"):
    """Загружает данные в S3"""
    global total_uploaded_size, uploaded_files_count
    
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            await s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type
            )
            total_uploaded_size += len(data)
            uploaded_files_count += 1
            
            print(f"✅ Uploaded HQ {key} ({len(data)} bytes) - Total: {total_uploaded_size / (1024*1024):.1f} MB")
            return True
        except Exception as e:
            print(f"❌ Error uploading {key}: {e}")
            return False


async def improve_movie_poster(movie_data: Dict[str, Any]):
    """Улучшает качество постера фильма"""
    movie_id = movie_data["id"]
    title = movie_data.get("title", "Unknown")
    release_date = movie_data.get("release_date")
    year = release_date.year if release_date else None
    
    print(f"\n🎬 Improving poster for movie {movie_id}: {title} ({year or 'N/A'})")
    
    # Ищем фильм в TMDB
    tmdb_movie = await search_movie_in_tmdb(title, year)
    
    if tmdb_movie and tmdb_movie.get("poster_path"):
        poster_path = tmdb_movie["poster_path"]
        poster_url = f"https://image.tmdb.org/t/p/w780{poster_path}"  # Используем w780 для лучшего качества
        
        # Скачиваем и оптимизируем постер
        poster_data = await download_high_quality_image(poster_url)
        
        if poster_data:
            # Загружаем в S3
            poster_key = f"movies/{movie_id}/poster_hq.jpg"
            success = await upload_to_s3(bucket_name, poster_key, poster_data)
            
            if success:
                # Обновляем URL в базе данных
                new_poster_url = f"http://localhost:9000/{bucket_name}/{poster_key}"
                await update_movie_poster_url(movie_id, new_poster_url)
                return True
    
    return False


async def update_movie_poster_url(movie_id: int, poster_url: str):
    """Обновляет URL постера в базе данных"""
    connection = await asyncpg.connect(**DB_PARAMS)
    try:
        update_query = "UPDATE movies SET poster_url = $2 WHERE id = $1"
        await connection.execute(update_query, movie_id, poster_url)
        print(f"✅ Updated movie {movie_id} poster URL in database")
    except Exception as e:
        print(f"❌ Error updating movie {movie_id}: {e}")
    finally:
        await connection.close()


async def main():
    """Основная функция"""
    print("🎨 Cinema Poster Quality Improvement")
    print("=" * 60)
    print(f"🎯 Target: High quality posters (quality: {IMAGE_QUALITY}%)")
    print(f"📏 Max image size: {MAX_IMAGE_SIZE / (1024*1024):.1f} MB")
    
    # Получаем фильмы из базы данных
    movies_query = "SELECT * FROM movies WHERE poster_url IS NOT NULL ORDER BY id LIMIT 20"
    movies = await execute_query(movies_query)
    
    if not movies:
        print("❌ No movies found in database")
        return
    
    print(f"📋 Found {len(movies)} movies to improve")
    
    improved_count = 0
    for i, movie in enumerate(movies, 1):
        print(f"\n📊 Progress: {i}/{len(movies)}")
        
        success = await improve_movie_poster(movie)
        if success:
            improved_count += 1
        
        # Небольшая пауза между запросами
        await asyncio.sleep(0.5)
    
    print(f"\n🎉 Completed! Improved {improved_count}/{len(movies)} posters")
    print(f"📊 Total uploaded: {total_uploaded_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    asyncio.run(main()) 