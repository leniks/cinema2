# Import all models and association tables to ensure proper SQLAlchemy registration
from main_service.database import Base

# Import association tables first
from main_service.models.movie_genres import movie_genres
from main_service.models.user_favorites import user_favorites
from main_service.models.user_watchlist import user_watchlist
from main_service.models.movie_actors import movie_actors

# Import models
from main_service.models.Genre import Genre
from main_service.models.Movie import Movie
from main_service.models.User import User
from main_service.models.Actor import Actor

# Make all models available when importing from this module
__all__ = [
    "Base",
    "movie_genres",
    "user_favorites", 
    "user_watchlist",
    "movie_actors",
    "Genre",
    "Movie",
    "User",
    "Actor"
]
