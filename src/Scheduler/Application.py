import tkinter
from tkinter import ttk, messagebox
import pyodbc
import Settings_tab, Run_tab

class Application(tkinter.Tk):
    def __init__(self):
        self._connection_string = ""
        self._connection = None
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