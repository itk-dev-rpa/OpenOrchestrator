"""Database revision ${repr(up_revision)}: ${message}"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# pylint: disable=invalid-name
# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade the database."""
    ${upgrades if upgrades else "pass"}
