#!/usr/bin/env python3
"""
Скрипт для заполнения S3 с постерами и фоновыми изображениями
Поиск фильмов в TMDB по названию
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

# Ограничения
MAX_TOTAL_SIZE = 5 * 1024 * 1024 * 1024  # 5 ГБ (увеличиваем для 1000 фильмов)
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 МБ на изображение
MAX_MOVIES = 1000  # Загружаем 1000 фильмов
IMAGE_QUALITY = 75

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


async def update_movie_urls(movie_id: int, poster_url: str = None, backdrop_url: str = None):
    """Обновляет URL постера и фона в базе данных"""
    connection = await asyncpg.connect(**DB_PARAMS)
    try:
        update_query = """
        UPDATE movies 
        SET poster_url = COALESCE($2, poster_url),
            trailer_url = COALESCE($3, trailer_url)
        WHERE id = $1
        """
        await connection.execute(update_query, movie_id, poster_url, backdrop_url)
        print(f"✅ Updated movie {movie_id} URLs in database")
    except Exception as e:
        print(f"❌ Error updating movie {movie_id}: {e}")
    finally:
        await connection.close()


async def search_movie_in_tmdb(title: str, year: int = None) -> Dict[str, Any]:
    """Ищет фильм в TMDB по названию"""
    async with aiohttp.ClientSession() as session:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {tmdb_api_key}"
        }
        
        # Формируем запрос для поиска
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
                        # Возвращаем первый результат
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


def optimize_image(image_data: bytes, max_size: int = MAX_IMAGE_SIZE) -> bytes:
    """Оптимизирует изображение"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        quality = IMAGE_QUALITY
        while quality > 20:
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            optimized_data = output.getvalue()
            
            if len(optimized_data) <= max_size:
                print(f"📸 Image optimized: {len(image_data)} -> {len(optimized_data)} bytes (quality: {quality}%)")
                return optimized_data
            
            quality -= 10
        
        # Если все еще большое, уменьшаем размер
        width, height = image.size
        while len(optimized_data) > max_size and width > 100:
            width = int(width * 0.8)
            height = int(height * 0.8)
            resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            resized_image.save(output, format='JPEG', quality=30, optimize=True)
            optimized_data = output.getvalue()
        
        print(f"📸 Image resized: {len(image_data)} -> {len(optimized_data)} bytes ({width}x{height})")
        return optimized_data
        
    except Exception as e:
        print(f"❌ Error optimizing image: {e}")
        return image_data[:max_size]


