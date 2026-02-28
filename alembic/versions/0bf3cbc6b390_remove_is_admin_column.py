"""remove is_admin column

Revision ID: 0bf3cbc6b390
Revises: f95d824b3c51
Create Date: 2026-02-15 10:01:27.609509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bf3cbc6b390'
down_revision: Union[str, Sequence[str], None] = 'f95d824b3c51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column("users", "is_admin")

def downgrade():
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=True)
    )