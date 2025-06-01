from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class TMDBMovieResponse(BaseModel):
    """Схема ответа от TMDB API для фильма"""
    id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    vote_average: float = 0.0
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    genre_ids: List[int] = []
    original_language: str = "en"
    popularity: float = 0.0

class TMDBGenre(BaseModel):
    """Схема жанра от TMDB API"""
    id: int
    name: str

class TMDBCast(BaseModel):
    """Схема актера от TMDB API"""
    id: int
    name: str
    character: str
    profile_path: Optional[str] = None

class TransformedMovie(BaseModel):
    """Схема трансформированного фильма для загрузки в БД"""
    tmdb_id: int
    title: str
    description: Optional[str] = None
    release_date: Optional[date] = None
    duration: Optional[int] = None
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    trailer_url: Optional[str] = None
    movie_url: Optional[str] = None
    genres: List[str] = []
    actors: List[dict] = []

class ETLJobStatus(BaseModel):
    """Схема статуса ETL задачи"""
    job_id: str
    status: str  # pending, running, completed, failed
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

class ETLJobRequest(BaseModel):
    """Схема запроса на запуск ETL задачи"""
    source: str = "tmdb"  # tmdb, file, manual
    movie_ids: Optional[List[int]] = None  # Конкретные ID фильмов
    page_start: int = 1
    page_end: int = 5
    update_existing: bool = False 