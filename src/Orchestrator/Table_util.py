from tkinter import ttk
import os

def create_table(parent, columns):
    table = ttk.Treeview(parent, show='headings', selectmode='browse')
    table['columns'] = columns
    for c in table['columns']:
        table.heading(c, text=c, anchor='w')
        table.column(c, stretch=False)
    
    yscroll = ttk.Scrollbar(parent, orient='vertical', command=table.yview)
    yscroll.pack(side='right', fill='y')
    table.configure(yscrollcommand=yscroll.set)

    xscroll = ttk.Scrollbar(parent, orient='horizontal', command=table.xview)
    xscroll.pack(side='bottom', fill='x')
    table.configure(xscrollcommand=xscroll.set)

    table.pack(expand=True, fill='both')

    table.bind("<Control-c>", lambda e: copy_selected_rows_to_clipboard(table))

    return table

def copy_selected_rows_to_clipboard(table):
    string = "("
    for item in table.selection():
        string += f'echo "{str(table.item(item)["values"])}" & '
    string = string.rstrip("& ")
    string += ")"
    os.system(f"{string} | clip")

def update_table(table: ttk.Treeview, rows):
    #Clear table
    for c in table.get_children():
        table.delete(c)

    #Update table
    for row in rows:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)

def deselect_tables(*tables):
    for table in tables:
        table.selection_remove(table.selection())