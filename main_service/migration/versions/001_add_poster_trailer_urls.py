"""Add poster_url and trailer_url to Movie

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новые колонки в таблицу movies
    op.add_column('movies', sa.Column('poster_url', sa.String(), nullable=True))
    op.add_column('movies', sa.Column('trailer_url', sa.String(), nullable=True))


def downgrade() -> None:
    # Удаляем добавленные колонки
    op.drop_column('movies', 'trailer_url')
    op.drop_column('movies', 'poster_url') 