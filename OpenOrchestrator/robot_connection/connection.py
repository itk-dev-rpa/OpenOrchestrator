"""The main module of this package. It contains a single class called OrchestratorConnection.
The easiest way to create an OrchestratorConnection object is to call the
class method create_connection_from_args."""

import sys
from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util


class OrchestratorConnection:
    """An OrchestratorConnection is used to easier communicate with
    OpenOrchestrator within a running process. If used in conjuction with
    OpenOrchestrator's Scheduler use orchestrator_connection.create_connection_from_args
    to instead of initializing the object manually.
    """

    def __init__(self, process_name: str, connection_string: str, crypto_key: str):
        self.process_name = process_name
        crypto_util.set_key(crypto_key)
        db_util.connect(connection_string)

    def __repr__(self):
        return f"OrchestratorConnection - Process name: {self.process_name}"

    def log_trace(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'trace'.
        The log is automatically annotated with the current time and name of the process"""
        db_util.create_log(self.process_name, 0, message)

    def log_info(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'info'.
        The log is automatically annotated with the current time and name of the process
        """
        db_util.create_log(self.process_name, 1, message)

    def log_error(self, message: str) -> None:
        """Create a message in the Orchestrator log with a level of 'error'.
        The log is automatically annotated with the current time and name of the process
        """
        db_util.create_log(self.process_name, 2, message)

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

    @classmethod
    def create_connection_from_args(cls):
        """Create a Connection object using the arguments passed to sys.argv.
        This function is the preferred way to create a connection with OpenOrchestrator's Scheduler"""
        process_name = sys.argv[1]
        connection_string = sys.argv[2]
        crypto_key = sys.argv[3]
        process_arguments = sys.argv[4]
        return OrchestratorConnection(process_name, connection_string, crypto_key, process_arguments)

