from sqlalchemy import select, text
from main_service.database import async_session_maker

from main_service.models.User import User
from main_service.models.Genre import Genre
from main_service.models.Movie import Movie

from main_service.cache_redis import redis_client
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieService:

    @classmethod
    async def get_all_movies_simple(cls):
        """Простой метод для получения всех фильмов без relationships"""
        async with async_session_maker() as session:
            query = text("""
                SELECT id, title, description, release_date, duration, rating, 
                       movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at
                FROM movies 
                ORDER BY id
            """)
            result = await session.execute(query)
            rows = result.fetchall()
            
            logger.info(f"DEBUG: Found {len(rows)} movies")
            if rows:
                first_row = rows[0]
                logger.info(f"DEBUG: First movie - ID: {first_row[0]}, Title: {first_row[1]}, Backdrop: {first_row[8]}, Trailer: {first_row[9]}")
            
            # Преобразуем результаты в словари
            movies = []
            for row in rows:
                movie_dict = {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "release_date": row[3].isoformat() if row[3] else None,
                    "duration": row[4],
                    "rating": row[5],
                    "movie_url": row[6],
                    "poster_url": row[7],
                    "backdrop_url": row[8],
                    "trailer_url": row[9],
                    "created_at": row[10].isoformat() if row[10] else None,
                    "updated_at": row[11].isoformat() if row[11] else None,
                }
                movies.append(movie_dict)
            
            logger.info(f"DEBUG: Returning {len(movies)} movies")
            if movies:
                logger.info(f"DEBUG: First movie dict - backdrop_url: {movies[0].get('backdrop_url')}, trailer_url: {movies[0].get('trailer_url')}")
            
            return movies

    @classmethod
    async def get_movies_by_parameters(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(Movie).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_movie_or_none_by_id(cls, data_id: int):
        cache_key = f"movie_{data_id}"
        
        # ?????????? ????????? ? ?????? ?????
        log_message = {
            "service": "main_service",
            "level": "info",
            "message": f"Movie cache update for movie_id: {data_id}",
            "metadata": {
                "movie_id": data_id,
                "action": "cache_update"
            }
        }
        await redis_client.publish("logs", json.dumps(log_message))
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            # Возвращаем словарь напрямую, так как роутер ожидает объект Movie или dict
            cached_dict = json.loads(cached_data)
            return cached_dict

        async with async_session_maker() as session:
            query = select(Movie).filter_by(id=data_id)
            result = await session.execute(query)
            movie = result.unique().scalar_one_or_none()
            
            if movie:
                await redis_client.set(
                    cache_key,
                    json.dumps(movie.to_dict()),
                    ex=3600
                )
                logger.info(f"Movie {data_id} cached")
            
            return movie