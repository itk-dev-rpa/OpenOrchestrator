"""This module is responsible for the layout and functionality of the settings tab
in Scheduler."""

import os
import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util
from OpenOrchestrator.scheduler import util


# pylint: disable=too-many-ancestors
class SettingsTab(ttk.Frame):
    """A ttk.Frame object containing the functionality of the settings tab in Scheduler."""
    def __init__(self, parent: ttk.Notebook):
        super().__init__(parent)
        self.pack(fill='both', expand=True)

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Connection string:").grid(row=0, column=0, sticky='w')

        self._conn_entry = ttk.Entry(self)
        self._conn_entry.grid(row=0, column=1, sticky='ew')

        self._conn_button = ttk.Button(self, text="Connect", command=self._connect)
        self._conn_button.grid(row=0, column=2, sticky='e')

        ttk.Label(self, text="Encryption key:").grid(row=1, column=0, sticky='w')

        self._key_entry = ttk.Entry(self)
        self._key_entry.grid(row=1, column=1, sticky='ew')

        self._disconn_button = ttk.Button(self, text="Disconnect", command=self._disconnect, state='disabled')
        self._disconn_button.grid(row=1, column=2, sticky='e')

        ttk.Label(self, text=f"Scheduler name: {util.get_scheduler_name()}").grid(row=2, column=0, sticky='w', columnspan=2, pady=10)

        self.whitelist_value = tkinter.BooleanVar()
        self._whitelist_check = ttk.Checkbutton(self, text="Only run whitelisted triggers", variable=self.whitelist_value)
        self._whitelist_check.grid(row=3, column=0, sticky='w', columnspan=2)

        self._auto_fill()

    def _connect(self) -> None:
        """Validate the connection string and encryption key
        and connect to the database.
        """
        conn_string = self._conn_entry.get()
        crypto_key = self._key_entry.get()

        if not crypto_util.validate_key(crypto_key):
            messagebox.showerror("Invalid encryption key", "The entered encryption key is not a valid AES key.")
            return

        if db_util.connect(conn_string):
            crypto_util.set_key(crypto_key)
            self._set_state(True)
            if not db_util.check_database_revision():
                messagebox.showerror("Warning", "This version of Scheduler doesn't match the version of the connected database. Unexpected errors might occur.")

    def _disconnect(self) -> None:
        db_util.disconnect()
        crypto_util.set_key(None)
        self._set_state(False)

    def _set_state(self, connected: bool) -> None:
        if connected:
            self._conn_entry.configure(state='disabled')
            self._key_entry.configure(state='disabled')
            self._conn_button.configure(state='disabled')
            self._disconn_button.configure(state='normal')
            self._whitelist_check.configure(state='disabled')
        else:
            self._conn_entry.configure(state='normal')
            self._key_entry.configure(state='normal')
            self._conn_button.configure(state='normal')
            self._disconn_button.configure(state='disabled')
            self._whitelist_check.configure(state='normal')

    def _auto_fill(self) -> None:
        """Check the environment for a connection string
        and encryption key and autofill the inputs.
        """
        conn_string = os.environ.get('OpenOrchestratorConnString', None)
        if conn_string:
            self._conn_entry.insert(0, conn_string)

        crypto_key = os.environ.get('OpenOrchestratorKey', None)
        if crypto_key:
            self._key_entry.insert(0, crypto_key)

    def new_key(self):
        """Creates a new encryption key and inserts it
        into the key entry.
        """
        key = crypto_util.generate_key().decode()
        self._key_entry.delete(0, 'end')
        self._key_entry.insert(0, key)
