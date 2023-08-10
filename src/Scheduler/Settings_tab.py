from tkinter import ttk
import DB_util

def create_tab(parent, app):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
      
    conn_label = ttk.Label(tab, text="Connection string:")
    conn_label.pack()

    conn_entry = ttk.Entry(tab)
    conn_entry.pack(fill='x')

    conn_button = ttk.Button(tab, text="Connect", command=lambda: connect(app, conn_entry, conn_button))
    conn_button.pack()

    # TEMPORARY
    conn_entry.insert(0, "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;")
    connect(app, conn_entry, conn_button)

    return tab

def connect(app, conn_entry: ttk.Entry, conn_button: ttk.Button):
    conn_string = conn_entry.get()

    if DB_util.connect(conn_string):
        conn_button.configure(text="Connected!")
    else:
        conn_button.configure(text="Connect")