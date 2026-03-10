"""create notice_assignments table

Revision ID: 359f7d7ab09e
Revises: 351db21e11c7
Create Date: 2026-02-19 19:32:11.958856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '359f7d7ab09e'
down_revision: Union[str, Sequence[str], None] = '351db21e11c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.create_table(
        'notice_assignments',

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
            'assigned_to',
            sa.Integer(),
            sa.ForeignKey('users.id'),
            nullable=False
        ),

        sa.Column(
            'role',
            sa.String(),
            nullable=False
        ),

        sa.Column(
            'assigned_at',
            sa.TIMESTAMP(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        )
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
