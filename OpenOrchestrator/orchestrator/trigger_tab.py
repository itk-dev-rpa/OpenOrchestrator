"""This module is responsible for the layout and functionality of the Trigger tab
in Orchestrator."""

from tkinter import ttk, messagebox

from OpenOrchestrator.database import db_util
from OpenOrchestrator.database.triggers import Trigger, TriggerStatus
from OpenOrchestrator.orchestrator import table_util
from OpenOrchestrator.orchestrator.popups import queue_trigger_popup, single_trigger_popup, scheduled_trigger_popup


def create_tab(parent: ttk.Notebook) -> ttk.Frame:
    """Create a new Trigger tab object.

    Args:
        parent: The ttk.Notebook object that this tab is a child of.

    Returns:
        ttk.Frame: The created tab object as a ttk.Frame.
    """
    tab = ttk.Frame(parent)
    tab.pack(fill='both', expand=True)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure((0,2,4), weight=1, uniform='a')
    tab.rowconfigure((1,3,5), weight=6, uniform='a')
    tab.rowconfigure((6,7), weight=1, uniform='a')

    #Scheduled table
    ttk.Label(tab, text="Scheduled Triggers").grid(row=0, column=0)
    sc_table_frame = ttk.Frame(tab)
    sc_table_frame.grid(row=1, column=0, sticky='nsew')
    sc_table = table_util.create_table(sc_table_frame, ('Trigger Name', 'Status', 'Process Name', 'Cron', 'Last run', 'Next run', 'Path', 'Arguments', 'Is GIT?', 'Blocking?', 'UUID'))

    #Queue table
    ttk.Label(tab, text="Queue Triggers").grid(row=2, column=0)
    q_table_frame = ttk.Frame(tab)
    q_table_frame.grid(row=3, column=0, sticky='nsew')
    q_table = table_util.create_table(q_table_frame, ('Trigger Name', 'Status', 'Process Name', 'Queue Name', 'Min batch size', 'Last run', 'Path', 'Arguments', 'Is GIT?', 'Blocking?', 'UUID'))

    #Single table
    ttk.Label(tab, text="Single Triggers").grid(row=4, column=0)
    si_table_frame = ttk.Frame(tab)
    si_table_frame.grid(row=5, column=0, sticky='nsew')
    si_table = table_util.create_table(si_table_frame, ('Trigger Name', 'Status', 'Process Name', 'Last run', 'Next run', 'Path', 'Arguments', 'Is GIT?', 'Blocking?', 'UUID'))

    # Controls 1
    controls_frame = ttk.Frame(tab)
    controls_frame.grid(row=6, column=0)
    def update_command():
        update_tables(sc_table, q_table, si_table)

    update_button = ttk.Button(controls_frame, text='Update tables', command=update_command)
    update_button.pack(side='left')

    reenable_button = ttk.Button(controls_frame, text="Reenable", command=lambda: set_trigger_status(TriggerStatus.IDLE, sc_table, q_table, si_table))
    reenable_button.pack(side='left')

    pause_button = ttk.Button(controls_frame, text="Pause", command=lambda: set_trigger_status(TriggerStatus.PAUSED, sc_table, q_table, si_table))
    pause_button.pack(side='left')

    delete_button = ttk.Button(controls_frame, text='Delete', command=lambda: delete_trigger(sc_table, q_table, si_table))
    delete_button.pack(side='left')

    # Controls 2
    controls_frame2 = ttk.Frame(tab)
    controls_frame2.grid(row=7, column=0)

    ttk.Button(controls_frame2, text='New scheduled trigger', command=lambda: show_scheduled_trigger_popup(update_command)).pack(side='left')
    ttk.Button(controls_frame2, text='New queue trigger', command=lambda: show_queue_trigger_popup(update_command)).pack(side='left')
    ttk.Button(controls_frame2, text='New single trigger', command=lambda: show_single_trigger_popup(update_command)).pack(side='left')

    # Bindings
    sc_table.bind('<FocusIn>', lambda e: table_util.deselect_tables(q_table, si_table))
    q_table.bind('<FocusIn>', lambda e: table_util.deselect_tables(sc_table, si_table))
    si_table.bind('<FocusIn>', lambda e: table_util.deselect_tables(sc_table, q_table))

    return tab


