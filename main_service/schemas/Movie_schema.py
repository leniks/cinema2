from enum import Enum
from pydantic import BaseModel, Field, validator, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class SMovie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str = Field(..., min_length=1, max_length=50, description="Название фильма, от 1 до 50 символов")
    description: Optional[str] = Field(default=None, max_length=500,
                                       description="Описание фильма, не более 500 символов")
    release_date: date = Field(default=None, description="Дата выхода фильма в формате ГГГГ-ММ-ДД")
    duration: int = Field(default=None, ge=0, description="Продолжительность в минутах")
    rating: int = Field(default=None, ge=1, le=10, description="Рейтинг фильма от 1 до 10")
    movie_url: Optional[str] = Field(default=None, description="URL видео файла")
    poster_url: Optional[str] = Field(default=None, description="URL постера фильма")
    backdrop_url: Optional[str] = Field(default=None, description="URL фонового изображения фильма")
    trailer_url: Optional[str] = Field(default=None, description="URL трейлера фильма")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('release_date')
    def check_release_date(cls, value):
        if value > date.today():
            raise ValueError("Дата выхода не может быть в будущем.")
        return value

