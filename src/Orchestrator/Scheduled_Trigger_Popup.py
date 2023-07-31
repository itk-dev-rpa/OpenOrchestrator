import tkinter
from tkinter import ttk, messagebox
import croniter
from datetime import datetime
from DB_util import catch_db_error
import webbrowser

def show_popup(app):
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

    ttk.Button(window, text='Create', command=lambda: create_trigger(app, window, name_entry, cron_entry, path_entry, git_check, blocking_check)).pack()
    ttk.Button(window, text='Cancel', command=lambda: window.destroy()).pack()

    return window

@catch_db_error
def create_trigger(app, window,
                   name_entry: ttk.Entry, cron_entry: ttk.Entry, 
                   path_entry: ttk.Entry, git_check: tkinter.IntVar, blocking_check: tkinter.IntVar):
    
    name = name_entry.get()
    cron = cron_entry.get()
    path = path_entry.get()
    git = git_check.get()
    blocking = blocking_check.get()

    if not name:
        messagebox.showerror('Error', 'Please enter a process name')
        return

    try:
        c = croniter.croniter(cron, datetime.now(), day_or=False)
        date = c.get_next(datetime)
    except Exception as e:
        messagebox.showerror('Error', 'Please enter a valid cron expression\n'+str(e))
        return

    if not path:
        messagebox.showerror('Error', 'Please enter a process path')
        return
    
    # Create trigger in database
    conn = app.get_db_connection()

    with open('SQL/Create_Scheduled_Trigger.sql') as file:
        command = file.read()
    
    command = command.replace('{NAME}', str(name))
    command = command.replace('{CRON}', str(cron))
    command = command.replace('{DATE}', date.strftime('%d-%m-%Y %H:%M:%S'))
    command = command.replace('{PATH}', str(path))
    command = command.replace('{GIT}', str(git))
    command = command.replace('{BLOCKING}', str(blocking))

    conn.execute(command).commit()

    window.destroy()



    
