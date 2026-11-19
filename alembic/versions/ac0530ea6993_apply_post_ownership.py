"""apply post ownership

Revision ID: ac0530ea6993
Revises: fb0c0a211965
Create Date: 2026-11-20 00:32:15.621342

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac0530ea6993'
down_revision: Union[str, Sequence[str], None] = 'fb0c0a211965'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 1. Add Post Ownership Column
def upgrade():
    op.add_column(
        "posts",
        sa.Column("owner_id", sa.Integer(), nullable=True)
    )

    op.create_foreign_key(
        "posts_owner_id_fkey",
        "posts",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE"
    )

# 2. Reverse Migration
def downgrade():
    op.drop_constraint(
        "posts_owner_id_fkey",
        "posts",
        type_="foreignkey"
    )

    op.drop_column("posts", "owner_id")
