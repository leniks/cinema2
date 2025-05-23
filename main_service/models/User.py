from sqlalchemy import Integer, String, Text, Date, TIMESTAMP, ForeignKey, UniqueConstraint, Table, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

from main_service.database import Base, str_uniq, str_null_true

from main_service.models.user_favorites import user_favorites
from main_service.models.user_watchlist import user_watchlist


class User(Base):

    username: Mapped[str_uniq]
    email: Mapped[str_uniq]
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    favorites: Mapped[list["Movie"]] = relationship("Movie",
                                                 secondary=user_favorites,
                                                 back_populates="favorites_users",
                                                 lazy='joined')

    watchlists: Mapped[list["Movie"]] = relationship("Movie",
                                                 secondary=user_watchlist,
                                                 back_populates="watchlists_users",
                                                 lazy='joined')

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin
        }