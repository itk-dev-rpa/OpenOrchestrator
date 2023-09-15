import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.Orchestrator import DB_util, Crypto_util

def show_popup(name=None, username=None):
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Credential")
    window.geometry("300x300")

    ttk.Label(window, text="Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Username:").pack()
    username_entry = ttk.Entry(window)
    username_entry.pack()

    ttk.Label(window, text="Password:").pack()
    password_entry = ttk.Entry(window)
    password_entry.pack()

    def create_command(): create_credential(window, name_entry,username_entry, password_entry)
    ttk.Button(window, text='Create', command=create_command).pack()
    ttk.Button(window, text='Cancel', command=window.destroy).pack()

    if name:
        name_entry.insert('end', name)
    if username:
        username_entry.insert('end', username)

    return window

def create_credential(window, name_entry: ttk.Entry,
                      username_entry: ttk.Entry, password_entry:ttk.Entry):
    name = name_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a name')
        return

    if not username:
        messagebox.showerror('Error', 'Please enter a username')
        return
    
    if not password:
        messagebox.showerror('Error', 'Please enter a password')
        return
    
    credentials = DB_util.get_credentials()
    exists = any(c[0] == name for c in credentials)
    
    if exists and not messagebox.askyesno('Error', 'A credential with that name already exists. Do you want to overwrite it?'):
        return
    
    DB_util.delete_credential(name)

    # username = Crypto_util.encrypt_data(username)
    password = Crypto_util.encrypt_string(password)

    DB_util.create_credential(name, username, password)

    window.destroy()
