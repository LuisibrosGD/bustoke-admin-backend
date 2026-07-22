"""create tipo_amenidad enum and amenidades_bus table

Elementos no-asiento del plano del bus (TV, baño, escaleras, cafetera)
que el editor de plantilla de asientos ahora puede colocar en la
grilla, además de asientos y celdas vacías.

Revision ID: 006_amenidades_bus
Revises: 005_admin_terminal_role
Create Date: 2026-07-22 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "006_amenidades_bus"
down_revision: Union[str, None] = "005_admin_terminal_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_amenidad_enum = postgresql.ENUM(
    "tv", "bano", "escaleras", "cafetera", name="tipo_amenidad", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    tipo_amenidad_enum.create(bind, checkfirst=True)

    if not sa.inspect(bind).has_table("amenidades_bus"):
        op.create_table(
            "amenidades_bus",
            sa.Column("id_amenidad", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("id_bus", sa.Integer(), nullable=False),
            sa.Column("tipo", tipo_amenidad_enum, nullable=False),
            sa.Column("piso", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("coord_x", sa.Integer(), nullable=False),
            sa.Column("coord_y", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["id_bus"], ["buses.id_bus"]),
            sa.PrimaryKeyConstraint("id_amenidad"),
        )


def downgrade() -> None:
    op.drop_table("amenidades_bus")
    tipo_amenidad_enum.drop(op.get_bind(), checkfirst=True)
