from sqlalchemy import select
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
    async def get_movies_by_parameters(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(Movie).filter_by(**filter_by)
            result = await session.execute(query)
            return result.unique().scalars().all()

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
            return json.loads(cached_data)

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