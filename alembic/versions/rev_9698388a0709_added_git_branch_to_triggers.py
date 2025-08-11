"""Database revision '9698388a0709': Added git branch to triggers"""

from alembic import op
import sqlalchemy as sa


# pylint: disable=invalid-name
# revision identifiers, used by Alembic.
revision: str = '9698388a0709'
down_revision = '90d46abd44a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade the database."""
    op.add_column('Triggers', sa.Column('git_branch', sa.String(length=100), nullable=True))
