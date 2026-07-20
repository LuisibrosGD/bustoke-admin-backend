"""add admin_terminal role and id_terminal column to usuarios

Tercer nivel de RBAC: un usuario admin_terminal queda restringido a un
solo terminal dentro de su agencia (ver app/dependencies.py,
resolve_terminal_scope). id_terminal es nullable porque solo aplica a
ese rol.

Revision ID: 005_admin_terminal_role
Revises: 004_pagos_metodo_pago
Create Date: 2026-07-20 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005_admin_terminal_role"
down_revision: Union[str, None] = "004_pagos_metodo_pago"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No se puede usar el valor nuevo del enum dentro de la misma
    # transacción en la que se agrega (limitación de Postgres) — esta
    # migración solo agrega el valor, nunca lo usa/inserta.
    op.execute("ALTER TYPE rol_usuario ADD VALUE IF NOT EXISTS 'admin_terminal'")

    op.add_column(
        "usuarios",
        sa.Column(
            "id_terminal",
            sa.Integer(),
            sa.ForeignKey("terminales.id_terminal"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "id_terminal")
    # Postgres no soporta DROP VALUE de un enum de forma nativa. Revertir
    # 'admin_terminal' requeriría recrear el tipo completo (crear uno
    # nuevo sin ese valor, migrar la columna, borrar el viejo, renombrar)
    # y no se implementa aquí — si hace falta revertir, hacerlo a mano.
