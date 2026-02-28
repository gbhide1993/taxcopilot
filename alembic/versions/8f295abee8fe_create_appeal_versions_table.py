"""create appeal_versions table

Revision ID: 8f295abee8fe
Revises: 0d6d89a92bdc
Create Date: 2026-02-20 12:10:09.975335

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f295abee8fe'
down_revision: Union[str, Sequence[str], None] = '0d6d89a92bdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():

    op.create_table(
        "appeal_versions",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),

        sa.Column(
            "notice_id",
            sa.Integer(),
            sa.ForeignKey("notices.id", ondelete="CASCADE"),
            nullable=False
        ),

        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "background",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "grounds",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "prayer",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        )
    )

    op.create_unique_constraint(
        "unique_notice_appeal_version",
        "appeal_versions",
        ["notice_id", "version_number"]
    )


def downgrade():
    op.drop_table("appeal_versions")