"""Add deleted_at to posts for soft delete

Revision ID: c5d4e3f2a1b0
Revises: b2f1c3d4e5f6
Create Date: 2026-07-08 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d4e3f2a1b0'
down_revision: Union[str, Sequence[str], None] = 'b2f1c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('posts', 'deleted_at')
