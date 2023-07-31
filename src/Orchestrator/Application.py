import tkinter as tk
from tkinter import ttk, messagebox
import Logging_tab, Settings_tab, Trigger_tab
import pyodbc

class Application(tk.Tk):
    def __init__(self):
        self._connection_string = ""
        self._connection = None

        super().__init__()
        self.title("OpenOrchestrator")
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        trig_tab = Trigger_tab.create_tab(notebook, self)
        log_tab = Logging_tab.create_tab(notebook, self)
        set_tab = Settings_tab.create_tab(notebook, self)

        notebook.add(trig_tab, text="Triggers")
        notebook.add(log_tab, text="Logs")
        notebook.add(set_tab, text="Settings")

        self.mainloop()
    
    def get_db_connection(self):
        if self._connection:
            try:
                self._connection.cursor()
                return self._connection
            except pyodbc.ProgrammingError as e:
                if str(e) != 'Attempt to use a closed connection.':
                    messagebox.showerror("Connection Error", str(e))
        
        try:
            self._connection = pyodbc.connect(self._connection_string)
            return self._connection
        except pyodbc.InterfaceError as e:
            messagebox.showerror("Error", f"Connection failed.\nGo to settings and enter a valid connection string.\n{e}")
    
if __name__=='__main__':
    Application()