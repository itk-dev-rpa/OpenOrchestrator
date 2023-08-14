import tkinter
from tkinter import ttk, messagebox
import DB_util, Crypto_util
import os

# TODO: Layout
def create_tab(parent):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
      
    ttk.Label(tab, text="Connection string:").pack()

    conn_entry = ttk.Entry(tab)
    conn_entry.pack(fill='x')

    conn_button = ttk.Button(tab, text="Connect", command=lambda: connect(conn_entry, conn_button))
    conn_button.pack()

    ttk.Label(tab, text="Encryption Key:").pack()
    key_entry = ttk.Entry(tab, width=50, validate='key')
    reg = key_entry.register(validate_key(key_entry))
    key_entry.configure(validatecommand=(reg, '%P'))
    key_entry.pack()

    key_button = ttk.Button(tab, text="New key", command=lambda: new_key(key_entry))
    key_button.pack()

    init_button = ttk.Button(tab, text='Initialize Database', command=DB_util.initialize_database)
    init_button.pack()

    # TEMPORARY
    conn_entry.insert(0, "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;")
    connect(conn_entry, conn_button)
    key_entry.insert(0, os.environ['OpenOrhcestratorKey'])

    return tab

def connect(conn_entry: ttk.Entry, conn_button: ttk.Button):
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

def new_key(key_entry:ttk.Entry):
    key = Crypto_util.generate_key()
    key_entry.delete(0, 'end')
    key_entry.insert(0, key)