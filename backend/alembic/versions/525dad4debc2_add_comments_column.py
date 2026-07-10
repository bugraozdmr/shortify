"""add comments column

Revision ID: 525dad4debc2
Revises: 035fbbe052a7
Create Date: 2026-07-10 12:41:34.410441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '525dad4debc2'
down_revision: Union[str, Sequence[str], None] = '035fbbe052a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('comments', sa.JSON(), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'comments')
