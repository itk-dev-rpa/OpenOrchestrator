"""This module is responsible for the layout and functionality of the Logging tab
in Orchestrator."""

import tkinter
from tkinter import ttk, font, messagebox
from datetime import datetime
from ast import literal_eval

from OpenOrchestrator.common import db_util
from OpenOrchestrator.Orchestrator import Table_util

def create_tab(parent):
    """Create a new Logging tab object.

    Args:
        parent: The ttk.Notebook object that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
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
    ttk.Label(filter_frame, text="Process name:").grid(row=1, column=0)
    ttk.Style().configure("TMenubutton", background='white')
    process_options_var = tkinter.StringVar()
    process_options = ttk.OptionMenu(filter_frame, process_options_var, "", *("", "hej1", "med2", "dig3","hej4", "med5", "dig6"))
    process_options['menu'].delete(0, 'end')
    process_options.grid(row=1, column=1, columnspan=3, sticky='ew', pady=2)

    # Level filter
    ttk.Label(filter_frame, text="Log level:").grid(row=2, column=0)
    log_level = tkinter.StringVar()
    ttk.OptionMenu(filter_frame, log_level, "", *("", "Trace", "Info", "Error")).grid(row=2, column=1, sticky='ew', pady=2)

    #Buttons
    def update_command():
        update(table, from_date_entry, to_date_entry, process_options, process_options_var, log_level)
    update_button = ttk.Button(filter_frame, text="Update", command=update_command)
    update_button.grid(row=4, column=0)

    return tab


def validate_date(entry: ttk.Entry) -> callable:
    """Creates a validator function to validate if
    an datetime entered in the given entry is valid.
    Changes the color of the Entry widget according
    to the validity of the datetime.

    Args:
        entry: The entry widget to validate on.

    Returns:
        callable: The validator function.
    """
    def inner(text: str):
        if parse_date(text) is not None:
            entry.configure(foreground='black')
        else:
            entry.configure(foreground='red')
        return True
    return inner


def resize_table(table: ttk.Treeview) -> None:
    """Resizes the 'Message' column of the table to match the longest string
    in the column.

    Args:
        table (ttk.Treeview): The table object.
    """
    max_length = 0
    f = font.nametofont("TkDefaultFont")

    for row in table.get_children():
        item = table.item(row)
        message = item['values'][-1]
        max_length = max(max_length, f.measure(message))

    table.column("Message", width=max_length+20, stretch=False)


def update(table: ttk.Treeview, from_date_entry: ttk.Entry, to_date_entry: ttk.Entry,
                 process_options:ttk.OptionMenu, process_options_var:tkinter.StringVar,
                 log_level: tkinter.StringVar) -> None:
    """Updates the logs table with new values from the database
    using the filter options given in the UI.
    Updates the filter option menus with values from the database.

    Args:
        table: The logs table to update.
        from_date_entry: The entry with the from date.
        to_date_entry: The entry with the to date.
        process_options: The options menu with process names.
        process_options_var: The StringVar connected to process_options.
        log_level: The log level to filter on.
    """
    offset = 0
    fetch = 100

    from_date = parse_date(from_date_entry.get()) or datetime(1900, 1, 1)
    to_date = parse_date(to_date_entry.get()) or datetime(2100, 12, 31)

    process_name = process_options_var.get()
    log_level = log_level.get()

    logs = db_util.get_logs(offset, fetch, from_date, to_date, process_name, log_level)

    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in logs:
        # Pretty date format
        row[0] = row[0].strftime('%d-%m-%Y %H:%M:%S')

        # Convert the message to single line text
        row[-1] = repr(row[-1])

        table.insert('', 'end', values=row)

    resize_table(table)

    # Update process_name OptionMenu
    process_names = db_util.get_unique_log_process_names()
    process_names.insert(0, "")
    replace_options(process_options, process_options_var, process_names)


def parse_date(date_str: str) -> datetime:
    """Tries to parse a string to a datetime object with
    a selection of different formats.

    Args:
        date_str: The string to parse.

    Returns:
        datetime: The parsed datetime if possible else None.
    """
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


def double_click_log(table: ttk.Treeview) -> None:
    """Handles double clicks on the logs table.
    Opens a popup with the selected log's text.

    Args:
        table (ttk.Treeview): _description_
    """
    item = table.selection()

    if item:
        values = list(table.item(item[0], 'values'))

        # Convert message back to multiline text
        values[-1] = literal_eval(values[-1])

        text = "\n".join(values)
        messagebox.showinfo("Info", text)


def replace_options(option_menu: ttk.OptionMenu, option_menu_var: tkinter.StringVar, new_options: tuple[str]) -> None:
    """Replaces the options in a ttk.OptionsMenu.

    Args:
        option_menu: The OptionsMenu whose options to replace.
        option_menu_var: The StringVar connected to the OptionsMenu.
        new_options (tuple[str]): _description_
    """
    selected = option_menu_var.get()

    option_menu.set_menu(None, *new_options)

    if selected in new_options:
        option_menu_var.set(selected)
