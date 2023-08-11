import tkinter
from tkinter import ttk, font, messagebox
from datetime import datetime
import DB_util, Table_util

# TODO: Grid layout
def create_tab(parent):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
      
    #Table frame
    table_frame = tkinter.Frame(tab, bg='red')
    table_frame.pack(fill='both')

    table = Table_util.create_table(table_frame, ("Time", "Level", "Process", "Message"))
    table.column("Time", width=120, stretch=False)
    table.column("Level", width=50, stretch=False)
    table.column("Process", width=150, stretch=False)
    # TODO: Double click log to open pop-up
    
    #Filters
    ttk.Label(tab, text="Date from:").pack(side='left')
    from_date_entry = ttk.Entry(tab, width=21, validate='key')
    reg = tab.register(validate_date(from_date_entry))
    from_date_entry.configure(validatecommand=(reg, '%P'))
    from_date_entry.insert(0, 'dd-mm-yyyy hh:mm:ss')
    from_date_entry.pack(side='left')

    ttk.Label(tab, text='Date to:').pack(side='left')
    to_date_entry = ttk.Entry(tab, width=21, validate='key')
    reg = tab.register(validate_date(to_date_entry))
    to_date_entry.configure(validatecommand=(reg, '%P'))
    to_date_entry.insert(0, 'dd-mm-yyyy hh:mm:ss')
    to_date_entry.pack(side='left')

    #Buttons
    update_button = ttk.Button(tab, text="Update", command=lambda: update_table(table, from_date_entry, to_date_entry))
    update_button.pack(side='left')

    return tab

def validate_date(entry: ttk.Entry):
    def inner(text: str):
        if parse_date(text) is not None:
            entry.configure(foreground='black')
        else:
            entry.configure(foreground='red')
        return True
    return inner

def resize_table(table):
    max_length = 0
    f = font.nametofont("TkDefaultFont")

    for row in table.get_children():
        item = table.item(row)
        message = item['values'][-1]
        max_length = max(max_length, f.measure(message))

    table.column("Message", width=max_length+20, stretch=False)

def update_table(table: ttk.Treeview, from_date_entry: ttk.Entry, to_date_entry: ttk.Entry):    
    offset = 0
    fetch = 100
    
    from_date = parse_date(from_date_entry.get()) or datetime(1900, 1, 1)
    to_date = parse_date(to_date_entry.get()) or datetime(2100, 12, 31)

    logs = DB_util.get_logs(offset, fetch, from_date, to_date)
    
    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in logs:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)
    
    resize_table(table)

def parse_date(date_str: str):
    formats = (
        '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y %H:%M',
        '%d-%m-%Y',
        '%d-%m',
    )

    for f in formats:
        try:
            return datetime.strptime(date_str, f)
        except:
            ...

    return None