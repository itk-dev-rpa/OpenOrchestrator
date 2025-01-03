"""Database revision 'b67b7649b282': Initial"""

from alembic import op
import sqlalchemy as sa


# pylint: disable=invalid-name
# revision identifiers, used by Alembic.
revision: str = 'b67b7649b282'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade the database."""
    op.create_table(
        'Constants',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=1000), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_table(
        'Credentials',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=250), nullable=False),
        sa.Column('password', sa.String(length=1000), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_table(
        'Logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('log_time', sa.DateTime(), nullable=False),
        sa.Column('log_level', sa.Enum('TRACE', 'INFO', 'ERROR', name='loglevel'), nullable=False),
        sa.Column('process_name', sa.String(length=100), nullable=False),
        sa.Column('log_message', sa.String(length=8000), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'Queues',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('queue_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'DONE', 'FAILED', 'ABANDONED', name='queuestatus'), nullable=False),
        sa.Column('data', sa.String(length=2000), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('message', sa.String(length=1000), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Queues_created_date'), 'Queues', ['created_date'], unique=False)
    op.create_index(op.f('ix_Queues_queue_name'), 'Queues', ['queue_name'], unique=False)
    op.create_table(
        'Triggers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('trigger_name', sa.String(length=100), nullable=False),
        sa.Column('process_name', sa.String(length=100), nullable=False),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('process_path', sa.String(length=250), nullable=False),
        sa.Column('process_args', sa.String(length=1000), nullable=True),
        sa.Column('process_status', sa.Enum('IDLE', 'RUNNING', 'FAILED', 'DONE', 'PAUSED', 'PAUSING', name='triggerstatus'), nullable=False),
        sa.Column('is_git_repo', sa.Boolean(), nullable=False),
        sa.Column('is_blocking', sa.Boolean(), nullable=False),
        sa.Column('type', sa.Enum('SINGLE', 'SCHEDULED', 'QUEUE', name='triggertype'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'Queue_Triggers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('queue_name', sa.String(length=200), nullable=False),
        sa.Column('min_batch_size', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['Triggers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'Scheduled_Triggers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('cron_expr', sa.String(length=200), nullable=False),
        sa.Column('next_run', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['Triggers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'Single_Triggers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('next_run', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['Triggers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
