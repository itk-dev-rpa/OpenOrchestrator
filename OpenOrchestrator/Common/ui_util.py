"""This module contains functions to create similar UI elements used more than
once across the project."""

import os
import tkinter
from tkinter import ttk

from OpenOrchestrator.Common import db_util, crypto_util

def create_connection_frame(parent: tkinter.Widget) -> ttk.Frame:
    """Creates a frame containing a label, entry and button
    used to connect to a database.

    Args:
        parent: The parent of the created frame.

    Returns:
        ttk.Frame: A frame containing a label, entry and button.
    """
    frame = ttk.Frame(parent)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Connection string:").grid(row=0, column=0, sticky='w')

    conn_entry = ttk.Entry(frame)
    conn_entry.grid(row=0, column=1, sticky='ew')

    conn_button = ttk.Button(frame, text="Connect", command=lambda: _connect(conn_entry, conn_button))
    conn_button.grid(row=0, column=2, sticky='e')

    # If a connection string exists in the environment
    # insert it and connect automatically.
    conn_string = os.environ.get('OpenOrchestratorConnString', None)
    if conn_string:
        conn_entry.insert(0, conn_string)
        _connect(conn_entry, conn_button)

    return frame


def _connect(conn_entry: ttk.Entry, conn_button: ttk.Button) -> None:
    """Connect using the connection string given in the UI.
    Change the label of the connect button if successful.

    Args:
        conn_entry: The connection string entry.
        conn_button: The connect button.
    """
    conn_string = conn_entry.get()

    if db_util.connect(conn_string):
        conn_button.configure(text="Connected!")
    else:
        conn_button.configure(text="Connect")


def create_encryption_key_frame(parent: tkinter.Widget) -> [ttk.Frame, ttk.Entry]:
    """Creates a frame containing a label and an entry
    to enter a encryption key.

    Args:
        parent: the parent of the created frame.

    Returns:
        ttk.Frame: A frame containing a label and entry.
        ttk.Entry: The key entry in the frame.
    """
    frame = ttk.Frame(parent)

    ttk.Label(frame, text="Encryption Key:").pack()

    key_entry = ttk.Entry(frame, width=50, validate='key')
    reg = key_entry.register(_validate_key(key_entry))
    key_entry.configure(validatecommand=(reg, '%P'))
    key_entry.pack()

    crypto_key = os.environ.get('OpenOrhcestratorKey', None)
    if crypto_key:
        key_entry.insert(0, crypto_key)

    return frame, key_entry


def _validate_key(entry:ttk.Entry) -> callable:
    """Creates a validator function to validate if
    an AES key entered in the given entry is valid.
    Changes the color of the Entry widget according
    to the validity of the key.

    Args:
        entry: The entry widget to validate on.

    Returns:
        callable: The validator function.
    """
    def inner(text:str):
        if crypto_util.validate_key(text):
            entry.configure(foreground='black')
            crypto_util.set_key(text)
        else:
            entry.configure(foreground='red')
        return True
    return inner
