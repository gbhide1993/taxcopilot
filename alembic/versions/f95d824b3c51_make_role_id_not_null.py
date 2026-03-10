"""make role_id not null

Revision ID: f95d824b3c51
Revises: 6fa5b963139f
Create Date: 2026-02-15 09:59:15.993826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f95d824b3c51'
down_revision: Union[str, Sequence[str], None] = '6fa5b963139f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("users", "role_id", nullable=False)

def downgrade():
    op.alter_column("users", "role_id", nullable=True)
