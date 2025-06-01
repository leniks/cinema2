from sqlalchemy import Integer, String, Text, Date, TIMESTAMP, ForeignKey, UniqueConstraint, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

from main_service.models.movie_genres import movie_genres
from main_service.models.user_favorites import user_favorites
from main_service.models.user_watchlist import user_watchlist
from main_service.models.movie_actors import movie_actors

from main_service.database import Base, str_uniq, str_null_true

from datetime import datetime

# Модель фильма
class Movie(Base):

    title: Mapped[str_null_true]
    description: Mapped[str] = mapped_column(Text)
    release_date: Mapped[Date] = mapped_column(Date)
    duration: Mapped[int] = mapped_column(Integer)  # продолжительность в минутах
    rating: Mapped[int] = mapped_column(Integer)  # рейтинг от 1 до 10
    movie_url: Mapped[str_null_true]
    poster_url: Mapped[str_null_true]  # URL постера в MinIO
    trailer_url: Mapped[str_null_true]  # URL трейлера в MinIO

    genres: Mapped[list["Genre"]] = relationship("Genre",
                                                 secondary=movie_genres,
                                                 back_populates="movies",
                                                 lazy='select')
    actors: Mapped[list["Actor"]] = relationship("Actor",
                                                 secondary=movie_actors,
                                                 back_populates="movies",
                                                 lazy='select')
    favorites_users: Mapped[list["User"]] = relationship("User",
                                                 secondary=user_favorites,
                                                 back_populates="favorites",
                                                 lazy='select')
    watchlists_users: Mapped[list["User"]] = relationship("User",
                                                 secondary=user_watchlist,
                                                 back_populates="watchlists",
                                                 lazy='select')
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "duration": self.duration,
            "rating": self.rating,
            "movie_url": self.movie_url,
            "poster_url": self.poster_url,
            "trailer_url": self.trailer_url,
        }
    
