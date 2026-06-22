"""initial schema baseline

La base de datos se crea mediante docs/bustoke_bd.sql.
Esta revisión es la línea base para que Alembic pueda rastrear cambios futuros.
Ejecutar: alembic stamp head
"""

from typing import Sequence, Union

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
