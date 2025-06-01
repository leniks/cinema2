from fastapi import APIRouter, Depends
from main_service.models.User import User
from main_service.services.dependencies_service import get_current_user
from main_service.services.movies_service import MovieService
from typing import Optional, List
from main_service.schemas.Movie_schema import SMovie
from main_service.database import async_session_maker
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class RBMovie:
    def __init__(self, id: int | None = None,
                 title: str | None = None):
        self.id = id
        self.title = title

    def to_dict(self) -> dict:
        data = {'id': self.id, 'title': self.title}
        # Создаем копию словаря, чтобы избежать изменения словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data


router = APIRouter(prefix='/movies', tags=['Работа с фильмами'])


@router.get("/", summary="Получить все фильмы или фильмы с некоторыми параметрами")
async def get_movies_by_parameters(request_body: RBMovie = Depends()):
    """Простой метод для получения всех фильмов с backdrop'ами"""
    async with async_session_maker() as session:
        query = text("""
            SELECT id, title, description, release_date, duration, rating, 
                   movie_url, poster_url, trailer_url, created_at, updated_at
            FROM movies 
            ORDER BY id
        """)
        result = await session.execute(query)
        rows = result.fetchall()
        
        logger.info(f"DIRECT SQL: Found {len(rows)} movies")
        if rows:
            first_row = rows[0]
            logger.info(f"DIRECT SQL: First movie - ID: {first_row[0]}, Title: {first_row[1]}, Trailer: {first_row[8]}")
        
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
                "trailer_url": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
                "updated_at": row[10].isoformat() if row[10] else None,
            }
            movies.append(movie_dict)
        
        logger.info(f"DIRECT SQL: Returning {len(movies)} movies")
        if movies:
            logger.info(f"DIRECT SQL: First movie dict - trailer_url: {movies[0].get('trailer_url')}")
        
        return movies

@router.get("/me")
async def get_me(user_data: User = Depends(get_current_user)):
    data = user_data.to_dict()
    print(data)

@router.get("/all", summary="Получить все фильмы с backdrop'ами")
async def get_all_movies():
    # Используем простой метод для получения всех фильмов с backdrop'ами
    movies = await MovieService.get_all_movies_simple()
    return movies

@router.get("/{id}", summary="Получить фильм по id")
async def get_movie_or_none_by_id(id: int):
    result = await MovieService.get_movie_or_none_by_id(id)
    if result is None:
        return {'message': f'Фильм с ID {id} не найден'}
    # Если это объект Movie, преобразуем в словарь
    if hasattr(result, 'to_dict'):
        return result.to_dict()
    # Если это уже словарь (из кэша), возвращаем как есть
    return result

@router.get("/watchlist/")
async def get_watchlist(user_data: User = Depends(get_current_user)):
    favorite_movies_ids = user_data.favorites
    movies = [movie.title for movie in favorite_movies_ids]
    return movies