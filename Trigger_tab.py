from tkinter import ttk, messagebox
import pyodbc
from DB_util import catch_db_error

class Trigger_tab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.pack(fill='both', expand=True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0,2,4), weight=1, uniform='a')
        self.rowconfigure((1,3,5), weight=6, uniform='a')
        self.rowconfigure(6, weight=1, uniform='a')

    #Scheduled table
        ttk.Label(self, text="Scheduled Triggers").grid(row=0, column=0)

        sc_table_frame = ttk.Frame(self)
        sc_table_frame.grid(row=1, column=0, sticky='nsew')

        sc_table = create_table(sc_table_frame, ('Process Name', 'Cron', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Force update?', 'Blocking?', 'UUID'))
    
    #Email table
        ttk.Label(self, text="Email Triggers").grid(row=2, column=0)

        e_table_frame = ttk.Frame(self)
        e_table_frame.grid(row=3, column=0, sticky='nsew')

        e_table = create_table(e_table_frame, ('Process Name', 'Folder', 'Last run', 'Path', 'Status', 'Is GIT?', 'Force update?', 'Blocking?', 'UUID'))
    
    #Single table
        ttk.Label(self, text="Single Triggers").grid(row=4, column=0)

        si_table_frame = ttk.Frame(self)
        si_table_frame.grid(row=5, column=0, sticky='nsew')

        si_table = create_table(si_table_frame, ('Process Name', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Force update?', 'Blocking?', 'UUID'))
    
    # Controls
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=6, column=0, sticky='nsew')

        update_button = ttk.Button(controls_frame, text='Update', command=lambda: update_tables(app, sc_table, e_table, si_table))
        update_button.pack()
    
    # Bindings
        sc_table.bind('<FocusIn>', lambda t: deselect_tables(e_table, si_table))
        e_table.bind('<FocusIn>', lambda t: deselect_tables(sc_table, si_table))
        si_table.bind('<FocusIn>', lambda t: deselect_tables(sc_table, e_table))


def deselect_tables(*tables):
    for table in tables:
        table.selection_remove(table.selection())


def create_table(parent, columns):
    table = ttk.Treeview(parent, show='headings', selectmode='browse')
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

def update_tables(app, sc_table, e_table, si_table):
    update_table(app, sc_table, 'SQL/Get_Scheduled_Triggers.sql')
    update_table(app, e_table, 'SQL/Get_Email_Triggers.sql')
    update_table(app, si_table, 'SQL/Get_Single_Triggers.sql')

@catch_db_error
def update_table(app, table: ttk.Treeview, sql_path):
    conn = app.get_db_connection()

    with open(sql_path) as file:
        command = file.read()

    cursor = conn.execute(command)

    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in cursor:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)

    
    