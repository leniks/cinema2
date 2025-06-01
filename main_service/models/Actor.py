from sqlalchemy import Integer, String, Text, Date, TIMESTAMP, ForeignKey, UniqueConstraint, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

from main_service.models.movie_actors import movie_actors
from main_service.database import Base, str_uniq, str_null_true

from datetime import datetime

# Модель актера
class Actor(Base):
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Имя актера
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True)  # Дата рождения  
    photo_url: Mapped[str_null_true]  # URL фото актера
    biography: Mapped[str_null_true] = mapped_column(Text)  # Биография
    
    movies: Mapped[list["Movie"]] = relationship("Movie",
                                                 secondary=movie_actors,
                                                 back_populates="actors",
                                                 lazy='select')
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "photo_url": self.photo_url,
            "biography": self.biography,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 