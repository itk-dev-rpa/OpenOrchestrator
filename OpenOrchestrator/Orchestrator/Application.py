"""This module is the entry point for the Orchestrator app. It contains a single class
that when created starts the application."""

import tkinter
from tkinter import ttk

from OpenOrchestrator.Orchestrator import Logging_tab, Settings_tab, Trigger_tab, Constants_tab

class Application(tkinter.Tk):
    """The main application object of the Orchestrator app.
    Extends the tkinter.Tk object.
    """
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
        const_tab = Constants_tab.create_tab(notebook)
        set_tab = Settings_tab.create_tab(notebook)

        notebook.add(trig_tab, text="Triggers")
        notebook.add(log_tab, text="Logs")
        notebook.add(const_tab, text="Constants")
        notebook.add(set_tab, text="Settings")

        self.mainloop()

if __name__=='__main__':
    Application()
