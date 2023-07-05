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
        conn_entry.insert(0, "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;")
        conn_entry.pack(fill='x')

        conn_button = ttk.Button(self, text="Connect", command=lambda: connect(parent, conn_entry, conn_button))
        conn_button.pack()

        init_button = ttk.Button(self, text='Initialize Database', command=lambda: initialize_database(parent))
        init_button.pack()

def connect(app, conn_entry: ttk.Entry, conn_button: ttk.Button):
    conn_string = conn_entry.get()
    try:
        pyodbc.connect(conn_string)
        app.connection_string = conn_string
        conn_button.configure(text="Connected!")
    except Exception as e:
        conn_button.configure(text="Connect")
        messagebox.showerror("Connection failed", str(e))

def initialize_database(app):
    try:
        conn = pyodbc.connect(app.connection_string)
    except Exception as e:
        messagebox.showerror("Connection failed", str(e))
    
    with open('SQL/initialize.sql') as sql_file:
        commands = sql_file.read().split(";")
        
    try:
        for command in commands:
            if command:
                conn.execute(command)
        
        conn.commit()
        messagebox.showinfo("Database initialized", "Database tables successfully created.")
    except Exception as e:
        messagebox.showerror('Initialization failed', str(e))
