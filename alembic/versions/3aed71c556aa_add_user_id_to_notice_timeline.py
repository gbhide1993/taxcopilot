"""add user_id to notice_timeline

Revision ID: 3aed71c556aa
Revises: 3e7d7ffbbc8a
Create Date: 2026-03-09 16:24:43.685226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3aed71c556aa'
down_revision: Union[str, Sequence[str], None] = '3e7d7ffbbc8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'notice_timeline',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )

    op.create_foreign_key(
        None,
        'notice_timeline',
        'users',
        ['user_id'],
        ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        None,
        'notice_timeline',
        type_='foreignkey'
    )

    op.drop_column(
        'notice_timeline',
        'user_id'
    )