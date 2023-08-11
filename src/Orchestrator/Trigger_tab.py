from tkinter import ttk, messagebox
import DB_util, Table_util
import Single_Trigger_Popup, Email_Trigger_Popup, Scheduled_Trigger_Popup


def create_tab(parent):
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
    sc_table = Table_util.create_table(sc_table_frame, ('Process Name', 'Cron', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Blocking?', 'UUID'))

    #Email table
    ttk.Label(tab, text="Email Triggers").grid(row=2, column=0)
    e_table_frame = ttk.Frame(tab)
    e_table_frame.grid(row=3, column=0, sticky='nsew')
    e_table = Table_util.create_table(e_table_frame, ('Process Name', 'Folder', 'Last run', 'Path', 'Status', 'Is GIT?', 'Blocking?', 'UUID'))

    #Single table
    ttk.Label(tab, text="Single Triggers").grid(row=4, column=0)
    si_table_frame = ttk.Frame(tab)
    si_table_frame.grid(row=5, column=0, sticky='nsew')
    si_table = Table_util.create_table(si_table_frame, ('Process Name', 'Last run', 'Next run', 'Path', 'Status', 'Is GIT?', 'Blocking?', 'UUID'))

    # Controls 1
    controls_frame = ttk.Frame(tab)
    controls_frame.grid(row=6, column=0)
    ut = lambda: update_tables(sc_table, e_table, si_table)

    update_button = ttk.Button(controls_frame, text='Update', command=ut)
    update_button.pack(side='left')

    delete_button = ttk.Button(controls_frame, text='Delete', command=lambda: delete_trigger(sc_table, e_table, si_table))
    delete_button.pack(side='left')

    # Controls 2
    controls_frame2 = ttk.Frame(tab)
    controls_frame2.grid(row=7, column=0)

    ttk.Button(controls_frame2, text='New scheduled trigger', command=lambda: show_scheduled_trigger_popup(ut)).pack(side='left')
    ttk.Button(controls_frame2, text='New email trigger', command=lambda: show_email_trigger_popup(ut)).pack(side='left')
    ttk.Button(controls_frame2, text='New single trigger', command=lambda: show_single_trigger_popup(ut)).pack(side='left')

    # Bindings
    sc_table.bind('<FocusIn>', lambda e: deselect_tables(e_table, si_table))
    e_table.bind('<FocusIn>', lambda e: deselect_tables(sc_table, si_table))
    si_table.bind('<FocusIn>', lambda e: deselect_tables(sc_table, e_table))

    return tab

def show_scheduled_trigger_popup(on_close: callable):
    popup = Scheduled_Trigger_Popup.show_popup()
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)

def show_single_trigger_popup(on_close: callable):
    popup = Single_Trigger_Popup.show_popup()
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)

def show_email_trigger_popup(on_close: callable):
    popup = Email_Trigger_Popup.show_popup()
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)

def deselect_tables(*tables):
    for table in tables:
        table.selection_remove(table.selection())

def update_tables(sc_table, e_table, si_table):
    update_table(sc_table, DB_util.get_scheduled_triggers())
    update_table(e_table, DB_util.get_email_triggers())
    update_table(si_table, DB_util.get_single_triggers())

def update_table(table: ttk.Treeview, rows):
    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in rows:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)

def delete_trigger(sc_table: ttk.Treeview, e_table: ttk.Treeview, si_table: ttk.Treeview):
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
    
    DB_util.delete_trigger(UUID)

    update_tables(sc_table, e_table, si_table)



    