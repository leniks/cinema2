from sqlalchemy import select
from main_service.database import async_session_maker
from sqlalchemy.exc import SQLAlchemyError

from main_service.models.User import User
from main_service.models.Genre import Genre
from main_service.models.Movie import Movie

from main_service.schemas.User_schema import EmailStr


class UserService:

    @classmethod
    async def get_user_or_none_by_email(cls, user_email: str):
        async with async_session_maker() as session:
            query = select(User).filter_by(email=user_email)
            result = await session.execute(query)
            return result.unique().scalar_one_or_none()

    @classmethod
    async def get_user_or_none_by_id(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(User).filter_by(id=user_id)
            result = await session.execute(query)
            return result.unique().scalar_one_or_none()
