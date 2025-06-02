#!/usr/bin/env python3

import asyncio
import asyncpg
from minio import Minio

# База данных настройки
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "cinema",
    "user": "admin",
    "password": "cinema"
}

# MinIO настройки
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
MINIO_BUCKET = "cinema-files"

async def update_backdrop_urls():
    """Обновление backdrop URL в базе данных"""
    
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    backdrop_objects = list(minio_client.list_objects(MINIO_BUCKET, prefix="backdrops/", recursive=True))
    print(f"Найдено backdrop файлов: {len(backdrop_objects)}")
    
    backdrop_map = {}
    for obj in backdrop_objects:
        if "movie_" in obj.object_name and "_backdrop" in obj.object_name:
            try:
                tmdb_id = obj.object_name.split("movie_")[1].split("_backdrop")[0]
                backdrop_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{obj.object_name}"
                backdrop_map[int(tmdb_id)] = backdrop_url
            except (ValueError, IndexError):
                continue
    
    print(f"Обработано backdrop URL: {len(backdrop_map)}")
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        movies = await conn.fetch("SELECT id, tmdb_id, title FROM movies WHERE tmdb_id IS NOT NULL")
        print(f"Фильмов в базе с tmdb_id: {len(movies)}")
        
        updated_count = 0
        
        for movie in movies:
            movie_id = movie['id']
            tmdb_id = movie['tmdb_id']
            title = movie['title']
            
            if tmdb_id in backdrop_map:
                backdrop_url = backdrop_map[tmdb_id]
                
                await conn.execute("""
                    UPDATE movies 
                    SET backdrop_url = $1, updated_at = NOW()
                    WHERE id = $2
                """, backdrop_url, movie_id)
                
                updated_count += 1
                print(f"Обновлен backdrop для: {title} -> {backdrop_url}")
        
        print(f"Обновлено фильмов: {updated_count}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    print("Обновление backdrop URL в базе данных")
    print("=" * 50)
    asyncio.run(update_backdrop_urls()) 