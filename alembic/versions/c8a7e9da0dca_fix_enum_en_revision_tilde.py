"""fix enum en revision tilde

Revision ID: c8a7e9da0dca
Revises: ad6b0dafc7fd
Create Date: 2026-08-03 21:03:54.365005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8a7e9da0dca'
down_revision: Union[str, Sequence[str], None] = 'ad6b0dafc7fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE estadopresupuesto RENAME TO estadopresupuesto_old")
    op.execute(
        "CREATE TYPE estadopresupuesto AS ENUM ('Borrador', 'Enviado', 'En Revisión', 'Aprobado', 'Rechazado')")
    op.execute(
        "ALTER TABLE presupuestos ALTER COLUMN estado TYPE estadopresupuesto USING estado::text::estadopresupuesto")
    op.execute("DROP TYPE estadopresupuesto_old")


def downgrade() -> None:
    op.execute("ALTER TYPE estadopresupuesto RENAME TO estadopresupuesto_old")
    op.execute(
        "CREATE TYPE estadopresupuesto AS ENUM ('BORRADOR', 'ENVIADO', 'ACEPTADO', 'RECHAZADO')")
    op.execute(
        "ALTER TABLE presupuestos ALTER COLUMN estado TYPE estadopresupuesto USING estado::text::estadopresupuesto")
    op.execute("DROP TYPE estadopresupuesto_old")
