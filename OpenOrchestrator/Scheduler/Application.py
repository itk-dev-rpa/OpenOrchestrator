"""This module is the entry point for the Scheduler app. It contains a single class
that when created starts the application."""

import tkinter
from tkinter import ttk, messagebox
from OpenOrchestrator.Scheduler import Settings_tab, Run_tab

class Application(tkinter.Tk):
    """The main application object of the Scheduler app.
    Extends the tkinter.Tk object.
    """
    def __init__(self):
        self.running_jobs = []
        self.running = False

        super().__init__()
        self.title("OpenOrchestrator - Scheduler")
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        run_tab = Run_tab.create_tab(notebook, self)
        settings_tab = Settings_tab.create_tab(notebook)

        notebook.add(run_tab, text='Run')
        notebook.add(settings_tab, text="Settings")

        self.protocol('WM_DELETE_WINDOW', self.on_close)

        self.mainloop()

    def on_close(self):
        """Checks whether any jobs are still running and prompts the user before closing."""
        if (len(self.running_jobs) == 0
                or messagebox.askyesno('Warning', 'Some processes are still running. Closing the scheduler while processes are running will gum up the trigger tables. Are you sure you want to close?')):
            self.destroy()



if __name__=='__main__':
    Application()
