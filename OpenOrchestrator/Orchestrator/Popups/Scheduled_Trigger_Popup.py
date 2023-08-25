import tkinter
from tkinter import ttk, messagebox
import croniter
from datetime import datetime
import DB_util
import webbrowser

def show_popup():
    window = tkinter.Toplevel()
    window.grab_set()
    window.title("New Single Trigger")
    window.geometry("300x300")

    ttk.Label(window, text="Process Name:").pack()
    name_entry = ttk.Entry(window)
    name_entry.pack()

    ttk.Label(window, text="Cron Expression:").pack()
    cron_entry = ttk.Entry(window)
    cron_entry.pack()

    help_label = ttk.Label(window, text='Cron Help', cursor='hand2', foreground='blue')
    help_label.bind('<Button-1>', lambda e: webbrowser.open('crontab.guru'))
    help_label.pack()

    ttk.Label(window, text="Process Path:").pack()
    path_entry = ttk.Entry(window)
    path_entry.pack()

    git_check = tkinter.IntVar()
    ttk.Checkbutton(window, text="Is Git Repo?", variable=git_check).pack()

    blocking_check = tkinter.IntVar()
    ttk.Checkbutton(window, text="Is Blocking?", variable=blocking_check).pack()

    ttk.Button(window, text='Create', command=lambda: create_trigger(window, name_entry, cron_entry, path_entry, git_check, blocking_check)).pack()
    ttk.Button(window, text='Cancel', command=lambda: window.destroy()).pack()

    return window

def create_trigger(window,
                   name_entry: ttk.Entry, cron_entry: ttk.Entry, 
                   path_entry: ttk.Entry, git_check: tkinter.IntVar, blocking_check: tkinter.IntVar):
    
    name = name_entry.get()
    cron = cron_entry.get()
    path = path_entry.get()
    is_git = git_check.get()
    is_blocking = blocking_check.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a process name')
        return

    try:
        c = croniter.croniter(cron, datetime.now())
        date = c.get_next(datetime)
    except Exception as e:
        messagebox.showerror('Error', 'Please enter a valid cron expression\n'+str(e))
        return

    if not path:
        messagebox.showerror('Error', 'Please enter a process path')
        return
    
    # Create trigger in database
    DB_util.create_scheduled_trigger(name, cron, date, path, is_git, is_blocking)

    window.destroy()



    
