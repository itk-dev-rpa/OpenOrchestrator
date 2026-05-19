"""Database access functions for queue elements."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, insert, desc
from sqlalchemy import func as alc_func

from OpenOrchestrator.database.db_util import _get_session
from OpenOrchestrator.database.exceptions import QueueElementNotFoundError
from OpenOrchestrator.database.queues import QueueElement, QueueStatus


def create_queue_element(queue_name: str, reference: str | None = None, data: str | None = None, created_by: str | None = None) -> QueueElement:
    """Adds a queue element to the given queue.

    Args:
        queue_name: The name of the queue to add the element to.
        reference (optional): The reference of the queue element.
        data (optional): The data of the queue element.
        created_by (optional): The name of the creator of the queue element.

    Returns:
        QueueElement: The created queue element.
    """
    with _get_session() as session:
        q_element = QueueElement(
            queue_name=queue_name,
            data=data,
            reference=reference,
            created_by=created_by,
        )
        session.add(q_element)
        session.commit()
        session.refresh(q_element)

    return q_element


def bulk_create_queue_elements(queue_name: str, references: tuple[str | None, ...], data: tuple[str | None, ...], created_by: str | None = None) -> None:
    """Insert multiple queue elements into a queue in an optimized manner.
    The lengths of both 'references' and 'data' must be equal to the number of elements to insert.

    Args:
        queue_name: The name of the queue to insert into.
        references: A tuple of reference strings for each queue element.
        data: A tuple of data strings for each queue element.
        created_by (Optional): The name of the creator of the queue elements.

    Raises:
        ValueError: If either 'references' or 'data' are empty, or if they are not equal in length.
    """
    if len(references) == 0:
        raise ValueError("No reference strings were given.")

    if len(data) == 0:
        raise ValueError("No data strings were given.")

    if len(references) != len(data):
        raise ValueError(f"The number of references and data strings don't match: {len(references)} != {len(data)}.")

    q_elements = (
        {
            "queue_name": queue_name,
            "reference": ref,
            "data": dat,
            "created_by": created_by,
        }
        for ref, dat in zip(references, data)
    )

    with _get_session() as session:
        session.execute(insert(QueueElement), q_elements)  # type: ignore
        session.commit()


def get_next_queue_element(queue_name: str, reference: str | None = None, set_status: bool = True) -> QueueElement | None:
    """Gets the next queue element from the given queue that has the status 'new'.

    Args:
        queue_name: The name of the queue to retrieve from.
        reference (optional): The reference to filter on. If None the filter is disabled.
        set_status (optional): If true the queue element's status is set to 'in progress' and the start time is noted.

    Returns:
        QueueElement | None: The next queue element in the queue if any.
    """
    with _get_session() as session:
        query = (
            select(QueueElement)
            .where(QueueElement.queue_name == queue_name)
            .where(QueueElement.status == QueueStatus.NEW)
            .order_by(QueueElement.created_date)
            .limit(1)
        )

        if reference is not None:
            query = query.where(QueueElement.reference == reference)

        q_element = session.scalar(query)

        if q_element and set_status:
            q_element.status = QueueStatus.IN_PROGRESS
            q_element.start_date = datetime.now()
            session.commit()
            session.refresh(q_element)

        return q_element


# pylint: disable=too-many-positional-arguments
def get_queue_elements(queue_name: str, reference: str | None = None, status: QueueStatus | None = None,
                       from_date: datetime | None = None, to_date: datetime | None = None,
                       offset: int = 0, limit: int | None = 100, search_term: str | None = None,
                       order_by: str | None = None, order_desc: bool = False, include_count: bool = False) -> tuple[QueueElement, ...] | tuple[tuple[QueueElement, ...], int]:
    """Get multiple queue elements from a queue. The elements are ordered by created_date.

    Args:
        queue_name: The queue to get elements from.
        reference (optional): The reference to filter by. If None the filter is disabled.
        status (optional): The status to filter by if any. If None the filter is disabled.
        offset (optional): The number of queue elements to skip.
        limit (optional): The number of queue elements to get.
        order_by (optional): Column to order the result by. If None, will use created_date.
        order_desc (optional): Should result be in descending order, only used with order_by.
        include_count (optional): Return a tuple with results as well as the total count of elements without limit applied.

    Returns:
        A tuple of queue elements, or — if include_count — a tuple with a tuple of queue elements and the total count.
    """
    def _apply_filters(query):
        query = query.where(QueueElement.queue_name == queue_name)

        if from_date is not None:
            query = query.where(QueueElement.created_date >= from_date)
        if to_date is not None:
            query = query.where(QueueElement.created_date <= to_date)
        if reference is not None:
            query = query.where(QueueElement.reference == reference)
        if status is not None:
            query = query.where(QueueElement.status == status)
        if search_term is not None:
            query = query.where(QueueElement.reference.startswith(search_term) |
                                QueueElement.data.like(f"%{search_term}%") |
                                QueueElement.message.like(f"%{search_term}%"))
        return query

    with _get_session() as session:
        query = _apply_filters(select(QueueElement))

        if order_by:
            order_column = getattr(QueueElement, order_by, 'created_date')
        else:
            order_column = 'created_date'
        query = query.order_by(desc(order_column) if order_desc else order_column)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = session.scalars(query).all()
        elements_tuple = tuple(result)

        if include_count:
            count_query = _apply_filters(select(alc_func.count()))  # pylint: disable=not-callable
            total_count = session.scalar(count_query)
            return elements_tuple, total_count

        return elements_tuple


def get_queue_element(element_id: UUID | str) -> QueueElement:
    """Get a specific QueueElement by id.

    Args:
        element_id: ID of QueueElement to get.

    Returns:
        QueueElement with the requested ID.

    Raises:
        QueueElementNotFoundError: If no element with the given id exists.
    """
    if isinstance(element_id, str):
        element_id = UUID(element_id)
    with _get_session() as session:
        q_element = session.get(QueueElement, element_id)
        if not q_element:
            raise QueueElementNotFoundError("No queue element with the given id was found.")
        return q_element


# pylint: disable=too-many-positional-arguments
def update_queue_element(element_id: str, reference: str | None = None, status: QueueStatus | None = None, data: str | None = None, message: str | None = None,
                         created_by: str | None = None, created_date: datetime | None = None, start_date: datetime | None = None, end_date: datetime | None = None):
    """Update fields of specific QueueElement. Fields with value None will not be updated.

    Args:
        element_id: ID of QueueElement to update.
        reference: New value for reference. Defaults to None.
        status: New value for status. Defaults to None.
        data: New value for data. Defaults to None.
        message: New value for message. Defaults to None.
        created_by: New value for created_by. Defaults to None.
        created_date: New value for created_date. Defaults to None.
        start_date: New value for start_date. Defaults to None.
        end_date: New value for end_date. Defaults to None.
    """
    with _get_session() as session:
        query = select(QueueElement).where(QueueElement.id == element_id)
        q_element: QueueElement = session.scalar(query)

        if q_element:
            if reference:
                q_element.reference = reference
            if status:
                q_element.status = status
            if data:
                q_element.data = data
            if message:
                q_element.message = message
            if created_date:
                q_element.created_date = created_date
            if start_date:
                q_element.start_date = start_date
            if end_date:
                q_element.end_date = end_date
            if created_by:
                q_element.created_by = created_by
            session.commit()
            session.refresh(q_element)


def get_queue_count() -> dict[str, dict[QueueStatus, int]]:
    """Count the number of queue elements of each status for every queue.

    Returns:
        A dict for each queue with the count for each status. E.g. result[queue_name][status] => count.
    """
    with _get_session() as session:
        query = (
            select(QueueElement.queue_name, QueueElement.status, alc_func.count())  # pylint: disable=not-callable
            .group_by(QueueElement.queue_name)
            .group_by(QueueElement.status)
        )
        rows = session.execute(query)
        rows = tuple(rows)

    result = {}
    for queue_name, status, count in rows:
        if queue_name not in result:
            result[queue_name] = {}
        result[queue_name][status] = count

    return result


def set_queue_element_status(element_id: UUID | str, status: QueueStatus, message: str | None = None) -> None:
    """Set the status of a queue element.
    If the new status is 'in progress' the start date is noted.
    If the new status is 'Done', 'Failed' or 'Abandoned' the end date is noted.

    Args:
        element_id: The id of the queue element to change status on.
        status: The new status of the queue element.
        message (Optional): The message to attach to the queue element. This overrides any existing messages.
    """
    if isinstance(element_id, str):
        element_id = UUID(element_id)

    with _get_session() as session:
        q_element = session.get(QueueElement, element_id)

        if not q_element:
            raise QueueElementNotFoundError("No queue element with the given id was found.")

        q_element.status = status

        if message is not None:
            q_element.message = message

        match status:
            case QueueStatus.IN_PROGRESS:
                q_element.start_date = datetime.now()
            case QueueStatus.DONE | QueueStatus.FAILED | QueueStatus.ABANDONED:
                q_element.end_date = datetime.now()
            case _:
                pass

        session.commit()


def delete_queue_element(element_id: UUID | str) -> None:
    """Delete a queue element from the database.

    Args:
        element_id: The id of the queue element.
    """
    with _get_session() as session:
        q_element = session.get(QueueElement, element_id)
        session.delete(q_element)
        session.commit()
