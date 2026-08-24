"""fix enum values to title case

Revision ID: 98336ebf5e26
Revises: c8a7e9da0dca
Create Date: 2026-08-03 21:09:43.050988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98336ebf5e26'
down_revision: Union[str, Sequence[str], None] = 'c8a7e9da0dca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
