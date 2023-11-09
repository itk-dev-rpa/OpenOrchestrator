"""The main module of this package. It contains a single class called OrchestratorConnection.
The easiest way to create an OrchestratorConnection object is to call the
class method create_connection_from_args."""

import sys
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.queues import QueueElement, QueueStatus
from OpenOrchestrator.database.logs import LogLevel


class OrchestratorConnection:
    """An OrchestratorConnection is used to easier communicate with
    OpenOrchestrator within a running process. If used in conjuction with
    OpenOrchestrator's Scheduler use orchestrator_connection.create_connection_from_args
    to instead of initializing the object manually.
    """

    def __init__(self, process_name: str, connection_string: str, crypto_key: str, process_arguments: str):
        """

        Args:
            process_name:
            connection_string:
            crypto_key:
            process_arguments:
        """
        self.process_name = process_name
        self.process_arguments = process_arguments
        crypto_util.set_key(crypto_key)
        db_util.connect(connection_string)

    def __repr__(self):
        return f"OrchestratorConnection - Process name: {self.process_name}"

    def log_trace(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'trace'.
        The log is automatically annotated with the current time and name of the process
        Args:
            message: Message to be logged.
        """
        db_util.create_log(self.process_name, LogLevel.TRACE, message)

    def log_info(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'info'.
        The log is automatically annotated with the current time and name of the process
        Args:
        """
        db_util.create_log(self.process_name, LogLevel.INFO, message)

    def log_error(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'error'.
        The log is automatically annotated with the current time and name of the process
        Args:
            message: Message to be logged.
        """
        db_util.create_log(self.process_name, LogLevel.ERROR, message)

    def get_constant(self, constant_name: str) -> str:
        """Get a constant from the Orchestrator with the given name.
        return: The value of the named constant."""
        return db_util.get_constant(constant_name)

    def get_credential(self, credential_name: str) -> tuple[str, str]:
        """Get a credential from the Orchestrator with the given name.
        return: tuple(username, password)
        """
        return db_util.get_credential(credential_name)

    def update_constant(self, constant_name: str, new_value: str) -> None:
        """Update an Orchestrator constant with a new value.
        Raises an error if no constant with the given name exists.
        """
        db_util.update_constant(constant_name, new_value)

    def update_credential(self, credential_name: str, new_username: str, new_password: str) -> None:
        """Update an Orchestrator credential with a new username and password.
        Raises an error if no credential with the given name exists.
        """
        db_util.update_credential(credential_name, new_username, new_password)


    # Methods for creating queue elements

    def create_queue_element(queue_name: str, reference: str = None, data: str = None, created_by: str = None):
        """Adds a queue element to the given queue.

        Args:
            queue_name: The name of the queue to add the element to.
            reference (optional): The reference of the queue element.
            data (optional): The data of the queue element.
            created_by (optional): The name of the creator of the queue element.
        """
        db_util.create_queue_element(queue_name=queue_name, reference=reference, data=data, created_by=created_by)

    def bulk_create_queue_elements(queue_name: str, references: tuple[str], data: tuple[str],
                                   created_by: str = None) -> None:
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
        db_util.bulk_create_queue_elements(queue_name=queue_name, references=references, data=data,
                                           created_by=created_by)

    # Method for reading queue elements

    def get_next_queue_element(queue_name: str, reference: str = None, set_status: bool = True) -> QueueElement | None:
        """Gets the next queue element from the given queue that has the status 'new'.

        Args:
            queue_name: The name of the queue to retrieve from.
            reference (optional): The reference to filter on. If None the filter is disabled.
            set_status (optional): If true the queue element's status is set to 'in progress'
                and the start time is noted.

        Returns:
            QueueElement | None: The next queue element in the queue if any.
        """
        return db_util.get_next_queue_element(queue_name=queue_name, reference=reference, set_status=set_status)

    def get_queue_elements(queue_name: str, reference: str = None, status: QueueStatus = None,
                           offset: int = 0, limit: int = 100) -> tuple[QueueElement]:
        """Get multiple queue elements from a queue. The elements are ordered by created_date.

        Args:
            queue_name: The queue to get elements from.
            reference (optional): The reference to filter by. If None the filter is disabled.
            status (optional): The status to filter by if any. If None the filter is disabled.
            offset: The number of queue elements to skip.
            limit: The number of queue elements to get.

        Returns:
            tuple[QueueElement]: A tuple of queue elements.
        """
        return db_util.get_queue_elements(queue_name=queue_name, reference=reference, status=status,
                                          QueueStatus=QueueStatus, offset=offset, limit=limit)

    # Method for updating status

    def set_queue_element_status(element_id: str, status: QueueStatus, message: str = None) -> None:
        """Set the status of a queue element.
        If the new status is 'in progress' the start date is noted.
        If the new status is 'Done' or 'Failed' the end date is noted.

        Args:
            element_id: The id of the queue element to change status on.
            status: The new status of the queue element.
            message (Optional): The message to attach to the queue element. This overrides any existing messages.
        """
        db_util.set_queue_element_status(element_id=element_id, status=status, message=message)

    # Method for deleting queue element

    def delete_queue_element(element_id: str) -> None:
        """Delete a queue element from the database.

        Args:
            element_id: The id of the queue element.
        """
        db_util.delete_queue_element(element_id)


    @classmethod
    def create_connection_from_args(cls):
        """Create a Connection object using the arguments passed to sys.argv.
        This function is the preferred way to create a connection with OpenOrchestrator's Scheduler"""
        process_name = sys.argv[1]
        connection_string = sys.argv[2]
        crypto_key = sys.argv[3]
        process_arguments = sys.argv[4]
        return OrchestratorConnection(process_name, connection_string, crypto_key, process_arguments)

