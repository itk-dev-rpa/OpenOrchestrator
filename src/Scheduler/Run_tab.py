import tkinter
from tkinter import ttk
import sys
import Runner, DB_util, Crypto_util

def create_tab(parent, app):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
    
    status_label = ttk.Label(tab, text="State: Paused")
    status_label.pack()

    ttk.Button(tab, text="Run", command=lambda: run(app, status_label)).pack()
    ttk.Button(tab, text="Pause", command=lambda: pause(app, status_label)).pack()

    # Text area
    text_frame = tkinter.Frame(tab)
    text_frame.pack()

    text_area = tkinter.Text(text_frame, state='disabled', wrap='none')
    sys.stdout.write = lambda s: print_text(text_area, s)

    text_yscroll = ttk.Scrollbar(text_frame, orient='vertical', command=text_area.yview)
    text_yscroll.pack(side='right', fill='y')
    text_area.configure(yscrollcommand=text_yscroll.set)

    text_xscroll = ttk.Scrollbar(text_frame, orient='horizontal', command=text_area.xview)
    text_xscroll.pack(side='bottom', fill='x')
    text_area.configure(xscrollcommand=text_xscroll.set)

    text_area.pack()

    return tab

def run(app, status_label: ttk.Label):
    if DB_util.get_conn_string() is None:
        print("Can't start without a valid connection string. Go to the settings tab to configure the connection string")
        return
    if Crypto_util.get_key() is None:
        print("Can't start without a valid encryption key. Go to the settings tab to configure the encryption key")
        return

    if not app.running:
        status_label.configure(text='State: Running')
        print('Running...\n')
        app.running = True

        # Only start loop if it's not already running
        if app.tk.call('after', 'info') == '':
            app.after(0, loop, app)

def pause(app, status_label: ttk.Label):
    if app.running:
        status_label.configure(text="State: Paused")
        print('Paused... Please wait for all processes to stop before closing the application\n')
        app.running = False

def print_text(print_text: tkinter.Text, string: str):
    print_text.configure(state='normal')
    print_text.insert('end', string)
    print_text.see('end')
    print_text.configure(state='disabled')

def loop(app):  
    check_heartbeats(app)

    if app.running:
        check_triggers(app)

    # Schedule next loop
    if app.running or len(app.running_jobs) > 0:
        print('Waiting 6 seconds...\n')
        app.after(6_000, loop, app)
    else:
        print("Scheduler is paused and no more processes are running.")
    
def check_heartbeats(app):
    print('Checking heartbeats...')
    for j in app.running_jobs:
        if j.process.poll() is not None:
            app.running_jobs.remove(j)

            if j.process.returncode == 0:
                print(f"Process '{j.process_name}' is done")
                Runner.end_job(j)
            else:
                print(f"Process '{j.process_name}' failed")
                Runner.fail_job(j)

        else:
            print(f"Process '{j.process_name}' is still running")

def check_triggers(app):
    #Check if process is blocking
    blocking = False
    for j in app.running_jobs:
        if j.blocking:
            print(f"Process '{j.process_name}' is blocking\n")
            blocking = True

    # Check triggers
    if not blocking:
        print('Checking triggers...')
        job = Runner.poll_triggers(app)

        if job is not None:
            app.running_jobs.append(job)