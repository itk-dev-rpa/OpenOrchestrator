import tkinter as tk
from tkinter import ttk
import Logging_tab, Settings_tab, Trigger_tab
import pyodbc

class Application(tk.Tk):
    def __init__(self):
        self.connection_string = ""

        tk.Tk.__init__(self)
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        trig_tab = Trigger_tab.Trigger_tab(notebook, self)
        log_tab = Logging_tab.Logging_tab(notebook, self)
        set_tab = Settings_tab.Settings_tab(notebook, self)

        notebook.add(trig_tab, text="Triggers")
        notebook.add(log_tab, text="Logs")
        notebook.add(set_tab, text="Settings")

        self.mainloop()
    
    def connect_to_db(self):
        return pyodbc.connect(self.connection_string)
    
if __name__=='__main__':
    Application()