from sqlalchemy import select
from main_service.database import async_session_maker

from main_service.models.User import User
from main_service.models.Genre import Genre
from main_service.models.Movie import Movie


class MovieService:

    @classmethod
    async def get_movies_by_parameters(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(Movie).filter_by(**filter_by)
            result = await session.execute(query)
            return result.unique().scalars().all()

    @classmethod
    async def get_movie_or_none_by_id(cls, data_id: int):
        async with async_session_maker() as session:
            query = select(Movie).filter_by(id=data_id)
            result = await session.execute(query)
            return result.unique().scalar_one_or_none()