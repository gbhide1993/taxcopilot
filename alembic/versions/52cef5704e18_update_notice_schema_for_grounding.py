"""update notice schema for grounding

Revision ID: 52cef5704e18
Revises: 67538e7bb681
Create Date: 2026-02-19 16:27:27.629005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52cef5704e18'
down_revision: Union[str, Sequence[str], None] = '67538e7bb681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # 1️⃣ Add columns as nullable first
    op.add_column(
        'notices',
        sa.Column('act_name', sa.String(), nullable=True)
    )

    op.add_column(
        'notices',
        sa.Column('section_number', sa.String(), nullable=True)
    )

    # 2️⃣ Populate existing rows with safe default
    op.execute(
        """
        UPDATE notices
        SET act_name = 'Income Tax Act 1961',
            section_number = 'UNKNOWN'
        """
    )

    # 3️⃣ Make columns NOT NULL
    op.alter_column('notices', 'act_name', nullable=False)
    op.alter_column('notices', 'section_number', nullable=False)

    # 4️⃣ Drop old column
    op.drop_column('notices', 'section')



def downgrade():

    # Add section column back
    op.add_column(
        'notices',
        sa.Column('section', sa.String(), nullable=True)
    )

    # Drop new columns
    op.drop_column('notices', 'section_number')
    op.drop_column('notices', 'act_name')
