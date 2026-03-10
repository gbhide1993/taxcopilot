"""create notice_timeline table

Revision ID: 7f96171790ac
Revises: 359f7d7ab09e
Create Date: 2026-02-19 20:04:23.199993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f96171790ac'
down_revision: Union[str, Sequence[str], None] = '359f7d7ab09e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa


def upgrade():

    op.create_table(
        'notice_timeline',

        sa.Column(
            'id',
            sa.Integer(),
            primary_key=True,
            autoincrement=True
        ),

        sa.Column(
            'notice_id',
            sa.Integer(),
            sa.ForeignKey('notices.id', ondelete="CASCADE"),
            nullable=False
        ),

        sa.Column(
            'event_type',
            sa.String(),
            nullable=False
        ),

        sa.Column(
            'description',
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            'created_at',
            sa.TIMESTAMP(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
