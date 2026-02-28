"""create admin role

Revision ID: 6fa5b963139f
Revises: f98d6e599230
Create Date: 2026-02-15 07:33:20.606873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fa5b963139f'
down_revision: Union[str, Sequence[str], None] = 'f98d6e599230'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        INSERT INTO roles (name, description)
        SELECT 'ADMIN', 'Full system access'
        WHERE NOT EXISTS (
            SELECT 1 FROM roles WHERE name = 'ADMIN'
        )
    """)

def downgrade():
    op.execute("""
        DELETE FROM roles WHERE name = 'ADMIN'
    """)