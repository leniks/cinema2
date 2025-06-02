import aiohttp
import asyncio
import logging
from typing import List, Optional, Dict, Any
from etl_service.config import config
from etl_service.schemas.movie_schema import TMDBMovieResponse, TMDBGenre, TMDBCast

logger = logging.getLogger(__name__)

class TMDBExtractor:
    """Сервис для извлечения данных из TMDB API"""
    
    def __init__(self):
        self.api_key = config.TMDB_API_KEY
        self.base_url = config.TMDB_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("TMDB_API_KEY не установлен. Некоторые функции будут недоступны.")
    
    async def __aenter__(self):
        """Создание HTTP сессии"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие HTTP сессии"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Выполнение HTTP запроса к TMDB API"""
        if not self.api_key:
            logger.error("TMDB API ключ не настроен")
            return None
        
        if not self.session:
            logger.error("HTTP сессия не инициализирована")
            return None
        
        url = f"{self.base_url}/{endpoint}"
        request_params = {"api_key": self.api_key, "language": "ru-RU"}
        
        if params:
            request_params.update(params)
        
        try:
            async with self.session.get(url, params=request_params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limiting - ждем и повторяем
                    logger.warning("Rate limit достигнут, ожидание...")
                    await asyncio.sleep(1)
                    return await self._make_request(endpoint, params)
                else:
                    logger.error(f"TMDB API ошибка: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка запроса к TMDB: {e}")
            return None
    
    async def get_popular_movies(self, page: int = 1) -> List[TMDBMovieResponse]:
        """Получение популярных фильмов"""
        logger.info(f"Получение популярных фильмов, страница {page}")
        
        data = await self._make_request("movie/popular", {"page": page})
        if not data or "results" not in data:
            return []
        
        movies = []
        for movie_data in data["results"]:
            try:
                movie = TMDBMovieResponse(**movie_data)
                movies.append(movie)
            except Exception as e:
                logger.warning(f"Ошибка парсинга фильма {movie_data.get('id')}: {e}")
        
        logger.info(f"Получено {len(movies)} фильмов со страницы {page}")
        return movies
    
    async def get_movie_details(self, movie_id: int) -> Optional[TMDBMovieResponse]:
        """Получение детальной информации о фильме"""
        logger.info(f"Получение деталей фильма {movie_id}")
        
        data = await self._make_request(f"movie/{movie_id}")
        if not data:
            return None
        
        try:
            # Преобразуем жанры в список ID для совместимости
            if "genres" in data:
                data["genre_ids"] = [genre["id"] for genre in data["genres"]]
            
            movie = TMDBMovieResponse(**data)
            logger.info(f"Получены детали фильма: {movie.title}")
            return movie
        except Exception as e:
            logger.error(f"Ошибка парсинга деталей фильма {movie_id}: {e}")
            return None
    
    async def get_movie_cast(self, movie_id: int) -> List[TMDBCast]:
        """Получение актерского состава фильма"""
        logger.info(f"Получение актеров фильма {movie_id}")
        
        data = await self._make_request(f"movie/{movie_id}/credits")
        if not data or "cast" not in data:
            return []
        
        cast = []
        # Берем только первых 10 актеров
        for cast_data in data["cast"][:10]:
            try:
                actor = TMDBCast(**cast_data)
                cast.append(actor)
            except Exception as e:
                logger.warning(f"Ошибка парсинга актера: {e}")
        
        logger.info(f"Получено {len(cast)} актеров для фильма {movie_id}")
        return cast
    
    async def get_genres(self) -> List[TMDBGenre]:
        """Получение списка жанров"""
        logger.info("Получение списка жанров")
        
        data = await self._make_request("genre/movie/list")
        if not data or "genres" not in data:
            return []
        
        genres = []
        for genre_data in data["genres"]:
            try:
                genre = TMDBGenre(**genre_data)
                genres.append(genre)
            except Exception as e:
                logger.warning(f"Ошибка парсинга жанра: {e}")
        
        logger.info(f"Получено {len(genres)} жанров")
        return genres
    
    async def search_movies(self, query: str, page: int = 1) -> List[TMDBMovieResponse]:
        """Поиск фильмов по названию"""
        logger.info(f"Поиск фильмов: '{query}', страница {page}")
        
        data = await self._make_request("search/movie", {"query": query, "page": page})
        if not data or "results" not in data:
            return []
        
        movies = []
        for movie_data in data["results"]:
            try:
                movie = TMDBMovieResponse(**movie_data)
                movies.append(movie)
            except Exception as e:
                logger.warning(f"Ошибка парсинга найденного фильма: {e}")
        
        logger.info(f"Найдено {len(movies)} фильмов по запросу '{query}'")
        return movies 