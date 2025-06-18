"""Database revision '526b6edac328': Add schedulers table"""

from alembic import op
import sqlalchemy as sa


# pylint: disable=invalid-name
# revision identifiers, used by Alembic.
revision: str = '526b6edac328'
down_revision = 'b67b7649b282'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade the database."""
    op.create_table(
        'Schedulers',
        sa.Column('machine_name', sa.String(length=100), nullable=False, primary_key=True),
        sa.Column('last_update', sa.DateTime(), nullable=False),
        sa.Column('latest_trigger', sa.String(length=100), nullable=True),
        sa.Column('latest_trigger_time', sa.DateTime(), nullable=True),
    )
