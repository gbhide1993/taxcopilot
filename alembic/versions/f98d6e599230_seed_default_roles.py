"""seed default roles

Revision ID: f98d6e599230
Revises: c85b7d5018ca
Create Date: 2026-02-15 12:59:12.623097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f98d6e599230'
down_revision: Union[str, Sequence[str], None] = 'c85b7d5018ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("name", sa.String),
            sa.column("description", sa.Text),
        ),
        [
            {"name": "ADMIN", "description": "Full system access"},
            {"name": "SENIOR_CA", "description": "Review and approve drafts"},
            {"name": "JUNIOR_CA", "description": "Draft and manage clients"},
            {"name": "ARTICLE", "description": "Limited drafting access"},
            {"name": "DATA_ENTRY", "description": "Upload documents only"},
        ],
    )

def downgrade():
    op.execute("DELETE FROM roles")