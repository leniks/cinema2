from sqlalchemy import Table, Column, Integer, String, ForeignKey
from main_service.database import Base

# Таблица связи между фильмами и актерами (many-to-many)
movie_actors = Table(
    'movie_actors',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('actor_id', Integer, ForeignKey('actors.id'), primary_key=True),
    Column('role_name', String(255), nullable=True),  # Имя персонажа, которого играет актер
    Column('order', Integer, nullable=True)  # Порядок актера в касте (0 = главная роль)
) 