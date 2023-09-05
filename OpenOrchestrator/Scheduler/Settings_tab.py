from tkinter import ttk
import os
from OpenOrchestrator.Scheduler import DB_util, Crypto_util

def create_tab(parent, app):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
      
    conn_label = ttk.Label(tab, text="Connection string:")
    conn_label.pack()

    conn_entry = ttk.Entry(tab)
    conn_entry.pack(fill='x')

    conn_button = ttk.Button(tab, text="Connect", command=lambda: connect(app, conn_entry, conn_button))
    conn_button.pack()

    ttk.Label(tab, text="Encryption Key:").pack()
    key_entry = ttk.Entry(tab, width=50, validate='key')
    reg = key_entry.register(validate_key(key_entry))
    key_entry.configure(validatecommand=(reg, '%P'))
    key_entry.pack()

    # TEMPORARY
    conn_entry.insert(0, "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;")
    connect(app, conn_entry, conn_button)
    key_entry.insert(0, os.environ['OpenOrhcestratorKey'])

    return tab

def connect(app, conn_entry: ttk.Entry, conn_button: ttk.Button):
    conn_string = conn_entry.get()

    if DB_util.connect(conn_string):
        conn_button.configure(text="Connected!")
    else:
        conn_button.configure(text="Connect")

def validate_key(entry:ttk.Entry):
    def inner(text:str):
        if Crypto_util.validate_key(text):
            entry.configure(foreground='black')
            Crypto_util.set_key(text)
        else:
            entry.configure(foreground='red')
        return True
    return inner