def show_scheduled_trigger_popup(on_close: callable) -> None:
    """Shows the new scheduled trigger popup.
    Binds a callable to the popup's on_close event.

    Args:
        on_close: on_close: A function to be called when the popup closes.
    """
    popup = scheduled_trigger_popup.show_popup()
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)


def show_single_trigger_popup(on_close: callable) -> None:
    """Shows the new single trigger popup.
    Binds a callable to the popup's on_close event.

    Args:
        on_close: on_close: A function to be called when the popup closes.
    """
    popup = single_trigger_popup.show_popup()
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)


def show_queue_trigger_popup(on_close: callable) -> None:
    """Shows the new queue trigger popup.
    Binds a callable to the popup's on_close event.

    Args:
        on_close: on_close: A function to be called when the popup closes.
    """
    popup = queue_trigger_popup.show_popup()
    popup.bind('<Destroy>', lambda e: on_close() if e.widget == popup else ...)


def update_tables(sc_table: ttk.Treeview, q_table: ttk.Treeview, si_table: ttk.Treeview):
    """Updates all three trigger tables
    with values from the database.

    Args:
        sc_table: The scheduled table.
        q_table: The queue table.
        si_table: The single table.
    """
    scheduled_triggers = db_util.get_scheduled_triggers()
    sc_list = [t.to_tuple() for t in scheduled_triggers]

    queue_triggers = db_util.get_queue_triggers()
    q_list = [t.to_tuple() for t in queue_triggers]

    single_triggers = db_util.get_single_triggers()
    si_list = [t.to_tuple() for t in single_triggers]

    table_util.update_table(sc_table, sc_list)
    table_util.update_table(q_table, q_list)
    table_util.update_table(si_table, si_list)


def delete_trigger(sc_table: ttk.Treeview, q_table: ttk.Treeview, si_table: ttk.Treeview) -> None:
    """Deletes the currently selected trigger from either
    of the three trigger tables.
    Shows a confirmation dialog before deleting.

    Args:
        sc_table: The scheduled table.
        q_table: The queue table.
        si_table: The single table.
    """
    trigger = get_selected_trigger(sc_table, q_table, si_table)

    if trigger is None:
        messagebox.showinfo("No trigger selected", "No trigger is selected.")
        return

    if not messagebox.askyesno('Delete trigger', f"Are you sure you want to delete trigger '{trigger.trigger_name} - {trigger.id}'?"):
        return

    db_util.delete_trigger(trigger.id)

    update_tables(sc_table, q_table, si_table)


def set_trigger_status(status: TriggerStatus, sc_table: ttk.Treeview, q_table: ttk.Treeview, si_table: ttk.Treeview) -> None:
    """Set the status of the currently selected trigger.

    Args:
        status: The new status to apply.
        sc_table: The scheduled table.
        q_table: The queue table.
        si_table: The single table.
    """
    trigger = get_selected_trigger(sc_table, q_table, si_table)

    if trigger is None:
        messagebox.showinfo("No trigger selected", "No trigger is selected.")
        return

    db_util.set_trigger_status(trigger.id, status)

    update_tables(sc_table, q_table, si_table)

    messagebox.showinfo("Trigger status changed", f"The status of {trigger.trigger_name} has been set to {status.value}")


def get_selected_trigger(sc_table: ttk.Treeview, q_table: ttk.Treeview, si_table: ttk.Treeview) -> Trigger:
    """Get the currently selected trigger across all three tables.

    Args:
        sc_table: The scheduled table.
        q_table: The queue table.
        si_table: The single table.

    Returns:
        Trigger: The ORM trigger object with the given id.
    """
    if sc_table.selection():
        table = sc_table
    elif q_table.selection():
        table = q_table
    elif si_table.selection():
        table = si_table
    else:
        return None

    trigger_id = table.item(table.selection()[0])['values'][-1]
    return db_util.get_trigger(trigger_id)
