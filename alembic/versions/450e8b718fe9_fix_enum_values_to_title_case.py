"""fix enum values to title case

Revision ID: 450e8b718fe9
Revises: 7215e405a2a3
Create Date: 2026-08-03 21:14:42.188785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '450e8b718fe9'
down_revision: Union[str, Sequence[str], None] = '7215e405a2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cambiar la columna a texto temporalmente
    op.execute("ALTER TABLE presupuestos ALTER COLUMN estado TYPE text")
    op.execute("DROP TYPE estadopresupuesto")

    # 2. Actualizar los valores existentes a title case
    op.execute(
        "UPDATE presupuestos SET estado = 'Borrador' WHERE estado = 'BORRADOR'")
    op.execute(
        "UPDATE presupuestos SET estado = 'Enviado' WHERE estado = 'ENVIADO'")
    op.execute(
        "UPDATE presupuestos SET estado = 'Aprobado' WHERE estado = 'ACEPTADO'")
    op.execute(
        "UPDATE presupuestos SET estado = 'Rechazado' WHERE estado = 'RECHAZADO'")

    # 3. Crear el nuevo enum y reconvertir
    op.execute(
        "CREATE TYPE estadopresupuesto AS ENUM ('Borrador', 'Enviado', 'En Revisión', 'Aprobado', 'Rechazado')")
    op.execute(
        "ALTER TABLE presupuestos ALTER COLUMN estado TYPE estadopresupuesto USING estado::estadopresupuesto")


def downgrade() -> None:
    """Downgrade schema."""
    pass
