"""enhance sections_master schema for enterprise

Revision ID: fe5290256dec
Revises: 8f295abee8fe
Create Date: 2026-02-22 13:49:09.076669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'fe5290256dec'
down_revision: Union[str, Sequence[str], None] = '8f295abee8fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column(
        "sections_master",
        sa.Column("category", sa.String(), nullable=False, server_default="section")
    )
    op.add_column(
        "sections_master",
        sa.Column("workflow_mapping", sa.String(), nullable=True)
    )
    op.add_column(
        "sections_master",
        sa.Column("exposure_type", sa.String(), nullable=True)
    )
    op.add_column(
        "sections_master",
        sa.Column("related_penalty_reference", sa.String(), nullable=True)
    )
    op.add_column(
        "sections_master",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
