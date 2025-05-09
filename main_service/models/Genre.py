from sqlalchemy import Integer, String, Text, Date, TIMESTAMP, ForeignKey, UniqueConstraint, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

from main_service.models.movie_genres import movie_genres
from main_service.database import Base, str_uniq, str_null_true


class Genre(Base):

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship("Movie",
                                                 secondary=movie_genres,
                                                 back_populates="genres",
                                                 lazy='joined')