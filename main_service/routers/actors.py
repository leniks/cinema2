from fastapi import APIRouter, HTTPException
from typing import List
from main_service.database import async_session_maker
from sqlalchemy import text

router = APIRouter(prefix="/actors", tags=["actors"])

@router.get("/{movie_id}", response_model=List[dict])
async def get_movie_actors(movie_id: int):
    """Получить список актеров для фильма"""
    try:
        async with async_session_maker() as session:
            # Прямой SQL запрос для получения актеров фильма
            query = text("""
                SELECT a.id, a.name, a.photo_url, a.birth_date, a.biography, ma.role_name as character
                FROM actors a
                JOIN movie_actors ma ON a.id = ma.actor_id
                WHERE ma.movie_id = :movie_id
                ORDER BY a.id
            """)
            
            result = await session.execute(query, {"movie_id": movie_id})
            rows = result.fetchall()
            
            actors_list = []
            for row in rows:
                actor_dict = {
                    "id": row[0],
                    "name": row[1], 
                    "photo_url": row[2],
                    "birth_date": row[3].isoformat() if row[3] else None,
                    "biography": row[4],
                    "character": row[5]
                }
                actors_list.append(actor_dict)
            
            return actors_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching actors: {str(e)}")

@router.get("/actor/{actor_id}", response_model=dict)
async def get_actor_details(actor_id: int):
    """Получить детальную информацию об актере"""
    try:
        async with async_session_maker() as session:
            # Получаем информацию об актере
            actor_query = text("""
                SELECT id, name, photo_url, birth_date, biography
                FROM actors
                WHERE id = :actor_id
            """)
            
            actor_result = await session.execute(actor_query, {"actor_id": actor_id})
            actor_row = actor_result.fetchone()
            
            if not actor_row:
                raise HTTPException(status_code=404, detail="Actor not found")
            
            # Получаем фильмы актера
            movies_query = text("""
                SELECT m.id, m.title, m.poster_url, m.release_date, ma.role_name as character
                FROM movies m
                JOIN movie_actors ma ON m.id = ma.movie_id
                WHERE ma.actor_id = :actor_id
                ORDER BY m.release_date DESC
            """)
            
            movies_result = await session.execute(movies_query, {"actor_id": actor_id})
            movies_rows = movies_result.fetchall()
            
            movies_list = []
            for movie_row in movies_rows:
                movie_dict = {
                    "id": movie_row[0],
                    "title": movie_row[1],
                    "poster_url": movie_row[2],
                    "release_date": movie_row[3].isoformat() if movie_row[3] else None,
                    "character": movie_row[4]
                }
                movies_list.append(movie_dict)
            
            actor_dict = {
                "id": actor_row[0],
                "name": actor_row[1],
                "photo_url": actor_row[2],
                "birth_date": actor_row[3].isoformat() if actor_row[3] else None,
                "biography": actor_row[4],
                "movies": movies_list
            }
            
            return actor_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching actor details: {str(e)}") 