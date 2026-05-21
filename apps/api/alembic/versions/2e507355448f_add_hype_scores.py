"""add_hype_scores

Revision ID: 2e507355448f
Revises: 1b0ff766b9a1
Create Date: 2026-03-29 12:48:25.504646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e507355448f'
down_revision: Union[str, Sequence[str], None] = '1b0ff766b9a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS hype_scores (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id),
            week_number INTEGER NOT NULL,
            season_year INTEGER NOT NULL,
            hype_score DECIMAL(5,1) NOT NULL,
            hype_label VARCHAR(20) NOT NULL,
            rating_velocity DECIMAL(6,3),
            win_streak INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(team_id, week_number, season_year)
        );
    """)
    op.execute("CREATE INDEX idx_hype_scores_team ON hype_scores(team_id, season_year);")
    op.execute("CREATE INDEX idx_hype_scores_week ON hype_scores(week_number, season_year);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS hype_scores;")
