"""This module contains database utility functions used in testing."""

from datetime import datetime, timedelta
import os

from OpenOrchestrator.database import db_util, base

from OpenOrchestrator.common import crypto_util


def establish_clean_database():
    """Connect to the database, drop all tables and recreate them."""
    db_util.connect(os.environ["CONN_STRING"])
    crypto_util.set_key(crypto_util.generate_key().decode())

    drop_all_tables()
    base.Base.metadata.create_all(db_util._connection_engine)  # pylint: disable=protected-access


def drop_all_tables():
    """Drop all ORM tables from the database."""
    engine = db_util._connection_engine  # pylint: disable=protected-access
    if not engine:
        raise RuntimeError("Not connected to a database.")

    base.Base.metadata.drop_all(engine)


def reset_triggers():
    """Delete all triggers in the database and create a new of each."""
    for t in db_util.get_all_triggers():
        db_util.delete_trigger(t.id)

    if len(db_util.get_all_triggers()) != 0:
        raise RuntimeError("Not all triggers were deleted.")

    next_run = datetime.now() - timedelta(seconds=2)
    db_util.create_single_trigger("Single", "Process1", next_run, "Path", "Args", False, False, 0, "")
    db_util.create_scheduled_trigger("Scheduled", "Process1", "0 0 * * *", next_run, "Path", "Args", False, False, 0, "")
    db_util.create_queue_trigger("Queue", "Process1", "Trigger Queue", "Path", "Args", False, False, 2, 0, "")
