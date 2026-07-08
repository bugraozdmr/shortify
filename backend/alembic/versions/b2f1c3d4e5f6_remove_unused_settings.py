"""Remove unused settings

Revision ID: b2f1c3d4e5f6
Revises: a80c82ba6ef4
Create Date: 2026-07-08 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2f1c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'a80c82ba6ef4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM settings WHERE `key` IN ("
        "'default_voice_male', 'default_voice_female', "
        "'font_style', 'font_size', 'subtitle_outline', "
        "'youtube_privacy', 'youtube_category_id', 'youtube_tags', "
        "'ai_system_prompt'"
        ")"
    )


def downgrade() -> None:
    pass
