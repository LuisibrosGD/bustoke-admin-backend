"""drop chk_formato_asiento check constraint on asientos

El editor de plano de asientos ahora permite numeración libre (según
mapas reales de buses: "4", "17", "99"...), no solo el formato viejo
letra+dígito-piso ("A1-1"). Nada más en el código depende de ese
formato (es solo una etiqueta de display), así que se quita la
restricción en vez de forzar el nuevo diseño a calzar en el viejo
patrón.

Revision ID: 007_quitar_chk_formato_asiento
Revises: 006_amenidades_bus
Create Date: 2026-07-22 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "007_quitar_chk_formato_asiento"
down_revision: Union[str, None] = "006_amenidades_bus"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE asientos DROP CONSTRAINT IF EXISTS chk_formato_asiento")


def downgrade() -> None:
    op.execute(
        "ALTER TABLE asientos ADD CONSTRAINT chk_formato_asiento "
        "CHECK (numero_asiento SIMILAR TO '[A-Z][0-9]-%')"
    )
