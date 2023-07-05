import tkinter as tk
from tkinter import ttk
import Logging_tab, Settings_tab

class Application(tk.Tk):
    connection_string = ""

    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("850x600")
        style = ttk.Style(self)
        style.theme_use('vista')

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        log_tab = Logging_tab.Logging_tab(notebook)
        set_tab = Settings_tab.Settings_tab(notebook)

        notebook.add(log_tab, text="Logs")
        notebook.add(set_tab, text="Settings")

        self.mainloop()

if __name__ == '__main__':
    Application()