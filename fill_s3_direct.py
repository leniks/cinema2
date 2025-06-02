#!/usr/bin/env python3

import asyncio
import aiohttp
import asyncpg
import os
import tempfile
from minio import Minio
from minio.error import S3Error
from datetime import datetime, date
import json

# TMDB API настройки
TMDB_API_KEY = "4575913dcaafdb1efd57fbefa5a773cf"
TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NTc1OTEzZGNhYWZkYjFlZmQ1N2ZiZWZhNWE3NzNjZiIsIm5iZiI6MTczMjIxNDQyNS4zNDQsInN1YiI6IjY3M2Y3ZTk5ODcwODFjNzI1YTk3MjgwZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.suRKgHJCd6423Ol2JgXhJEP3Wog-FrY_KQQuPF3tRNU"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"

# MinIO настройки
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
MINIO_BUCKET = "cinema-files"

# База данных настройки
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "cinema",
    "user": "admin",
    "password": "cinema"
}

class TMDBDirectFiller:
    def __init__(self):
        self.session = None
        self.minio_client = None
        self.db_pool = None
        self.processed_movies = 0
        self.processed_actors = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
        )
        
        self.minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        
        if not self.minio_client.bucket_exists(MINIO_BUCKET):
            self.minio_client.make_bucket(MINIO_BUCKET)
            print(f"Bucket {MINIO_BUCKET} создан")
        
        self.db_pool = await asyncpg.create_pool(
            **DB_CONFIG,
            min_size=1,
            max_size=10
        )
        print("Подключение к базе данных установлено")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.db_pool:
            await self.db_pool.close()
    
    async def make_tmdb_request(self, endpoint: str, params: dict = None):
        """Выполнение запроса к TMDB API"""
        url = f"{TMDB_BASE_URL}/{endpoint}"
        request_params = {"api_key": TMDB_API_KEY, "language": "ru-RU"}
        
        if params:
            request_params.update(params)
        
        try:
            async with self.session.get(url, params=request_params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    print("Rate limit, ожидание...")
                    await asyncio.sleep(1)
                    return await self.make_tmdb_request(endpoint, params)
                else:
                    print(f"TMDB API ошибка: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return None
    
    async def download_image(self, url: str, object_name: str):
        """Скачивание и загрузка изображения в MinIO"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(await response.read())
                        temp_file_path = temp_file.name
                    
                    self.minio_client.fput_object(MINIO_BUCKET, object_name, temp_file_path)
                    
                    os.unlink(temp_file_path)
                    
                    return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
                else:
                    print(f"Ошибка скачивания изображения: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return None
    
    async def save_genre_to_db(self, genre_id: int, name: str):
        """Сохранение жанра в базу данных"""
        async with self.db_pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO genres (id, name, created_at, updated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        updated_at = EXCLUDED.updated_at
                """, genre_id, name, datetime.now(), datetime.now())
            except Exception as e:
                print(f"Ошибка сохранения жанра {name}: {e}")
    
    async def save_actor_to_db(self, actor_data: dict, photo_url: str = None):
        """Сохранение актера в базу данных"""
        async with self.db_pool.acquire() as conn:
            try:
                existing_actor = await conn.fetchval("""
                    SELECT id FROM actors WHERE name = $1
                """, actor_data["name"])
                
                if existing_actor:
                    await conn.execute("""
                        UPDATE actors SET 
                            biography = $1,
                            photo_url = $2,
                            updated_at = $3
                        WHERE id = $4
                    """, 
                    actor_data.get("biography", ""),
                    photo_url,
                    datetime.now(),
                    existing_actor
                    )
                    return existing_actor
                else:
                    actor_id = await conn.fetchval("""
                        INSERT INTO actors (name, biography, birth_date, photo_url, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING id
                    """, 
                    actor_data["name"], 
                    actor_data.get("biography", ""),
                    None,
                    photo_url,
                    datetime.now(), 
                    datetime.now()
                    )
                    return actor_id
            except Exception as e:
                print(f"Ошибка сохранения актера {actor_data['name']}: {e}")
                return None
    
    async def save_movie_to_db(self, movie_data: dict, poster_url: str = None, backdrop_url: str = None):
        """Сохранение фильма в базу данных"""
        async with self.db_pool.acquire() as conn:
            try:
                movie_id = await conn.fetchval("""
                    INSERT INTO movies (tmdb_id, title, description, release_date, duration, rating, poster_url, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (tmdb_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        release_date = EXCLUDED.release_date,
                        duration = EXCLUDED.duration,
                        rating = EXCLUDED.rating,
                        poster_url = EXCLUDED.poster_url,
                        updated_at = EXCLUDED.updated_at
                    RETURNING id
                """, 
                movie_data["id"],
                movie_data["title"],
                movie_data.get("overview", ""),
                datetime.strptime(movie_data.get("release_date", "2000-01-01"), "%Y-%m-%d").date() if movie_data.get("release_date") else date(2000, 1, 1),
                movie_data.get("runtime", 0),
                round(movie_data.get("vote_average", 0)),
                poster_url,
                datetime.now(),
                datetime.now()
                )
                return movie_id
            except Exception as e:
                print(f"Ошибка сохранения фильма {movie_data['title']}: {e}")
                return None
    
    async def link_movie_genre(self, movie_id: int, genre_id: int):
        """Связывание фильма с жанром"""
        async with self.db_pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO movie_genres (movie_id, genre_id)
                    VALUES ($1, $2)
                    ON CONFLICT (movie_id, genre_id) DO NOTHING
                """, movie_id, genre_id)
            except Exception as e:
                print(f"Ошибка связывания фильма с жанром: {e}")
    
    async def link_movie_actor(self, movie_id: int, actor_id: int, character: str = None):
        """Связывание фильма с актером"""
        async with self.db_pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO movie_actors (movie_id, actor_id, role_name)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (movie_id, actor_id) DO UPDATE SET
                        role_name = EXCLUDED.role_name
                """, movie_id, actor_id, character)
            except Exception as e:
                print(f"Ошибка связывания фильма с актером: {e}")
    
    async def process_movie(self, movie_basic: dict):
        """Обработка одного фильма"""
        movie_id = movie_basic["id"]
        print(f"Обрабатываю фильм: {movie_basic['title']} (ID: {movie_id})")
        
        movie_details = await self.make_tmdb_request(f"movie/{movie_id}")
        if not movie_details:
            print(f"Не удалось получить детали фильма {movie_id}")
            return
        
        poster_url = None
        if movie_details.get("poster_path"):
            poster_tmdb_url = f"{TMDB_IMAGE_BASE_URL}{movie_details['poster_path']}"
            poster_object_name = f"posters/movie_{movie_id}_poster.jpg"
            poster_url = await self.download_image(poster_tmdb_url, poster_object_name)
            if poster_url:
                print(f"  Постер загружен: {poster_object_name}")
        
        backdrop_url = None
        if movie_details.get("backdrop_path"):
            backdrop_tmdb_url = f"{TMDB_BACKDROP_BASE_URL}{movie_details['backdrop_path']}"
            backdrop_object_name = f"backdrops/movie_{movie_id}_backdrop.jpg"
            backdrop_url = await self.download_image(backdrop_tmdb_url, backdrop_object_name)
            if backdrop_url:
                print(f"  Бекдроп загружен: {backdrop_object_name}")
        
        db_movie_id = await self.save_movie_to_db(movie_details, poster_url, backdrop_url)
        if not db_movie_id:
            print(f"Не удалось сохранить фильм в базу")
            return
        
        for genre in movie_details.get("genres", []):
            await self.save_genre_to_db(genre["id"], genre["name"])
            await self.link_movie_genre(db_movie_id, genre["id"])
        
        credits = await self.make_tmdb_request(f"movie/{movie_id}/credits")
        if credits and "cast" in credits:
            for actor_data in credits["cast"][:10]:
                photo_url = None
                if actor_data.get("profile_path"):
                    photo_tmdb_url = f"{TMDB_IMAGE_BASE_URL}{actor_data['profile_path']}"
                    photo_object_name = f"actors/actor_{actor_data['id']}_photo.jpg"
                    photo_url = await self.download_image(photo_tmdb_url, photo_object_name)
                
                db_actor_id = await self.save_actor_to_db(actor_data, photo_url)
                if db_actor_id:
                    await self.link_movie_actor(db_movie_id, db_actor_id, actor_data.get("character"))
                    self.processed_actors += 1
                    print(f"  Актер: {actor_data['name']}")
        
        self.processed_movies += 1
        print(f"Фильм обработан: {movie_details['title']} ({self.processed_movies}/100)")
    
    async def fill_s3_with_movies(self):
        """Основная функция заполнения S3"""
        print("Начинаю заполнение S3 фильмами и актерами...")
        
        movies_to_process = []
        page = 1
        
        while len(movies_to_process) < 100 and page <= 10:
            print(f"Загружаю страницу {page} популярных фильмов...")
            
            popular_movies = await self.make_tmdb_request("movie/popular", {"page": page})
            if not popular_movies or "results" not in popular_movies:
                print(f"Не удалось загрузить страницу {page}")
                break
            
            movies_to_process.extend(popular_movies["results"])
            page += 1
        
        movies_to_process = movies_to_process[:100]
        print(f"Найдено {len(movies_to_process)} фильмов для обработки")
        
        for movie in movies_to_process:
            await self.process_movie(movie)
            await asyncio.sleep(0.1)
        
        print(f"ЗАВЕРШЕНО!")
        print(f"Обработано фильмов: {self.processed_movies}")
        print(f"Обработано актеров: {self.processed_actors}")

async def main():
    """Главная функция"""
    async with TMDBDirectFiller() as filler:
        await filler.fill_s3_with_movies()

if __name__ == "__main__":
    print("Скрипт прямого заполнения S3 фильмами и актерами")
    print("=" * 50)
    asyncio.run(main()) 