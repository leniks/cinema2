from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from auth_service.database import async_session_maker
from auth_service.models.User import User

from auth_service.cache_redis import redis_client
from datetime import datetime, timedelta

class UsersService:

    @classmethod
    async def get_user_by_id(cls, id):
        async with async_session_maker() as session:
            query = select(User).filter_by(id=id)
            result = await session.execute(query)
            users = result.scalars().one_or_none()
            return users

    @classmethod
    async def get_user_by_username(cls, username):
        async with async_session_maker() as session:
            query = select(User).filter_by(username=username)
            result = await session.execute(query)
            users = result.scalars().one_or_none()
            return users

    @classmethod
    async def add_user(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = User(**values)
                session.add(new_instance)
                try:
                    await session.commit()

                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance

    @classmethod
    async def make_admin(cls, id):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(User).filter_by(id=id)
                result = await session.execute(query)
                user = result.scalars().one_or_none()

                if user.is_admin is False:
                    user.is_admin = True
                    session.add(user)
                    await session.commit()  # Сохраняем изменения в базе данных
                    return True

                else:
                    return False
    
    @classmethod
    async def check_cache_health(cls) -> None:
        try:
            await redis_client.set("health", "ok")
            print("Cache is healthy")
        except Exception as e:
            raise e
    
    @classmethod
    async def add_session_to_cache(cls, user_id: int) -> None:
        try:
            await redis_client.set(f"user_{user_id}", f"session_started_at_{datetime.now()}")
            await redis_client.expire(f"user_{user_id}", timedelta(days=7))
            
            print(f"Session for user {user_id} added to cache")
        except Exception as e:
            raise e
    
    @classmethod
    async def delete_session_from_cache(cls, user_id: int) -> None:
        try:
            await redis_client.delete(f"user_{user_id}")
          
            print(f"{user_id} stopped session")
        except Exception as e:
            raise e
