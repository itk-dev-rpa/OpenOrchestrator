import tkinter
from tkinter import ttk, messagebox
import sys


def create_tab(parent, app):
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
    
    status_label = ttk.Label(tab, text="Status: Paused")
    status_label.pack()

    ttk.Button(tab, text="Run", command=lambda: run(status_label)).pack()
    ttk.Button(tab, text="Pause", command=lambda: pause(status_label)).pack()

    text_area = tkinter.Text(tab, state='disabled')
    text_area.pack()
    sys.stdout.write = lambda s: print_text(text_area, s)

    return tab

def run(status_label: ttk.Label):
    status_label.configure(text='Status: Running')
    print('Running...')

def pause(status_label: ttk.Label):
    status_label.configure(text="Status: Paused")
    print('Paused...')

def print_text(print_text: tkinter.Text, string: str):
    print_text.configure(state='normal')
    print_text.insert('end', string)
    print_text.configure(state='disabled')