async def download_and_optimize_image(image_url: str) -> bytes:
    """Скачивает и оптимизирует изображение"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(image_url) as img_resp:
                if img_resp.status == 200:
                    image_data = await img_resp.read()
                    print(f"📥 Downloaded image: {len(image_data)} bytes from {image_url}")
                    return optimize_image(image_data)
                else:
                    print(f"⚠️ Error downloading image: {img_resp.status}")
                    return b""
        except Exception as e:
            print(f"⚠️ Exception downloading image: {e}")
            return b""


async def upload_to_s3(bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream"):
    """Загружает данные в S3"""
    global total_uploaded_size, uploaded_files_count
    
    if total_uploaded_size + len(data) > MAX_TOTAL_SIZE:
        print(f"⚠️ Size limit reached! Skipping {key}")
        return False
    
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
            
            print(f"✅ Uploaded {key} ({len(data)} bytes) - Total: {total_uploaded_size / (1024*1024):.1f} MB")
            return True
        except Exception as e:
            print(f"❌ Error uploading {key}: {e}")
            return False


async def process_movie_with_images(movie_data: Dict[str, Any]):
    """Обрабатывает фильм с загрузкой изображений"""
    global total_uploaded_size
    
    if total_uploaded_size >= MAX_TOTAL_SIZE:
        print(f"🛑 Size limit reached!")
        return False
    
    movie_id = movie_data["id"]
    title = movie_data.get("title", "Unknown")
    release_date = movie_data.get("release_date")
    year = release_date.year if release_date else None
    
    print(f"\n🎬 Processing movie {movie_id}: {title} ({year or 'N/A'})")
    
    # Ищем фильм в TMDB
    tmdb_movie = await search_movie_in_tmdb(title, year)
    
    poster_url = None
    backdrop_url = None
    
    # Создаем базовые метаданные
    metadata = {
        "id": movie_id,
        "title": title,
        "description": movie_data.get("description", ""),
        "release_date": str(release_date) if release_date else "",
        "duration": movie_data.get("duration", 0),
        "rating": movie_data.get("rating", 0),
        "movie_url": movie_data.get("movie_url", "")
    }
    
    # Если нашли в TMDB, добавляем данные и загружаем изображения
    if tmdb_movie:
        metadata.update({
            "tmdb_id": tmdb_movie.get("id"),
            "tmdb_title": tmdb_movie.get("title"),
            "tmdb_overview": tmdb_movie.get("overview"),
            "tmdb_release_date": tmdb_movie.get("release_date"),
            "tmdb_vote_average": tmdb_movie.get("vote_average"),
            "tmdb_vote_count": tmdb_movie.get("vote_count"),
            "tmdb_popularity": tmdb_movie.get("popularity")
        })
        
        # Загружаем постер
        poster_path = tmdb_movie.get("poster_path")
        if poster_path:
            poster_image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            poster_data = await download_and_optimize_image(poster_image_url)
            
            if poster_data:
                poster_key = f"movies/{movie_id}/poster.jpg"
                success = await upload_to_s3(bucket_name, poster_key, poster_data, "image/jpeg")
                if success:
                    poster_url = f"http://localhost:9000/{bucket_name}/{poster_key}"
        
        # Загружаем фоновое изображение
        backdrop_path = tmdb_movie.get("backdrop_path")
        if backdrop_path:
            backdrop_image_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
            backdrop_data = await download_and_optimize_image(backdrop_image_url)
            
            if backdrop_data:
                backdrop_key = f"movies/{movie_id}/backdrop.jpg"
                success = await upload_to_s3(bucket_name, backdrop_key, backdrop_data, "image/jpeg")
                if success:
                    backdrop_url = f"http://localhost:9000/{bucket_name}/{backdrop_key}"
    
    # Добавляем URL в метаданные
    metadata["poster_url"] = poster_url
    metadata["backdrop_url"] = backdrop_url
    
    # Загружаем метаданные
    metadata_key = f"movies/{movie_id}/metadata.json"
    metadata_json = json.dumps(metadata, ensure_ascii=False, indent=2)
    metadata_bytes = metadata_json.encode('utf-8')
    
    success = await upload_to_s3(bucket_name, metadata_key, metadata_bytes, "application/json")
    
    # Обновляем базу данных
    if success:
        await update_movie_urls(movie_id, poster_url, backdrop_url)
    
    return success


async def main():
    """Основная функция"""
    global total_uploaded_size, uploaded_files_count
    
    print("🎬 Cinema S3 Filling - With Posters & Backdrops")
    print("=" * 60)
    print(f"🚀 Starting with 1GB limit, max {MAX_MOVIES} movies")
    print(f"📊 Max image size: {MAX_IMAGE_SIZE / (1024*1024):.1f} MB")
    
    # Получаем фильмы из базы данных
    movies_query = f"""
    SELECT id, title, description, release_date, duration, rating, movie_url
    FROM movies
    ORDER BY rating DESC, id
    LIMIT {MAX_MOVIES};
    """
    
    try:
        movies_data = await execute_query(movies_query)
        print(f"📋 Found {len(movies_data)} movies in database")
        
        if not movies_data:
            print("❌ No movies found")
            return
        
        successful_uploads = 0
        
        for i, movie in enumerate(movies_data):
            if total_uploaded_size >= MAX_TOTAL_SIZE:
                print(f"🛑 Size limit reached! Processed {i} movies.")
                break
            
            try:
                print(f"\n📊 Progress: {i+1}/{len(movies_data)} | Size: {total_uploaded_size / (1024*1024):.1f} MB / {MAX_TOTAL_SIZE / (1024*1024*1024):.1f} GB")
                
                success = await process_movie_with_images(movie)
                if success:
                    successful_uploads += 1
                
                # Небольшая пауза между запросами к TMDB
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing movie {movie.get('id')}: {e}")
                continue
        
        print(f"\n🎉 S3 filling completed!")
        print(f"📊 Total uploaded: {total_uploaded_size / (1024*1024):.1f} MB")
        print(f"📊 Files uploaded: {uploaded_files_count}")
        print(f"📊 Movies processed: {successful_uploads}")
        print(f"🌐 MinIO Console: http://localhost:9001")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 