"""create notice_risk_metadata table

Revision ID: 351db21e11c7
Revises: 5811075cdf0d
Create Date: 2026-02-19 18:55:07.364676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '351db21e11c7'
down_revision: Union[str, Sequence[str], None] = '5811075cdf0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():

    op.create_table(
        'notice_risk_metadata',

        sa.Column(
            'notice_id',
            sa.Integer(),
            sa.ForeignKey('notices.id', ondelete="CASCADE"),
            primary_key=True
        ),

        sa.Column(
            'severity_score',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'days_remaining',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'repeat_flag',
            sa.Boolean(),
            nullable=False,
            server_default='false'
        ),

        sa.Column(
            'risk_score',
            sa.Float(),
            nullable=False
        ),

        sa.Column(
            'last_updated',
            sa.TIMESTAMP(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        )
    )
