import tkinter
from tkinter import ttk, messagebox
import tkcalendar
from datetime import datetime
from OpenOrchestrator.Orchestrator import DB_util

def show_popup(name=None, value=None):
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Constant")
    window.geometry("300x300")

    ttk.Label(window, text="Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Value:").pack()
    value_entry = ttk.Entry(window)
    value_entry.pack()

    ttk.Button(window, text='Create', command=lambda: create_constant(window, name_entry,value_entry)).pack()
    ttk.Button(window, text='Cancel', command=lambda: window.destroy()).pack()

    if name:
        name_entry.insert('end', name)
    if value:
        value_entry.insert('end', value)

    return window

def create_constant(window, name_entry: ttk.Entry, value_entry: ttk.Entry):
    name = name_entry.get()
    value = value_entry.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a name')
        return

    if not value:
        messagebox.showerror('Error', 'Please enter a value')
        return
    
    constants = DB_util.get_constants()
    exists = any(c[0].lower() == name.lower() for c in constants)
    
    if exists:
        if not messagebox.askyesno('Error', 'A constant with that name already exists. Do you want to overwrite it?'):
            return
        else:
            DB_util.delete_constant(name)
            
    DB_util.create_constant(name, value)

    window.destroy()
