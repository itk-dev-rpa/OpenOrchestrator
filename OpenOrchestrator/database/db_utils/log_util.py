"""Database access functions for log entries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy import func as alc_func

from OpenOrchestrator.database.db_util import _get_session
from OpenOrchestrator.database.logs import Log, LogLevel
from OpenOrchestrator.database.truncated_string import truncate_message


# pylint: disable=too-many-positional-arguments
def get_logs(offset: int, limit: int,
             from_date: datetime | None = None, to_date: datetime | None = None,
             process_name: str | None = None, log_level: LogLevel | None = None,
             job_id: str | UUID | None = None,
             order_by: str | None = None, order_desc: bool = True,
             include_count: bool = False) -> tuple[Log, ...] | tuple[tuple[Log, ...], int]:
    """Get the logs from the database using filters and pagination.

    Args:
        offset: The index of the first log to get.
        limit: The number of logs to get.
        from_date: The datetime where the log time must be at or after. If none the filter is disabled.
        to_date: The datetime where the log time must be at or earlier. If none the filter is disabled.
        process_name: The process name to filter on. If none the filter is disabled.
        log_level: The log level to filter on. If none the filter is disabled.
        job_id: The job ID to filter on. If none the filter is disabled.
        order_by: Column to order the result by. If None, will use log_time.
        order_desc: Should result be in descending order. Defaults to True.
        include_count: Return a tuple with results as well as the total count of logs without limit applied.

    Returns:
        A tuple of logs matching the given filters, or — if ``include_count`` —
        a tuple with the logs tuple and the total count.
    """
    if isinstance(job_id, str):
        job_id = UUID(job_id)

    def _apply_filters(_query):
        if from_date:
            _query = _query.where(Log.log_time >= from_date)
        if to_date:
            _query = _query.where(Log.log_time <= to_date)
        if process_name:
            _query = _query.where(Log.process_name == process_name)
        if log_level:
            _query = _query.where(Log.log_level == log_level)
        if job_id:
            _query = _query.where(Log.job_id == job_id)
        return _query

    with _get_session() as session:
        query = _apply_filters(select(Log))

        if order_by:
            key = order_by.lower().replace(" ", "_")
            if key == 'level':
                sort_col = Log.log_level
            elif key == 'message':
                sort_col = Log.log_message
            elif key in ('short_job_id', 'job_id', 'full_job_id'):
                sort_col = Log.job_id
            elif key == 'process_name':
                sort_col = Log.process_name
            else:
                sort_col = Log.log_time
        else:
            sort_col = Log.log_time

        query = query.order_by(desc(sort_col) if order_desc else sort_col)
        query = query.offset(offset).select_from(Log)
        if limit > 0:
            query = query.limit(limit)

        result = session.scalars(query).all()
        logs_tuple = tuple(result)

        if include_count:
            count_query = _apply_filters(select(alc_func.count()).select_from(Log))  # pylint: disable=not-callable
            total_count = session.scalar(count_query)
            return logs_tuple, total_count

        return logs_tuple


def create_log(process_name: str, level: LogLevel, job_id: str | UUID | None, message: str) -> None:
    """Create a log entry in the database.

    Args:
        process_name: The name of the process generating the log.
        level: The level of the log.
        job_id: The id of the job this log belongs to (or None).
        message: The message of the log. Long messages are truncated.
    """
    if isinstance(job_id, str):
        job_id = UUID(job_id)

    with _get_session() as session:
        log = Log(
            log_level=level,
            process_name=process_name,
            job_id=job_id,
            log_message=truncate_message(message),
        )
        session.add(log)
        session.commit()


def get_unique_log_process_names() -> tuple[str, ...]:
    """Get a list of unique process names that appear in the logs table."""
    query = (
        select(Log.process_name)
        .distinct()
        .order_by(Log.process_name)
    )

    with _get_session() as session:
        result = session.scalars(query).all()
        return tuple(result)
