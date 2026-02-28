"""standardize section_number to section_reference across project

Revision ID: 7e91925a42ca
Revises: 04c05b2b96ef
Create Date: 2026-02-25 05:47:31.196425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e91925a42ca'
down_revision: Union[str, Sequence[str], None] = '04c05b2b96ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():

    # Rename in sections_master
    op.alter_column(
        "document_chunks",
        "section_number",
        new_column_name="section_reference"
    )

    # Rename in notices
    op.alter_column(
        "notices",
        "section_number",
        new_column_name="section_reference"
    )

    


def downgrade():

    op.alter_column(
        "document_chunks",
        "section_reference",
        new_column_name="section_number"
    )

    op.alter_column(
        "notices",
        "section_reference",
        new_column_name="section_number"
    )
