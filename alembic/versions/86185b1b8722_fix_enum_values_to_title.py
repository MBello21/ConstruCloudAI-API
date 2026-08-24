"""fix enum values to title

Revision ID: 86185b1b8722
Revises: 450e8b718fe9
Create Date: 2026-08-03 21:15:43.106754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86185b1b8722'
down_revision: Union[str, Sequence[str], None] = '450e8b718fe9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
