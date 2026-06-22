"""add notificaciones and historial_cambios_soporte tables

Revision ID: 002_notificaciones_soporte
Revises: 001_initial
Create Date: 2026-06-21 20:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_notificaciones_soporte"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notificaciones",
        sa.Column("id_notificacion", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("referencia_tipo", sa.String(length=30), nullable=True),
        sa.Column("referencia_id", sa.Integer(), nullable=True),
        sa.Column("leida", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuarios.id_usuario"], ),
        sa.PrimaryKeyConstraint("id_notificacion"),
    )
    op.create_table(
        "historial_cambios_soporte",
        sa.Column("id_historial", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_ticket", sa.Integer(), nullable=False),
        sa.Column("campo", sa.String(length=30), nullable=False),
        sa.Column("valor_anterior", sa.String(length=50), nullable=True),
        sa.Column("valor_nuevo", sa.String(length=50), nullable=False),
        sa.Column("id_usuario_modifica", sa.Integer(), nullable=True),
        sa.Column("fecha_cambio", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["id_ticket"], ["tickets_soporte.id_ticket_soporte"], ),
        sa.ForeignKeyConstraint(["id_usuario_modifica"], ["usuarios.id_usuario"], ),
        sa.PrimaryKeyConstraint("id_historial"),
    )


def downgrade() -> None:
    op.drop_table("historial_cambios_soporte")
    op.drop_table("notificaciones")
