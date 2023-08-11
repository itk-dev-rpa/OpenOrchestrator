import tkinter as tk
from tkinter import ttk, messagebox
import Logging_tab, Settings_tab, Trigger_tab
import pyodbc

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenOrchestrator")
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        trig_tab = Trigger_tab.create_tab(notebook)
        log_tab = Logging_tab.create_tab(notebook)
        set_tab = Settings_tab.create_tab(notebook)

        notebook.add(trig_tab, text="Triggers")
        notebook.add(log_tab, text="Logs")
        notebook.add(set_tab, text="Settings")

        self.mainloop()

if __name__=='__main__':
    Application()