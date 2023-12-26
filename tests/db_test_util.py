"""This module contains database utility functions used in testing."""

from datetime import datetime, timedelta

from OpenOrchestrator.database import db_util, logs, triggers, constants, queues


def drop_all_tables():
    """Drop all ORM tables from the database."""
    engine = db_util._connection_engine  # pylint: disable=protected-access
    logs.Base.metadata.drop_all(engine)
    triggers.Base.metadata.drop_all(engine)
    constants.Base.metadata.drop_all(engine)
    queues.Base.metadata.drop_all(engine)


def reset_triggers():
    """Delete all triggers in the database and create a new of each."""
    for t in db_util.get_all_triggers():
        db_util.delete_trigger(t.id)

    if len(db_util.get_all_triggers()) != 0:
        raise RuntimeError("Not all triggers were deleted.")

    next_run = datetime.now() - timedelta(seconds=2)
    db_util.create_single_trigger("Single", "Process1", next_run, "Path", "Args", False, False)
    db_util.create_scheduled_trigger("Scheduled", "Process1", "0 0 * * *", next_run, "Path", "Args", False, False)
    db_util.create_queue_trigger("Queue", "Process1", "Trigger Queue", "Path", "Args", False, False, 2)
