"""add branding fields to firms

Revision ID: 0d6d89a92bdc
Revises: 7f96171790ac
Create Date: 2026-02-20 11:17:36.018999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d6d89a92bdc'
down_revision: Union[str, Sequence[str], None] = '7f96171790ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column('firms', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('firms', sa.Column('email', sa.String(), nullable=True))
    op.add_column('firms', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('firms', sa.Column('signature_name', sa.String(), nullable=True))
    op.add_column('firms', sa.Column('signature_designation', sa.String(), nullable=True))

def downgrade():

    op.drop_column('firms', 'signature_designation')
    op.drop_column('firms', 'signature_name')
    op.drop_column('firms', 'phone')
    op.drop_column('firms', 'email')
    op.drop_column('firms', 'address')