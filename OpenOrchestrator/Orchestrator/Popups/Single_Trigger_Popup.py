import tkinter
from tkinter import ttk, messagebox
import tkcalendar
from datetime import datetime
from OpenOrchestrator.Orchestrator import DB_util

def show_popup():
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Single Trigger")
    window.geometry("300x300")

    ttk.Label(window, text="Process Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Trigger Date:").pack()
    date_entry = tkcalendar.DateEntry(window, date_pattern='dd/MM/yyyy')
    date_entry.pack()

    ttk.Label(window, text="Trigger Time:").pack()
    time_entry = ttk.Entry(window)
    time_entry.insert(0, 'tt:mm')
    time_entry.pack()

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

    ttk.Button(window, text='Create', command=lambda: create_trigger(window, name_entry, date_entry, time_entry, path_entry, args_entry, git_check, blocking_check)).pack()
    ttk.Button(window, text='Cancel', command=lambda: window.destroy()).pack()

    return window

def create_trigger(window,
                   name_entry: ttk.Entry, date_entry: tkcalendar.DateEntry, 
                   time_entry: ttk.Entry, path_entry: ttk.Entry, args_entry: ttk.Entry,
                   git_check: tkinter.IntVar, blocking_check: tkinter.IntVar):
    
    name = name_entry.get()
    date = date_entry.get_date()
    time = time_entry.get()
    path = path_entry.get()
    args = args_entry.get()
    is_git = git_check.get()
    is_blocking = blocking_check.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a process name')
        return

    try:
        hour, minute = time.split(":")
        hour, minute = int(hour), int(minute)
        date = datetime(date.year, date.month, date.day, hour, minute)
    except Exception as e:
        messagebox.showerror('Error', "Please enter a valid time in the format 'tt:mm'\n"+str(e))
    
    if date < datetime.now():
        if not messagebox.askyesno('Warning', "The selected datetime is in the past. Do you want to create the trigger anyway?"):
            return

    if not path:
        messagebox.showerror('Error', 'Please enter a process path')
        return
    
    # Create trigger in database
    DB_util.create_single_trigger(name, date, path, args, is_git, is_blocking)

    window.destroy()



    
