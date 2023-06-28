import tkinter
from tkinter import ttk, font, messagebox
from datetime import datetime
import os
import pyodbc

class Logging_tab(tkinter.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
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

        fill_table(table)
    
    #Buttons
        update_button = ttk.Button(self, text="Update", command=lambda: update_table(parent, table))
        update_button.pack()

        
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

def fill_table(table: ttk.Treeview):
    for i in range(100):
        data = (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), ('Error', 'Info', 'Trace')[i%3], f"Level{i}", f"Message{i}"*i)
        table.insert('', 'end', values=data)
    resize_table(table)

def update_table(app, table: ttk.Treeview):
    try:
        conn = pyodbc.connect(app.connection_string)
        cursor = conn.execute("SELECT TOP(10) * FROM Logs ORDER BY Time DESC")   
    except:
        messagebox.showerror("Error", "Connection failed! Go to settings and enter a valid connection string.")
    
    #Clear table
    for c in table.get_children():
        table.delete(c)

    for row in cursor:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)
    
    resize_table(table)

