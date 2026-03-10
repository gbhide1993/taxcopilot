"""rename section_number to section_reference

Revision ID: 04c05b2b96ef
Revises: fe5290256dec
Create Date: 2026-02-22 18:05:19.363559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04c05b2b96ef'
down_revision: Union[str, Sequence[str], None] = 'fe5290256dec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.alter_column(
        "sections_master",
        "section_number",
        new_column_name="section_reference"
    )


def downgrade():
    op.alter_column(
        "sections_master",
        "section_reference",
        new_column_name="section_number"
    )