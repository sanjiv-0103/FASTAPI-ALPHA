"""add post ownership

Revision ID: fb0c0a211965
Revises: 6461ca5a2e72
Create Date: 2026-11-20 00:26:18.066325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb0c0a211965'
down_revision: Union[str, Sequence[str], None] = '6461ca5a2e72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
