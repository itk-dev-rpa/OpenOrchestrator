import tkinter
from tkinter import ttk, messagebox
import pyodbc

class Settings_tab(tkinter.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.pack(pady=20, padx=10, fill='both', expand=True)
      
        conn_label = ttk.Label(self, text="Connection string:")
        conn_label.pack()

        conn_entry = ttk.Entry(self)
        conn_entry.insert(0, "Driver={ODBC Driver 17 for SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=yes;")
        conn_entry.pack(fill='x')

        conn_button = ttk.Button(self, text="Connect", command=lambda: connect(parent, conn_entry, conn_button))
        conn_button.pack()

def connect(app, conn_entry: ttk.Entry, conn_button: ttk.Button):
    conn_string = conn_entry.get()
    try:
        pyodbc.connect(conn_string)
        app.connection_string = conn_string
        conn_button.configure(text="Connected!")
    except:
        conn_button.configure(text="Connect")
        messagebox.showerror("Connection failed", "Connection failed")
