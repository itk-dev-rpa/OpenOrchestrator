"""This module contains a single class: ConnectionFrame."""

import os

from nicegui import ui

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.orchestrator import test_helper
from OpenOrchestrator.orchestrator.popups import generic_popups


# pylint: disable-next=too-few-public-methods
class ConnectionFrame():
    """A ui module containing input and buttons for connecting to the database."""
    def __init__(self):
        self.conn_input = ui.input("Connection String").classes("w-4/6")
        self.key_input = ui.input("Encryption Key").classes("w-4/6")
        self._define_validation()
        with ui.row().classes("w-full"):
            self.conn_button = ui.button("Connect", on_click=self._connect)
            self.disconn_button = ui.button("Disconnect", on_click=self._disconnect, )
            self.disconn_button.disable()

        self._initial_connect()
        test_helper.set_automation_ids(self, "connection_frame")

    def _define_validation(self):
        self.conn_input._validation = {"Please enter a connection string": bool}  # pylint: disable=protected-access
        self.key_input._validation = {"Invalid AES key": crypto_util.validate_key}  # pylint: disable=protected-access

    async def _connect(self) -> None:
        """Validate the connection string and encryption key
        and connect to the database.
        """
        if not self.conn_input.validate() & self.key_input.validate():
            ui.notify("Please fill out all fields.", type='warning')
            return

        conn_string = self.conn_input.value
        crypto_key = self.key_input.value

        if db_util.connect(conn_string):
            crypto_util.set_key(crypto_key)
            self._set_state(True)
            ui.notify("Connected!", type='positive', timeout=1000)

            if not os.getenv("ORCHESTRATOR_TEST") and not db_util.check_database_revision():
                await generic_popups.info_popup("This version of Orchestrator doesn't match the version of the connected database. Unexpected errors might occur.")

    def _disconnect(self) -> None:
        db_util.disconnect()
        crypto_util.set_key(None)
        self._set_state(False)
        ui.notify("Disconnected!", type='positive')

    def _set_state(self, connected: bool) -> None:
        if connected:
            self.conn_input.disable()
            self.key_input.disable()
            self.conn_button.disable()
            self.disconn_button.enable()
        else:
            self.conn_input.enable()
            self.key_input.enable()
            self.conn_button.enable()
            self.disconn_button.disable()

    def _initial_connect(self) -> None:
        """Check the environment for a connection string
        and encryption key and connect to the database if both
        are found.
        """
        conn_string = os.environ.get('OpenOrchestratorConnString', None)
        if conn_string:
            self.conn_input.value = conn_string

        crypto_key = os.environ.get('OpenOrchestratorKey', None)
        if crypto_key:
            self.key_input.value = crypto_key

    def new_key(self):
        """Creates a new encryption key and inserts it
        into the key entry.
        """
        key = crypto_util.generate_key()
        self.key_input.value = key.decode()
