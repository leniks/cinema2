import logging
from typing import List, Optional
from datetime import datetime, date
from etl_service.schemas.movie_schema import TMDBMovieResponse, TMDBCast, TransformedMovie
from etl_service.config import config

logger = logging.getLogger(__name__)

class DataTransformer:
    """Сервис для трансформации данных из TMDB в формат БД"""
    
    def __init__(self):
        self.genre_mapping = {
            28: "Боевик",
            12: "Приключения", 
            16: "Мультфильм",
            35: "Комедия",
            80: "Криминал",
            99: "Документальный",
            18: "Драма",
            10751: "Семейный",
            14: "Фэнтези",
            36: "История",
            27: "Ужасы",
            10402: "Музыка",
            9648: "Детектив",
            10749: "Мелодрама",
            878: "Фантастика",
            10770: "Телефильм",
            53: "Триллер",
            10752: "Военный",
            37: "Вестерн"
        }
    
    def transform_movie(self, tmdb_movie: TMDBMovieResponse, cast: List[TMDBCast] = None) -> TransformedMovie:
        """Трансформация фильма из TMDB в формат БД"""
        logger.info(f"Трансформация фильма: {tmdb_movie.title}")
        
        # Преобразование даты выпуска
        release_date = None
        if tmdb_movie.release_date:
            try:
                release_date = datetime.strptime(tmdb_movie.release_date, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Неверный формат даты: {tmdb_movie.release_date}")
        
        # Преобразование рейтинга (TMDB использует шкалу 0-10, мы тоже)
        rating = round(tmdb_movie.vote_average, 1)
        
        # Формирование URL для постера
        poster_url = None
        if tmdb_movie.poster_path:
            poster_url = f"{config.TMDB_IMAGE_BASE_URL}{tmdb_movie.poster_path}"
        
        # Формирование URL для backdrop
        backdrop_url = None
        if tmdb_movie.backdrop_path:
            backdrop_url = f"{config.TMDB_BACKDROP_BASE_URL}{tmdb_movie.backdrop_path}"
        
        # Преобразование жанров
        genres = []
        for genre_id in tmdb_movie.genre_ids:
            if genre_id in self.genre_mapping:
                genres.append(self.genre_mapping[genre_id])
        
        # Преобразование актеров
        actors = []
        if cast:
            for actor in cast:
                actor_data = {
                    "tmdb_id": actor.id,
                    "name": actor.name,
                    "character": actor.character,
                    "photo_url": f"{config.TMDB_IMAGE_BASE_URL}{actor.profile_path}" if actor.profile_path else None
                }
                actors.append(actor_data)
        
        # Создание трансформированного объекта
        transformed = TransformedMovie(
            tmdb_id=tmdb_movie.id,
            title=tmdb_movie.title,
            description=tmdb_movie.overview,
            release_date=release_date,
            duration=tmdb_movie.runtime,
            rating=rating,
            poster_url=poster_url,
            backdrop_url=backdrop_url,
            genres=genres,
            actors=actors
        )
        
        logger.info(f"Фильм трансформирован: {transformed.title} ({len(actors)} актеров, {len(genres)} жанров)")
        return transformed
    
    def validate_movie_data(self, movie: TransformedMovie) -> bool:
        """Валидация данных фильма перед загрузкой"""
        errors = []
        
        # Обязательные поля
        if not movie.title or len(movie.title.strip()) == 0:
            errors.append("Отсутствует название фильма")
        
        if movie.rating < 0 or movie.rating > 10:
            errors.append(f"Неверный рейтинг: {movie.rating}")
        
        if movie.duration and movie.duration < 0:
            errors.append(f"Неверная продолжительность: {movie.duration}")
        
        # Проверка даты
        if movie.release_date:
            current_year = datetime.now().year
            if movie.release_date.year > current_year + 5:
                errors.append(f"Слишком далекая дата выпуска: {movie.release_date}")
        
        if errors:
            logger.warning(f"Ошибки валидации для фильма '{movie.title}': {', '.join(errors)}")
            return False
        
        return True
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """Очистка текстовых данных"""
        if not text:
            return None
        
        # Удаление лишних пробелов и переносов строк
        cleaned = text.strip().replace('\n', ' ').replace('\r', ' ')
        
        # Замена множественных пробелов на одинарные
        while '  ' in cleaned:
            cleaned = cleaned.replace('  ', ' ')
        
        return cleaned if cleaned else None
    
    def normalize_title(self, title: str) -> str:
        """Нормализация названия фильма"""
        if not title:
            return ""
        
        # Удаление лишних символов и пробелов
        normalized = title.strip()
        
        # Удаление года из названия если он в скобках в конце
        if normalized.endswith(')') and '(' in normalized:
            parts = normalized.rsplit('(', 1)
            if len(parts) == 2:
                year_part = parts[1].rstrip(')')
                if year_part.isdigit() and len(year_part) == 4:
                    normalized = parts[0].strip()
        
        return normalized
    
    def extract_year_from_title(self, title: str) -> Optional[int]:
        """Извлечение года из названия фильма"""
        if not title or '(' not in title:
            return None
        
        try:
            # Ищем год в скобках в конце названия
            if title.endswith(')'):
                year_part = title.split('(')[-1].rstrip(')')
                if year_part.isdigit() and len(year_part) == 4:
                    year = int(year_part)
                    if 1900 <= year <= datetime.now().year + 5:
                        return year
        except (ValueError, IndexError):
            pass
        
        return None 