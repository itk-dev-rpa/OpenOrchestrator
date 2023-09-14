import tkinter
from tkinter import ttk, font, messagebox
from datetime import datetime
from OpenOrchestrator.Orchestrator import DB_util, Table_util

def create_tab(parent):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)

    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(0, weight=2, uniform='a')
    tab.rowconfigure(1, weight=1, uniform='a')

    #Table
    table_frame = ttk.Frame(tab)
    table_frame.grid(row=0, column=0, sticky="nsew")

    table = Table_util.create_table(table_frame, ("Time", "Level", "Process", "Message"))
    table.column("Time", width=120, stretch=False)
    table.column("Level", width=50, stretch=False)
    table.column("Process", width=150, stretch=False)
    table.bind("<Double-1>", lambda e: double_click_log(table))
    
    # Filters
    filter_frame = ttk.Frame(tab)
    filter_frame.grid(row=1, column=0, sticky='nsew')

    # Date filters
    ttk.Label(filter_frame, text="Date from:").grid(row=0, column=0, sticky='w')
    from_date_entry = ttk.Entry(filter_frame, width=21, validate='key')
    reg = tab.register(validate_date(from_date_entry))
    from_date_entry.configure(validatecommand=(reg, '%P'))
    from_date_entry.insert(0, 'dd-mm-yyyy hh:mm:ss')
    from_date_entry.grid(row=0, column=1)

    ttk.Label(filter_frame, text='Date to:').grid(row=0, column=2)
    to_date_entry = ttk.Entry(filter_frame, width=21, validate='key')
    reg = tab.register(validate_date(to_date_entry))
    to_date_entry.configure(validatecommand=(reg, '%P'))
    to_date_entry.insert(0, 'dd-mm-yyyy hh:mm:ss')
    to_date_entry.grid(row=0, column=3)

    # Process filter
    ttk.Style().configure("TMenubutton", background='white')
    process_options_var = tkinter.StringVar()
    process_options = ttk.OptionMenu(filter_frame, process_options_var, "", *("", "hej1", "med2", "dig3","hej4", "med5", "dig6"))
    process_options['menu'].delete(0, 'end')
    process_options.grid(row=1, columnspan=3, sticky='ew')
    
    #Buttons
    update_button = ttk.Button(filter_frame, text="Update", command=lambda: update_table(table, from_date_entry, to_date_entry, process_options, process_options_var))
    update_button.grid(row=2, column=0)

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

def update_table(table: ttk.Treeview, from_date_entry: ttk.Entry, to_date_entry: ttk.Entry, 
                 process_options:ttk.OptionMenu, process_options_var:tkinter.StringVar):    
    offset = 0
    fetch = 100
    
    from_date = parse_date(from_date_entry.get()) or datetime(1900, 1, 1)
    to_date = parse_date(to_date_entry.get()) or datetime(2100, 12, 31)

    logs = DB_util.get_logs(offset, fetch, from_date, to_date, process_options_var.get())
    
    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in logs:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)
    
    resize_table(table)

    # Update process_name OptionMenu
    process_names = DB_util.get_unique_log_process_names()
    process_names.insert(0, "")
    replace_options(process_options, process_options_var, process_names)

def parse_date(date_str: str):
    formats = (
        '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y %H:%M',
        '%d-%m-%Y'
    )

    for f in formats:
        try:
            return datetime.strptime(date_str, f)
        except ValueError:
            ...

    return None

def double_click_log(table: ttk.Treeview):
    item = table.selection()

    if item:
        values = table.item(item[0], 'values')
        text = "\n".join(values)
        messagebox.showinfo("Info", text)

def replace_options(option_menu: ttk.OptionMenu, option_menu_var: tkinter.StringVar, new_options: tuple[str]):
    # Reset var and delete all old options
    selected = option_menu_var.get()
    if selected not in new_options:
        option_menu_var.set('')

    option_menu['menu'].delete(0, 'end')

    # Insert list of new options (tk._setit hooks them up to var)
    for choice in new_options:
        option_menu['menu'].add_command(label=choice, command=tkinter._setit(option_menu_var, choice))