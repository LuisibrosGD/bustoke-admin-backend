"""add estado_checkin column to boletos

Revision ID: 003_estado_checkin
Revises: 002_notificaciones_soporte
Create Date: 2026-06-29 22:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_estado_checkin"
down_revision: Union[str, None] = "002_notificaciones_soporte"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "boletos",
        sa.Column("estado_checkin", sa.String(20), nullable=False, server_default=sa.text("'pendiente'")),
    )


def downgrade() -> None:
    op.drop_column("boletos", "estado_checkin")
