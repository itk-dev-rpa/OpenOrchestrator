import tkinter
from tkinter import ttk
import Settings_tab, Run_tab

class Application(tkinter.Tk):
    def __init__(self):
        self.running_jobs = []
        self.running = False
        self.next_loop = None

        super().__init__()
        self.title("OpenOrchestrator - Scheduler")
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        run_tab = Run_tab.create_tab(notebook, self)
        settings_tab = Settings_tab.create_tab(notebook, self)

        notebook.add(run_tab, text='Run')
        notebook.add(settings_tab, text="Settings")
        
        self.mainloop()


if __name__=='__main__':
    Application()