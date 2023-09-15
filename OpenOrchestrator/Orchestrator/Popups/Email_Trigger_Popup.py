import tkinter
from tkinter import ttk, messagebox

from OpenOrchestrator.Orchestrator import DB_util

def show_popup():
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Email Trigger")
    window.geometry("300x300")

    ttk.Label(window, text="Process Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Email Folder:").pack()
    folder_entry = ttk.Entry(window)
    folder_entry.pack()

    ttk.Label(window, text="Process Path:").pack()
    path_entry = ttk.Entry(window)
    path_entry.pack()

    ttk.Label(window, text="Arguments:").pack()
    args_entry = ttk.Entry(window)
    args_entry.pack()

    git_check = tkinter.IntVar()
    ttk.Checkbutton(window, text="Is Git Repo?", variable=git_check).pack()

    blocking_check = tkinter.IntVar()
    ttk.Checkbutton(window, text="Is Blocking?", variable=blocking_check).pack()

    def create_command(): create_trigger(window, name_entry, folder_entry, path_entry, args_entry, git_check, blocking_check)
    ttk.Button(window, text='Create', command=create_command).pack()
    ttk.Button(window, text='Cancel', command=window.destroy).pack()

    return window

def create_trigger(window,
                   name_entry: ttk.Entry, folder_entry: ttk.Entry, 
                   path_entry: ttk.Entry, args_entry: ttk.Entry,
                   git_check: tkinter.IntVar, blocking_check: tkinter.IntVar):
    
    name = name_entry.get()
    folder = folder_entry.get()
    path = path_entry.get()
    args = args_entry.get()
    is_git = git_check.get()
    is_blocking = blocking_check.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a process name')
        return

    if not folder:
        messagebox.showerror('Error', 'Please enter a folder name')
        return

    if not path:
        messagebox.showerror('Error', 'Please enter a process path')
        return
    
    # Create trigger in database
    DB_util.create_email_trigger(name, folder, path, args, is_git, is_blocking)

    window.destroy()



    
