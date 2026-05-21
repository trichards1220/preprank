"""add_pickem_tables

Revision ID: 1b0ff766b9a1
Revises: 269781bb831b
Create Date: 2026-03-29 12:10:57.302122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b0ff766b9a1'
down_revision: Union[str, Sequence[str], None] = '269781bb831b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS pickem_contests (
            id SERIAL PRIMARY KEY,
            sport_id INTEGER REFERENCES sports(id),
            season_year INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'open', 'locked', 'scored', 'closed')),
            opens_at TIMESTAMP,
            locks_at TIMESTAMP,
            scored_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(sport_id, season_year, week_number)
        );
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS pickem_entries (
            id SERIAL PRIMARY KEY,
            contest_id INTEGER REFERENCES pickem_contests(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            game_id INTEGER REFERENCES games(id),
            picked_team_id INTEGER REFERENCES teams(id),
            is_correct BOOLEAN,
            points_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(contest_id, user_id, game_id)
        );
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS pickem_badges (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            badge_type VARCHAR(50) NOT NULL,
            badge_name VARCHAR(200) NOT NULL,
            description VARCHAR(500),
            earned_at TIMESTAMP DEFAULT NOW(),
            contest_id INTEGER REFERENCES pickem_contests(id),
            metadata_json TEXT
        );
    """)
    op.execute("CREATE INDEX idx_pickem_entries_contest ON pickem_entries(contest_id);")
    op.execute("CREATE INDEX idx_pickem_entries_user ON pickem_entries(user_id);")
    op.execute("CREATE INDEX idx_pickem_entries_correct ON pickem_entries(contest_id, is_correct);")
    op.execute("CREATE INDEX idx_pickem_badges_user ON pickem_badges(user_id);")
    op.execute("CREATE INDEX idx_pickem_contests_status ON pickem_contests(status);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS pickem_badges;")
    op.execute("DROP TABLE IF EXISTS pickem_entries;")
    op.execute("DROP TABLE IF EXISTS pickem_contests;")
