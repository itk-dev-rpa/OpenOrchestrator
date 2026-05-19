"""Database engine and session management for OpenOrchestrator.

This module owns the global engine handle and provides `_get_session()`
to the domain modules. Domain-specific access functions live in:

- `OpenOrchestrator.database.trigger_util`
- `OpenOrchestrator.database.queue_util`
- `OpenOrchestrator.database.job_util`
- `OpenOrchestrator.database.log_util`
- `OpenOrchestrator.database.settings_util` (constants + credentials)
- `OpenOrchestrator.database.scheduler_util`

For backwards compatibility this module re-exports every domain
function under the historical `db_util` namespace, so existing
`db_util.create_log(...)` style calls continue to work. New code
should import directly from the domain module.
"""

from sqlalchemy import Engine, create_engine, text
from sqlalchemy import exc as alc_exc
from sqlalchemy.orm import Session

_connection_engine: Engine | None = None


def connect(conn_string: str) -> bool:
    """Connect to the database using the given connection string.

    Args:
        conn_string: The connection string.

    Returns:
        True if the connection was established.
    """
    global _connection_engine  # pylint: disable=global-statement

    try:
        engine = create_engine(conn_string)
        engine.connect()
        _connection_engine = engine
        return True
    except (alc_exc.InterfaceError, alc_exc.ArgumentError, alc_exc.OperationalError):
        _connection_engine = None

    return False


def disconnect() -> None:
    """Disconnect from the database."""
    global _connection_engine  # pylint: disable=global-statement
    if _connection_engine:
        _connection_engine.dispose()
    _connection_engine = None


def is_connected() -> bool:
    """Check if the database is connected."""
    return _connection_engine is not None


def check_database_revision() -> bool:
    """Check that the connected database is on the expected Alembic revision."""
    try:
        with _get_session() as session:
            version = session.execute(text(
                """SELECT version_num FROM alembic_version"""
            )).scalar()
    except alc_exc.ProgrammingError:
        return False

    return version == "1c87ed320c78"


def _get_session() -> Session:
    """Return a session for the connected database.

    Raises:
        RuntimeError: If there's no connected database.
    """
    if not _connection_engine:
        raise RuntimeError("Not connected to database.")

    return Session(_connection_engine)


def get_conn_string() -> str:
    """Return the connection string of the active engine."""
    if not _connection_engine:
        raise RuntimeError("Not connected to database.")

    return str(_connection_engine.url)


# ---------------------------------------------------------------------------
# Backwards-compatibility re-exports.
#
# These imports MUST be at the bottom of the file so the engine helpers above
# are fully defined before the domain modules import ``_get_session`` from
# here (the resulting circular import resolves cleanly only in this order).
# Keep this section in sync when adding new domain functions.
# ---------------------------------------------------------------------------

# pylint: disable=wrong-import-position,unused-import,cyclic-import
from OpenOrchestrator.database.trigger_util import (  # noqa: E402,F401
    get_trigger,
    get_all_triggers,
    update_trigger,
    get_scheduled_triggers,
    get_single_triggers,
    get_queue_triggers,
    delete_trigger,
    create_single_trigger,
    create_scheduled_trigger,
    create_queue_trigger,
    begin_single_trigger,
    get_pending_single_triggers,
    get_pending_scheduled_triggers,
    begin_scheduled_trigger,
    get_pending_queue_triggers,
    begin_queue_trigger,
    set_trigger_status,
)
from OpenOrchestrator.database.queue_util import (  # noqa: E402,F401
    create_queue_element,
    bulk_create_queue_elements,
    get_next_queue_element,
    get_queue_elements,
    get_queue_element,
    update_queue_element,
    get_queue_count,
    set_queue_element_status,
    delete_queue_element,
)
from OpenOrchestrator.database.job_util import (  # noqa: E402,F401
    get_jobs,
    start_job,
    set_job_status,
    get_job,
)
from OpenOrchestrator.database.log_util import (  # noqa: E402,F401
    get_logs,
    create_log,
    get_unique_log_process_names,
)
from OpenOrchestrator.database.settings_util import (  # noqa: E402,F401
    get_constant,
    get_constants,
    create_constant,
    update_constant,
    delete_constant,
    get_credential,
    get_credentials,
    create_credential,
    update_credential,
    delete_credential,
)
from OpenOrchestrator.database.scheduler_util import (  # noqa: E402,F401
    get_schedulers,
    send_ping_from_scheduler,
    start_trigger_from_machine,
)
