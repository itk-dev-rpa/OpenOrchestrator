"""This module contains a single class called OrchestratorConnection.
The easiest way to create an OrchestratorConnection object is to call the
class method create_connection_from_args."""

import sys
from datetime import datetime

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.queues import QueueElement, QueueStatus
from OpenOrchestrator.database.logs import LogLevel
from OpenOrchestrator.database.constants import Constant, Credential
from OpenOrchestrator.database.triggers import TriggerStatus


class OrchestratorConnection:
    """An OrchestratorConnection is used to easier communicate with
    OpenOrchestrator within a running process. If used in conjunction with
    OpenOrchestrator's Scheduler use orchestrator_connection.create_connection_from_args
    to instead of initializing the object manually.
    """

    def __init__(self, process_name: str, connection_string: str, crypto_key: str, process_arguments: str, trigger_id: str):
        """
        Args:
            process_name: A human friendly tag to identify the process.
            connection_string: An ODBC connection to the OpenOrchestrator database.
            crypto_key: Secret key for decrypting database content.
            process_arguments (optional): Arguments for the controlling how the process should run.
            trigger_id: ID of trigger used to start this process.
        """
        self.process_name = process_name
        self.process_arguments = process_arguments
        self.trigger_id = trigger_id
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
            message: Message to be logged.
        """
        db_util.create_log(self.process_name, LogLevel.INFO, message)

    def log_error(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'error'.
        The log is automatically annotated with the current time and name of the process
        Args:
            message: Message to be logged.
        """
        db_util.create_log(self.process_name, LogLevel.ERROR, message)

    def get_constant(self, constant_name: str) -> Constant:
        """Get a constant from the database.

        Args:
            name: The name of the constant.

        Returns:
            Constant: The constant with the given name.

        Raises:
            ValueError: If no constant with the given name exists.
        """
        return db_util.get_constant(constant_name)

    def get_credential(self, credential_name: str) -> Credential:
        """Get a credential from the database.
        The password of the credential is decrypted.

        Args:
            name: The name of the credential.

        Returns:
            Credential: The credential with the given name.

        Raises:
            ValueError: If no credential with the given name exists.
        """
        return db_util.get_credential(credential_name)

    def update_constant(self, constant_name: str, new_value: str) -> None:
        """Updates an existing constant with a new value.

        Args:
            name: The name of the constant to update.
            new_value: The new value of the constant.
        """
        db_util.update_constant(constant_name, new_value)

    def update_credential(self, credential_name: str, new_username: str, new_password: str) -> None:
        """Updates an existing credential with a new value.

        Args:
            name: The name of the credential to update.
            new_username: The new username of the credential.
            new_password: The new password of the credential.
        """
        db_util.update_credential(credential_name, new_username, new_password)

    def create_queue_element(self, queue_name: str, reference: str | None = None, data: str | None = None, created_by: str | None = None) -> QueueElement:
        """Adds a queue element to the given queue.

        Args:
            queue_name: The name of the queue to add the element to.
            reference (optional): The reference of the queue element.
            data (optional): The data of the queue element.
            created_by (optional): The name of the creator of the queue element.

        Returns:
            QueueElement: The created queue element.
        """
        return db_util.create_queue_element(queue_name, reference, data, created_by)

    def bulk_create_queue_elements(self, queue_name: str, references: tuple[str | None, ...], data: tuple[str | None, ...],
                                   created_by: str | None = None) -> None:
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
        db_util.bulk_create_queue_elements(queue_name, references, data, created_by)

    def get_next_queue_element(self, queue_name: str, reference: str | None = None,
                               set_status: bool = True) -> QueueElement | None:
        """Gets the next queue element from the given queue that has the status 'new'.

        Args:
            queue_name: The name of the queue to retrieve from.
            reference (optional): The reference to filter on. If None the filter is disabled.
            set_status (optional): If true the queue element's status is set to 'in progress'
                and the start time is noted.

        Returns:
            QueueElement | None: The next queue element in the queue if any.
        """
        return db_util.get_next_queue_element(queue_name, reference, set_status)

    def get_queue_elements(self, queue_name: str, reference: str | None = None, status: QueueStatus | None = None,
                           offset: int = 0, limit: int = 100, from_date: datetime | None = None, to_date: datetime | None = None) -> tuple[QueueElement, ...]:
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
        return db_util.get_queue_elements(queue_name, reference, status, from_date, to_date, offset, limit)

    def set_queue_element_status(self, element_id: str, status: QueueStatus, message: str | None = None) -> None:
        """Set the status of a queue element.
        If the new status is 'in progress' the start date is noted.
        If the new status is 'Done', 'Failed' or 'Abandoned' the end date is noted.

        Args:
            element_id: The id of the queue element to change status on.
            status: The new status of the queue element.
            message (Optional): The message to attach to the queue element. This overrides any existing messages.
        """
        db_util.set_queue_element_status(element_id, status, message)

    def delete_queue_element(self, element_id: str) -> None:
        """Delete a queue element from the database.

        Args:
            element_id: The id of the queue element.
        """
        db_util.delete_queue_element(element_id)

    def is_trigger_pausing(self) -> bool:
        """Check if my trigger is pausing.

        Returns:
            bool: Whether or not the trigger used to start this process is pausing.
        """
        my_trigger = db_util.get_trigger(self.trigger_id)
        return my_trigger.process_status in (TriggerStatus.PAUSING, TriggerStatus.PAUSED)

    def pause_my_trigger(self) -> None:
        """Pause the trigger used to start this process."""
        db_util.set_trigger_status(self.trigger_id, TriggerStatus.PAUSING)

    @classmethod
    def create_connection_from_args(cls):
        """Create a Connection object using the arguments passed to sys.argv.
        This function is the preferred way to create a connection with OpenOrchestrator's Scheduler"""
        process_name = sys.argv[1]
        connection_string = sys.argv[2]
        crypto_key = sys.argv[3]
        process_arguments = sys.argv[4]
        trigger_id = sys.argv[5]
        return OrchestratorConnection(process_name, connection_string, crypto_key, process_arguments, trigger_id)
