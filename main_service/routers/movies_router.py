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
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data


router = APIRouter(prefix='/movies', tags=['Работа с фильмами'])


@router.get("/", summary="Получить все фильмы или фильмы с некоторыми параметрами")
async def get_movies_by_parameters(request_body: RBMovie = Depends()):
    """Простой метод для получения всех фильмов с backdrop'ами"""
    async with async_session_maker() as session:
        query = text("""
            SELECT id, title, description, release_date, duration, rating, 
                   movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at
            FROM movies 
            ORDER BY id
        """)
        result = await session.execute(query)
        rows = result.fetchall()
        
        logger.info(f"DIRECT SQL: Found {len(rows)} movies")
        if rows:
            first_row = rows[0]
            logger.info(f"DIRECT SQL: First movie - ID: {first_row[0]}, Title: {first_row[1]}, Backdrop: {first_row[8]}, Trailer: {first_row[9]}")
        
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
        
        logger.info(f"DIRECT SQL: Returning {len(movies)} movies")
        if movies:
            logger.info(f"DIRECT SQL: First movie dict - backdrop_url: {movies[0].get('backdrop_url')}, trailer_url: {movies[0].get('trailer_url')}")
        
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

@router.get("/test/{id}", summary="Тестовый endpoint для отладки")
async def test_movie_data_alt(id: int):
    """Тестовый endpoint для проверки данных фильма"""
    async with async_session_maker() as session:
        query = text("SELECT id, title, movie_url FROM movies WHERE id = :movie_id")
        result = await session.execute(query, {"movie_id": id})
        row = result.fetchone()
        
        if not row:
            return {'message': f'Фильм с ID {id} не найден'}
        
        return {
            "id": row[0],
            "title": row[1],
            "movie_url": row[2],
            "note": "Это тестовый endpoint - ALT"
        }

@router.get("/{id}/similar", summary="Получить похожие фильмы")
async def get_similar_movies(id: int):
    """Получить фильмы, похожие на указанный"""
    async with async_session_maker() as session:
        # Получаем информацию о текущем фильме
        current_movie_query = text("""
            SELECT rating FROM movies WHERE id = :movie_id
        """)
        current_result = await session.execute(current_movie_query, {"movie_id": id})
        current_row = current_result.fetchone()
        
        if not current_row:
            return []
        
        current_rating = current_row[0]
        
        # Получаем уникальные похожие фильмы с приоритетом по рейтингу
        similar_query = text("""
            WITH similar_movies AS (
                -- Сначала фильмы с точно таким же рейтингом
                SELECT DISTINCT id, title, description, release_date, duration, rating, 
                       movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at, 1 as priority
                FROM movies 
                WHERE id != :movie_id AND rating = :current_rating
                
                UNION
                
                -- Затем фильмы с рейтингом ±1
                SELECT DISTINCT id, title, description, release_date, duration, rating, 
                       movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at, 2 as priority
                FROM movies 
                WHERE id != :movie_id 
                AND rating BETWEEN :min_rating AND :max_rating 
                AND rating != :current_rating
                
                UNION
                
                -- Затем остальные фильмы
                SELECT DISTINCT id, title, description, release_date, duration, rating, 
                       movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at, 3 as priority
                FROM movies 
                WHERE id != :movie_id 
                AND rating NOT BETWEEN :min_rating AND :max_rating
            )
            SELECT id, title, description, release_date, duration, rating, 
                   movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at
            FROM similar_movies
            ORDER BY priority, RANDOM()
            LIMIT 20
        """)
        
        result = await session.execute(similar_query, {
            "movie_id": id,
            "current_rating": current_rating,
            "min_rating": max(1, current_rating - 1),
            "max_rating": min(10, current_rating + 1)
        })
        rows = result.fetchall()
        
        # Преобразуем результаты в словари с movie_id вместо id для совместимости с фронтендом
        movies = []
        for row in rows:
            movie_dict = {
                "movie_id": row[0],  # Используем movie_id для совместимости с фронтендом
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
        
        return movies

@router.get("/{id}", summary="Получить фильм по id")
async def get_movie_or_none_by_id(id: int):
    """Получить фильм по ID с актуальными данными"""
    print(f"DEBUG: Getting movie with ID {id}")
    async with async_session_maker() as session:
        query = text("""
            SELECT id, title, description, release_date, duration, rating, 
                   movie_url, poster_url, backdrop_url, trailer_url, created_at, updated_at
            FROM movies 
            WHERE id = :movie_id
        """)
        result = await session.execute(query, {"movie_id": id})
        row = result.fetchone()
        
        if not row:
            return {'message': f'Фильм с ID {id} не найден'}
        
        # Отладочная информация
        print(f"DEBUG: Raw movie_url from DB: {row[6]}")
        print(f"DEBUG: All row data: {row}")
        
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
        
        print(f"DEBUG: Movie dict movie_url: {movie_dict['movie_url']}")
        
        return movie_dict

@router.get("/{id}/test", summary="Тестовый endpoint для отладки")
async def test_movie_data(id: int):
    """Тестовый endpoint для проверки данных фильма"""
    async with async_session_maker() as session:
        query = text("SELECT id, title, movie_url FROM movies WHERE id = :movie_id")
        result = await session.execute(query, {"movie_id": id})
        row = result.fetchone()
        
        if not row:
            return {'message': f'Фильм с ID {id} не найден'}
        
        return {
            "id": row[0],
            "title": row[1],
            "movie_url": row[2],
            "note": "Это тестовый endpoint"
        }

@router.get("/watchlist/")
async def get_watchlist(user_data: User = Depends(get_current_user)):
    favorite_movies_ids = user_data.favorites
    movies = [movie.title for movie in favorite_movies_ids]
    return movies