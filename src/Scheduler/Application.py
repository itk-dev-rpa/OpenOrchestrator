import tkinter
from tkinter import ttk, messagebox
import Settings_tab, Run_tab

class Application(tkinter.Tk):
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
        settings_tab = Settings_tab.create_tab(notebook, self)

        notebook.add(run_tab, text='Run')
        notebook.add(settings_tab, text="Settings")

        self.protocol('WM_DELETE_WINDOW', self.on_close)
        
        self.mainloop()
    
    def on_close(self):
        if (len(self.running_jobs) == 0 
            or messagebox.askyesno('Warning', 'Some processes are still running. Closing the scheduler while processes are running will gum up the trigger tables. Are you sure you want to close?')):
            self.destroy()



if __name__=='__main__':
    Application()