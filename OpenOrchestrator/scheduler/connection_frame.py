"""This module contains a single class: ConnectionFrame."""

import os
import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.common import crypto_util
from OpenOrchestrator.database import db_util


# pylint: disable-next=too-many-ancestors
class ConnectionFrame(ttk.Frame):
    """A ttk.Frame object that contains two ttk.Entry and
    two ttk.Button used to enter a connection string and
    encryption key and to connect to the database.
    """
    def __init__(self, parent: tkinter.Widget):
        super().__init__(parent)

        frame = ttk.Frame(self)
        frame.columnconfigure(1, weight=1)
        frame.pack(fill='both')

        ttk.Label(frame, text="Connection string:").grid(row=0, column=0, sticky='w')

        self.conn_entry = ttk.Entry(frame)
        self.conn_entry.grid(row=0, column=1, sticky='ew')

        self.conn_button = ttk.Button(frame, text="Connect", command=self._connect)
        self.conn_button.grid(row=0, column=2, sticky='e')

        ttk.Label(frame, text="Encryption key:").grid(row=1, column=0, sticky='w')

        self.key_entry = ttk.Entry(frame)
        self.key_entry.grid(row=1, column=1, sticky='ew')

        self.disconn_button = ttk.Button(frame, text="Disconnect", command=self._disconnect, state='disabled')
        self.disconn_button.grid(row=1, column=2, sticky='e')

        self._initial_connect()

    def _connect(self) -> None:
        """Validate the connection string and encryption key
        and connect to the database.
        """
        conn_string = self.conn_entry.get()
        crypto_key = self.key_entry.get()

        if not crypto_util.validate_key(crypto_key):
            messagebox.showerror("Invalid encryption key", "The entered encryption key is not a valid AES key.")
            return

        if db_util.connect(conn_string):
            crypto_util.set_key(crypto_key)
            self._set_state(True)

    def _disconnect(self) -> None:
        db_util.disconnect()
        crypto_util.set_key(None)
        self._set_state(False)

    def _set_state(self, connected: bool) -> None:
        if connected:
            self.conn_entry.configure(state='disabled')
            self.key_entry.configure(state='disabled')
            self.conn_button.configure(state='disabled')
            self.disconn_button.configure(state='normal')
        else:
            self.conn_entry.configure(state='normal')
            self.key_entry.configure(state='normal')
            self.conn_button.configure(state='normal')
            self.disconn_button.configure(state='disabled')

    def _initial_connect(self) -> None:
        """Check the environment for a connection string
        and encryption key and connect to the database if both
        are found.
        """
        conn_string = os.environ.get('OpenOrchestratorConnString', None)
        if conn_string:
            self.conn_entry.insert(0, conn_string)

        crypto_key = os.environ.get('OpenOrchestratorKey', None)
        if crypto_key:
            self.key_entry.insert(0, crypto_key)

        if conn_string and crypto_key:
            self._connect()

    def new_key(self):
        """Creates a new encryption key and inserts it
        into the key entry.
        """
        key = crypto_util.generate_key().decode()
        self.key_entry.delete(0, 'end')
        self.key_entry.insert(0, key)
