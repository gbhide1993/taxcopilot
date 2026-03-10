"""create draft_versions table

Revision ID: 5811075cdf0d
Revises: 52cef5704e18
Create Date: 2026-02-19 17:16:58.684782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5811075cdf0d'
down_revision: Union[str, Sequence[str], None] = '52cef5704e18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.create_table(
        'draft_versions',

        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()')
        ),

        sa.Column(
            'notice_id',
            sa.Integer(),
            sa.ForeignKey('notices.id', ondelete="CASCADE"),
            nullable=False
        ),

        sa.Column(
            'version_number',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'introduction',
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            'facts_summary',
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            'legal_position',
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            'section_reference',
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            'prayer',
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            'created_at',
            sa.TIMESTAMP(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        )
    )

    op.create_unique_constraint(
        'unique_notice_version',
        'draft_versions',
        ['notice_id', 'version_number']
    )


def downgrade():
    op.drop_table('draft_versions')
