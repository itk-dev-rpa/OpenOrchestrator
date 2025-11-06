"""Database revision '90d46abd44a3': Added trigger priority"""

from alembic import op
import sqlalchemy as sa


# pylint: disable=invalid-name
# revision identifiers, used by Alembic.
revision: str = '90d46abd44a3'
down_revision = '526b6edac328'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade the database."""
    op.add_column('Triggers', sa.Column('scheduler_whitelist', sa.String(length=250), nullable=False, server_default=sa.text("'[]'")))
    op.add_column('Triggers', sa.Column('priority', sa.Integer(), nullable=False, server_default=sa.text("0")))
