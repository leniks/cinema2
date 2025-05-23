from fastapi import APIRouter, Depends
from main_service.models.User import User
from main_service.services.dependencies_service import get_current_user
from main_service.services.movies_service import MovieService
from typing import Optional, List
from main_service.schemas.Movie_schema import SMovie


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
async def get_movies_by_parameters(request_body: RBMovie = Depends()) -> List[SMovie]:
    return await MovieService.get_movies_by_parameters(**request_body.to_dict())

@router.get("/me")
async def get_me(user_data: User = Depends(get_current_user)):
    data = user_data.to_dict()
    print(data)

@router.get("/{id}", summary="Получить фильм по id")
async def get_movie_or_none_by_id(id: int) -> SMovie | dict:
    result = await MovieService.get_movie_or_none_by_id(id)
    if result is None:
        return {'message': f'Фильм с ID {id} не найден'}
    return result

@router.get("/watchlist/")
async def get_watchlist(user_data: User = Depends(get_current_user)):
    favorite_movies_ids = user_data.favorites
    movies = [movie.title for movie in favorite_movies_ids]
    return movies