from tkinter import ttk, messagebox
import pyodbc
from DB_util import catch_db_error
import Single_Trigger_Popup, Email_Trigger_Popup, Scheduled_Trigger_Popup


def create_tab(parent, app):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure((0,2,4), weight=1, uniform='a')
    tab.rowconfigure((1,3,5), weight=6, uniform='a')
    tab.rowconfigure((6,7), weight=1, uniform='a')

    #Scheduled table
    ttk.Label(tab, text="Scheduled Triggers").grid(row=0, column=0)
    sc_table_frame = ttk.Frame(tab)
    sc_table_frame.grid(row=1, column=0, sticky='nsew')
    sc_table = create_table(sc_table_frame, ('Process Name', 'Cron', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Blocking?', 'UUID'))

    #Email table
    ttk.Label(tab, text="Email Triggers").grid(row=2, column=0)
    e_table_frame = ttk.Frame(tab)
    e_table_frame.grid(row=3, column=0, sticky='nsew')
    e_table = create_table(e_table_frame, ('Process Name', 'Folder', 'Last run', 'Path', 'Status', 'Is GIT?', 'Blocking?', 'UUID'))

    #Single table
    ttk.Label(tab, text="Single Triggers").grid(row=4, column=0)
    si_table_frame = ttk.Frame(tab)
    si_table_frame.grid(row=5, column=0, sticky='nsew')
    si_table = create_table(si_table_frame, ('Process Name', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Blocking?', 'UUID'))

    # Controls 1
    controls_frame = ttk.Frame(tab)
    controls_frame.grid(row=6, column=0)
    ut = lambda: update_tables(app, sc_table, e_table, si_table)
    update_button = ttk.Button(controls_frame, text='Update', command=ut)
    update_button.pack(side='left')
    delete_button = ttk.Button(controls_frame, text='Delete', command=lambda: delete_trigger(app, sc_table, e_table, si_table))
    delete_button.pack(side='left')

    # Controls 2
    controls_frame2 = ttk.Frame(tab)
    controls_frame2.grid(row=7, column=0)

    ttk.Button(controls_frame2, text='New scheduled trigger', command=lambda: show_scheduled_trigger_popup(app, ut)).pack(side='left')
    ttk.Button(controls_frame2, text='New email trigger', command=lambda: show_email_trigger_popup(app, ut)).pack(side='left')
    ttk.Button(controls_frame2, text='New single trigger', command=lambda: show_single_trigger_popup(app, ut)).pack(side='left')

    # Bindings
    sc_table.bind('<FocusIn>', lambda t: deselect_tables(e_table, si_table))
    e_table.bind('<FocusIn>', lambda t: deselect_tables(sc_table, si_table))
    si_table.bind('<FocusIn>', lambda t: deselect_tables(sc_table, e_table))

    return tab

def show_scheduled_trigger_popup(app, on_close: callable):
    popup = Scheduled_Trigger_Popup.show_popup(app)
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)

def show_single_trigger_popup(app, on_close: callable):
    popup = Single_Trigger_Popup.show_popup(app)
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)

def show_email_trigger_popup(app, on_close: callable):
    popup = Email_Trigger_Popup.show_popup(app)
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)

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

@catch_db_error
def delete_trigger(app, sc_table: ttk.Treeview, e_table: ttk.Treeview, si_table: ttk.Treeview):
    if sc_table.selection():
        table = sc_table
    elif e_table.selection():
        table = e_table
    elif si_table.selection():
        table = si_table
    else:
        return

    UUID = table.item(table.selection()[0])['values'][-1]

    if not messagebox.askyesno('Delete trigger', f"Are you sure you want to delete trigger '{UUID}'?"):
        return
    
    with open('SQL/Delete_Trigger.sql') as file:
        commands = file.read()
    
    commands = commands.replace('{UUID}', UUID)
    commands = commands.split(';')

    conn = app.get_db_connection()

    for command in commands:
        if command:
            conn.execute(command)
    
    conn.commit()

    update_tables(app, sc_table, e_table, si_table)



    