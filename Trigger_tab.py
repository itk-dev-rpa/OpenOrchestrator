import tkinter
from tkinter import ttk

class Trigger_tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0,2,4), weight=6, uniform='a')
        self.rowconfigure((1,3,5), weight=1, uniform='a')

    #Scheduled table
        s_table_frame = tkinter.Frame(self, background='red')
        s_table_frame.grid(row=0, column=0, sticky='nsew')

        s_table = create_table(s_table_frame, ('Process Name', 'Cron', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Force update?', 'Blocking?'))

    #Scheduled controls
        s_controls_frame = tkinter.Frame(self, background='blue')
        s_controls_frame.grid(row=1, column=0, sticky='nsew')

        s_button = ttk.Button(s_controls_frame, text='Hej')
        s_button.pack()
    
    #Email table
        e_table_frame = tkinter.Frame(self, background='green')
        e_table_frame.grid(row=2, column=0, sticky='nsew')

        e_table = create_table(e_table_frame, ('Process Name', 'Folder', 'Last run', 'Path', 'Status', 'Is GIT?', 'Force update?', 'Blocking?'))
    
    #Email controls
        e_controls_frame = tkinter.Frame(self, background='yellow')
        e_controls_frame.grid(row=3, column=0, sticky='nsew')

        e_button = ttk.Button(e_controls_frame, text='Hej')
        e_button.pack()
    
    #Single table
        s_table_frame = tkinter.Frame(self, background='purple')
        s_table_frame.grid(row=4, column=0, sticky='nsew')

        s_table = create_table(s_table_frame, ('Process Name', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Force update?', 'Blocking?'))
    
    #Single controls
        s_controls_frame = tkinter.Frame(self, background='grey')
        s_controls_frame.grid(row=5, column=0, sticky='nsew')

        s_button = ttk.Button(s_controls_frame, text='Hej')
        s_button.pack()


def create_table(parent, columns):
    table = ttk.Treeview(parent, show='headings')
    table['columns'] = columns
    for c in table['columns']:
        table.heading(c, text=c, anchor='w')
        table.column(c, stretch=False)
    
    yscroll = ttk.Scrollbar(parent, orient='vertical', command=table.yview)
    yscroll.pack(side='left', fill='y')
    table.configure(yscrollcommand=yscroll.set)

    xscroll = ttk.Scrollbar(parent, orient='horizontal', command=table.xview)
    xscroll.pack(side='bottom', fill='x')
    table.configure(xscrollcommand=xscroll.set)

    table.pack(expand=True, fill='both')

    return table
