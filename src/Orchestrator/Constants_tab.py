import tkinter
from tkinter import ttk, messagebox
import DB_util, Table_util

def create_tab(parent):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    tab.columnconfigure(0, weight=1)
    tab.rowconfigure((0,2), weight=1, uniform='a')
    tab.rowconfigure((1,3), weight=6, uniform='a')
    tab.rowconfigure((4, 5), weight=1, uniform='a')

    #Constants table
    ttk.Label(tab, text="Constants").grid(row=0, column=0)
    const_table_frame = ttk.Frame(tab)
    const_table_frame.grid(row=1, column=0, sticky='nsew')
    const_table = Table_util.create_table(const_table_frame, ('Name', 'Value'))

    #Credentials table
    ttk.Label(tab, text="Credentials").grid(row=2, column=0)
    cred_table_frame = ttk.Frame(tab)
    cred_table_frame.grid(row=3, column=0, sticky='nsew')
    cred_table = Table_util.create_table(cred_table_frame, ('Name', 'Username', 'Password'))

    # Controls 1
    controls_frame = ttk.Frame(tab)
    controls_frame.grid(row=4, column=0)
    ut = lambda: update_tables(const_table, cred_table)

    update_button = ttk.Button(controls_frame, text='Update', command=ut)
    update_button.pack(side='left')

    delete_button = ttk.Button(controls_frame, text='Delete', command=lambda: delete_selected(const_table, cred_table))
    delete_button.pack(side='left')

    # Controls 2
    controls_frame2 = ttk.Frame(tab)
    controls_frame2.grid(row=5, column=0)

    ttk.Button(controls_frame2, text='New constant', command=lambda: show_constant_popup(ut)).pack(side='left')
    ttk.Button(controls_frame2, text='New credential', command=lambda: show_credential_popup(ut)).pack(side='left')

    # Bindings
    const_table.bind('<FocusIn>', lambda e: Table_util.deselect_tables(cred_table))
    cred_table.bind('<FocusIn>', lambda e: Table_util.deselect_tables(const_table))

    return tab
   
def update_tables(const_table:ttk.Treeview, cred_table:ttk.Treeview):
    Table_util.update_table(const_table, DB_util.get_constants())
    Table_util.update_table(cred_table, DB_util.get_credentials())

def delete_selected(const_table:ttk.Treeview, cred_table:ttk.Treeview):
    if const_table.selection():
        name = const_table.item(const_table.selection()[0])['values'][0]
        if not messagebox.askyesno('Delete constant?', f"Are you sure you want to delete constant '{name}'?"):
            return
        DB_util.delete_constant(name)

    elif cred_table.selection():
        name = cred_table.item(cred_table.selection()[0])['values'][0]
        if not messagebox.askyesno('Delete credential?', f"Are you sure you want to delete credential '{name}'?"):
            return
        DB_util.delete_credential(name)

    else:
        return
    
    update_tables(const_table, cred_table)
    

def show_constant_popup(on_close:callable):
    ...

def show_credential_popup(on_close:callable):
    ...