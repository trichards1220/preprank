"""add_refresh_tokens

Revision ID: 269781bb831b
Revises: a5a94be6e8d8
Create Date: 2026-03-29 10:22:06.011794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '269781bb831b'
down_revision: Union[str, Sequence[str], None] = 'a5a94be6e8d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(500) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            revoked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);")
    op.execute("CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS refresh_tokens;")
