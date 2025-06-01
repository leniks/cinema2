import logging
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, insert, update
from etl_service.config import config
from etl_service.schemas.movie_schema import TransformedMovie

logger = logging.getLogger(__name__)

class PostgresLoader:
    """Сервис для загрузки данных в PostgreSQL"""
    
    def __init__(self):
        self.engine = create_async_engine(
            config.database_url,
            echo=False,
            pool_size=10,
            max_overflow=20
        )
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def close(self):
        """Закрытие соединения с БД"""
        await self.engine.dispose()
    
    async def load_movie(self, movie: TransformedMovie) -> Optional[int]:
        """Загрузка одного фильма в БД"""
        logger.info(f"Загрузка фильма в БД: {movie.title}")
        
        async with self.async_session() as session:
            try:
                existing_query = text("""
                    SELECT id FROM movies WHERE tmdb_id = :tmdb_id
                """)
                result = await session.execute(existing_query, {"tmdb_id": movie.tmdb_id})
                existing_movie = result.fetchone()
                
                if existing_movie:
                    movie_id = existing_movie[0]
                    await self._update_movie(session, movie_id, movie)
                    logger.info(f"Фильм обновлен: {movie.title} (ID: {movie_id})")
                else:
                    movie_id = await self._create_movie(session, movie)
                    logger.info(f"Фильм создан: {movie.title} (ID: {movie_id})")
                
                if movie.actors:
                    await self._load_actors(session, movie_id, movie.actors)
                
                if movie.genres:
                    await self._load_genres(session, movie_id, movie.genres)
                
                await session.commit()
                return movie_id
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка загрузки фильма '{movie.title}': {e}")
                return None
    
    async def _create_movie(self, session: AsyncSession, movie: TransformedMovie) -> int:
        """Создание нового фильма"""
        insert_query = text("""
            INSERT INTO movies (
                tmdb_id, title, description, release_date, duration, 
                rating, poster_url, trailer_url, movie_url, created_at, updated_at
            ) VALUES (
                :tmdb_id, :title, :description, :release_date, :duration,
                :rating, :poster_url, :trailer_url, :movie_url, NOW(), NOW()
            ) RETURNING id
        """)
        
        result = await session.execute(insert_query, {
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "description": movie.description,
            "release_date": movie.release_date,
            "duration": movie.duration,
            "rating": movie.rating,
            "poster_url": movie.poster_url,
            "trailer_url": movie.trailer_url,
            "movie_url": movie.movie_url
        })
        
        return result.fetchone()[0]
    
    async def _update_movie(self, session: AsyncSession, movie_id: int, movie: TransformedMovie):
        """Обновление существующего фильма"""
        update_query = text("""
            UPDATE movies SET
                title = :title,
                description = :description,
                release_date = :release_date,
                duration = :duration,
                rating = :rating,
                poster_url = :poster_url,
                trailer_url = :trailer_url,
                updated_at = NOW()
            WHERE id = :movie_id
        """)
        
        await session.execute(update_query, {
            "movie_id": movie_id,
            "title": movie.title,
            "description": movie.description,
            "release_date": movie.release_date,
            "duration": movie.duration,
            "rating": movie.rating,
            "poster_url": movie.poster_url,
            "trailer_url": movie.trailer_url
        })
    
    async def _load_actors(self, session: AsyncSession, movie_id: int, actors: List[Dict]):
        """Загрузка актеров фильма"""
        logger.info(f"Загрузка {len(actors)} актеров для фильма {movie_id}")
        
        delete_query = text("DELETE FROM movie_actors WHERE movie_id = :movie_id")
        await session.execute(delete_query, {"movie_id": movie_id})
        
        for actor_data in actors:
            actor_query = text("SELECT id FROM actors WHERE tmdb_id = :tmdb_id")
            result = await session.execute(actor_query, {"tmdb_id": actor_data["tmdb_id"]})
            existing_actor = result.fetchone()
            
            if existing_actor:
                actor_id = existing_actor[0]
                update_actor_query = text("""
                    UPDATE actors SET 
                        name = :name,
                        photo_url = :photo_url,
                        updated_at = NOW()
                    WHERE id = :actor_id
                """)
                await session.execute(update_actor_query, {
                    "actor_id": actor_id,
                    "name": actor_data["name"],
                    "photo_url": actor_data["photo_url"]
                })
            else:
                insert_actor_query = text("""
                    INSERT INTO actors (tmdb_id, name, photo_url, created_at, updated_at)
                    VALUES (:tmdb_id, :name, :photo_url, NOW(), NOW())
                    RETURNING id
                """)
                result = await session.execute(insert_actor_query, {
                    "tmdb_id": actor_data["tmdb_id"],
                    "name": actor_data["name"],
                    "photo_url": actor_data["photo_url"]
                })
                actor_id = result.fetchone()[0]
            
            insert_movie_actor_query = text("""
                INSERT INTO movie_actors (movie_id, actor_id, role_name)
                VALUES (:movie_id, :actor_id, :role_name)
                ON CONFLICT (movie_id, actor_id) DO UPDATE SET
                    role_name = EXCLUDED.role_name
            """)
            await session.execute(insert_movie_actor_query, {
                "movie_id": movie_id,
                "actor_id": actor_id,
                "role_name": actor_data["character"]
            })
    
    async def _load_genres(self, session: AsyncSession, movie_id: int, genres: List[str]):
        """Загрузка жанров фильма"""
        logger.info(f"Загрузка {len(genres)} жанров для фильма {movie_id}")
        
        delete_query = text("DELETE FROM movie_genres WHERE movie_id = :movie_id")
        await session.execute(delete_query, {"movie_id": movie_id})
        
        for genre_name in genres:
            genre_query = text("SELECT id FROM genres WHERE name = :name")
            result = await session.execute(genre_query, {"name": genre_name})
            existing_genre = result.fetchone()
            
            if existing_genre:
                genre_id = existing_genre[0]
            else:
                insert_genre_query = text("""
                    INSERT INTO genres (name, created_at, updated_at)
                    VALUES (:name, NOW(), NOW())
                    RETURNING id
                """)
                result = await session.execute(insert_genre_query, {"name": genre_name})
                genre_id = result.fetchone()[0]
            
            insert_movie_genre_query = text("""
                INSERT INTO movie_genres (movie_id, genre_id)
                VALUES (:movie_id, :genre_id)
                ON CONFLICT (movie_id, genre_id) DO NOTHING
            """)
            await session.execute(insert_movie_genre_query, {
                "movie_id": movie_id,
                "genre_id": genre_id
            })
    
    async def load_movies_batch(self, movies: List[TransformedMovie]) -> Dict[str, int]:
        """Загрузка пакета фильмов"""
        logger.info(f"Загрузка пакета из {len(movies)} фильмов")
        
        results = {
            "success": 0,
            "failed": 0,
            "updated": 0,
            "created": 0
        }
        
        for movie in movies:
            try:
                movie_id = await self.load_movie(movie)
                if movie_id:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(f"Ошибка загрузки фильма '{movie.title}': {e}")
                results["failed"] += 1
        
        logger.info(f"Результаты загрузки пакета: {results}")
        return results
    
    async def get_movie_by_tmdb_id(self, tmdb_id: int) -> Optional[Dict]:
        """Получение фильма по TMDB ID"""
        async with self.async_session() as session:
            query = text("""
                SELECT id, tmdb_id, title, description, release_date, 
                       duration, rating, poster_url, trailer_url, movie_url
                FROM movies 
                WHERE tmdb_id = :tmdb_id
            """)
            result = await session.execute(query, {"tmdb_id": tmdb_id})
            row = result.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "tmdb_id": row[1],
                    "title": row[2],
                    "description": row[3],
                    "release_date": row[4],
                    "duration": row[5],
                    "rating": row[6],
                    "poster_url": row[7],
                    "trailer_url": row[8],
                    "movie_url": row[9]
                }
            return None 