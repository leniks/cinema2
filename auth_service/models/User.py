from auth_service.database import Base, str_uniq, int_pk, created_at, updated_at
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, text


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str_uniq]
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str_uniq]

    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin
        }

