"""Add title column to transactions

Revision ID: e5812d3d92b7
Revises: dcf9bbfd13c0
Create Date: 2025-08-06 16:47:14.409555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5812d3d92b7'
down_revision: Union[str, Sequence[str], None] = 'dcf9bbfd13c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('transactions', sa.Column('title', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'title')

