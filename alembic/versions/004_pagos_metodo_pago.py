"""create metodo_pago enum and pagos table

Antes esto se creaba en cada arranque de la app (app/main.py lifespan),
lo que corre el riesgo de una condición de carrera si arrancan varios
workers/réplicas a la vez. Se mueve a una migración normal de Alembic.

Revision ID: 004_pagos_metodo_pago
Revises: 003_estado_checkin
Create Date: 2026-07-06 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "004_pagos_metodo_pago"
down_revision: Union[str, None] = "003_estado_checkin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

metodo_pago_enum = postgresql.ENUM("yape", "plin", "tarjeta", name="metodo_pago", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    metodo_pago_enum.create(bind, checkfirst=True)

    if not sa.inspect(bind).has_table("pagos"):
        op.create_table(
            "pagos",
            sa.Column("id_pago", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("id_boleto", sa.Integer(), nullable=False),
            sa.Column("metodo", metodo_pago_enum, nullable=False),
            sa.Column(
                "estado",
                postgresql.ENUM("pendiente", "completado", "fallido", "reembolsado", name="estado_pago", create_type=False),
                nullable=False,
            ),
            sa.Column("monto", sa.Numeric(10, 2), nullable=False),
            sa.Column("fecha_pago", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.Column("referencia", sa.String(length=100), nullable=True),
            sa.ForeignKeyConstraint(["id_boleto"], ["boletos.id_boleto"]),
            sa.PrimaryKeyConstraint("id_pago"),
        )


def downgrade() -> None:
    op.drop_table("pagos")
    metodo_pago_enum.drop(op.get_bind(), checkfirst=True)
