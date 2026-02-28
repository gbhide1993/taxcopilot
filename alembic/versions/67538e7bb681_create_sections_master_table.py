"""create sections_master table

Revision ID: 67538e7bb681
Revises: c2180134ee2c
Create Date: 2026-02-19 14:25:24.342499

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67538e7bb681'
down_revision: Union[str, Sequence[str], None] = 'c2180134ee2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Enable pgcrypto for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    op.create_table(
        'sections_master',

        sa.Column('id', postgresql.UUID(as_uuid=True),
                  server_default=sa.text('gen_random_uuid()'),
                  nullable=False),

        sa.Column('act_name', sa.Text(), nullable=False),
        sa.Column('section_number', sa.Text(), nullable=False),

        sa.Column('heading', sa.Text(), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),

        sa.Column('penalty_flag', sa.Boolean(),
                  nullable=False, server_default='false'),

        sa.Column('severity_level', sa.SmallInteger(),
                  nullable=False, server_default='1'),

        sa.Column('annexure_template', postgresql.JSONB(), nullable=True),

        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=sa.text('CURRENT_TIMESTAMP'),
                  nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('act_name', 'section_number',
                            name='unique_act_section')
    )

    # Check constraint for severity range
    op.create_check_constraint(
        'check_severity_level',
        'sections_master',
        'severity_level BETWEEN 1 AND 5'
    )

    # Index for faster lookup
    op.create_index(
        'idx_sections_act_section',
        'sections_master',
        ['act_name', 'section_number']
    )

    op.create_index(
        'idx_sections_penalty_flag',
        'sections_master',
        ['penalty_flag']
    )


def downgrade():
    op.drop_index('idx_sections_penalty_flag',
                  table_name='sections_master')
    op.drop_index('idx_sections_act_section',
                  table_name='sections_master')

    op.drop_constraint('check_severity_level',
                       'sections_master',
                       type_='check')

    op.drop_table('sections_master')
