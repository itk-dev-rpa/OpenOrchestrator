import tkinter
from tkinter import ttk, messagebox
import pyodbc
import Main_frame

class Application(tkinter.Tk):
    def __init__(self):
        self._connection_string = ""
        self._connection = None

        super().__init__()
        self.title("OpenOrchestrator - Scheduler")
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        main_frame = Main_frame.create_tab(self, self)

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