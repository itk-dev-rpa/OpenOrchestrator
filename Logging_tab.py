import tkinter
from tkinter import ttk, font, messagebox
from datetime import datetime
import os
import pyodbc
# TODO: Grid layout
class Logging_tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(pady=20, padx=10, fill='both', expand=True)
      
    #Table frame
        table_frame = tkinter.Frame(self, bg='red')
        table_frame.pack(fill='both')

        table = ttk.Treeview(table_frame, show="headings")
        
        table['columns'] = ("Time", "Level", "Process", "Message")
        table.column("Time", width=120, stretch=False)
        table.column("Level", width=50, stretch=False)
        table.column("Process", width=150, stretch=False)
        for c in table['columns']:
            table.heading(c, text=c, anchor='w')

        table_yscroll = ttk.Scrollbar(table_frame, orient='vertical', command=table.yview)
        table_yscroll.pack(side='left', fill='y')
        table.configure(yscrollcommand=table_yscroll.set)

        table_xscroll = ttk.Scrollbar(table_frame, orient='horizontal', command=table.xview)
        table_xscroll.pack(side='bottom', fill='x')
        table.configure(xscrollcommand=table_xscroll.set)

        table.pack(expand=True, fill='both')

        table.bind("<Control-c>", lambda e: copy_rows(table))
    
    #Filters
        ttk.Label(self, text="Date from:").pack(side='left')
        from_date_entry = ttk.Entry(self, width=21, validate='key')
        reg = self.register(validate_date(from_date_entry))
        from_date_entry.configure(validatecommand=(reg, '%P'))
        from_date_entry.insert(0, 'dd-mm-yyyy hh:mm:ss')
        from_date_entry.pack(side='left')

        ttk.Label(self, text='Date to:').pack(side='left')
        to_date_entry = ttk.Entry(self, width=21, validate='key')
        reg = self.register(validate_date(to_date_entry))
        to_date_entry.configure(validatecommand=(reg, '%P'))
        to_date_entry.insert(0, 'dd-mm-yyyy hh:mm:ss')
        to_date_entry.pack(side='left')

    #Buttons
        update_button = ttk.Button(self, text="Update", command=lambda: update_table(parent, table, from_date_entry, to_date_entry))
        update_button.pack(side='left')

def validate_date(entry: ttk.Entry):
    def inner(text: str):
        try:
            datetime.strptime(text, '%d-%m-%Y %H:%M:%S')
            entry.configure(foreground='black')
        except:
            entry.configure(foreground='red')
        return True
    return inner

def copy_rows(table):
    string = "("
    for item in table.selection():
        string += f"echo {str(table.item(item)['values'])} & " 
    string = string.rstrip("& ")
    string += ")"
    os.system(f"{string} | clip")

def resize_table(table):
    max_length = 0
    f = font.nametofont("TkDefaultFont")
    for row in table.get_children():
        item = table.item(row)
        message = item['values'][-1]
        max_length = max(max_length, f.measure(message))
    table.column("Message", width=max_length+20, stretch=False)
    #TODO: Row height on multiline strings / repr()

def update_table(app, table: ttk.Treeview, from_date_entry: ttk.Entry, to_date_entry: ttk.Entry):
    try:
        conn = pyodbc.connect(app.connection_string)   
    except:
        messagebox.showerror("Error", "Connection failed! Go to settings and enter a valid connection string.")
        return
    
    with open('SQL/Get_Logs.sql') as file:
        command = file.read()
    
    offset = 0
    fetch = 100
    filter = create_select_filter(from_date_entry, to_date_entry)

    command = command.replace('{offset}', str(offset))
    command = command.replace('{fetch}', str(fetch))
    command = command.replace('{filter}', filter)

    print(command)

    try:
        cursor = conn.execute(command)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return
    
    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in cursor:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)
    
    resize_table(table)

def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S')
    except:
        return None
    
def create_select_filter(from_date_entry: ttk.Entry, to_date_entry: ttk.Entry):
    from_date = parse_date(from_date_entry.get())
    to_date = parse_date(to_date_entry.get())

    filters = []
    if from_date:
        filters.append(f"'{from_date.strftime('%d-%m-%Y %H:%M:%S')}' <= log_time")
    if to_date:
        filters.append(f"log_time <= '{to_date.strftime('%d-%m-%Y %H:%M:%S')}'")
    
    if filters:
        return 'WHERE '+ ' AND '.join(filters)
    else:
        return ''