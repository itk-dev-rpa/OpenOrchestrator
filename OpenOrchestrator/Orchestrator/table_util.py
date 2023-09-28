"""This module contains convenience functions related to ttk.Treeview objects."""

from tkinter import ttk
import os

def create_table(parent: ttk.Frame, columns: list[str]):
    """Create a ttk.Treeview with horizontal and vertical scroll bars
    and with the given column names.
    Bind ctrl+c to copy selection to the clipboard.

    Args:
        parent: The parent frame of the table and scroll bars.
        columns: A list of column names.

    Returns:
        ttk.Treeview: The created table (treeview).
    """
    table = ttk.Treeview(parent, show='headings', selectmode='browse')
    table['columns'] = columns
    for column in table['columns']:
        table.heading(column, text=column, anchor='w')
        table.column(column, stretch=False)

    yscroll = ttk.Scrollbar(parent, orient='vertical', command=table.yview)
    yscroll.pack(side='right', fill='y')
    table.configure(yscrollcommand=yscroll.set)

    xscroll = ttk.Scrollbar(parent, orient='horizontal', command=table.xview)
    xscroll.pack(side='bottom', fill='x')
    table.configure(xscrollcommand=xscroll.set)

    table.pack(expand=True, fill='both')

    table.bind("<Control-c>", lambda e: copy_selected_rows_to_clipboard(table))

    return table


def copy_selected_rows_to_clipboard(table: ttk.Treeview) -> None:
    """Copies the values of the selected rows in the table to the clipboard.

    Args:
        table: The table to copy from.
    """
    if len(table.selection()) == 0:
        return

    items = []
    for row_id in table.selection():
        values = table.item(row_id, "values")
        items.append(f'echo "{values}"')
    string = '('+' & '.join(items)+')'
    os.system(f"{string} | clip")


def update_table(table: ttk.Treeview, rows: list[list[any]]) -> None:
    """Deletes all rows in the table and inserts the given values.

    Args:
        table: The table whose values to replace.
        rows: The new row values to insert.
    """
    #Clear table
    for row in table.get_children():
        table.delete(row)

    #Update table
    for row in rows:
        row = [str(d) for d in row]
        table.insert('', 'end', values=row)


def deselect_tables(*tables) -> None:
    """Deselects all selected rows in the given tables."""    
    for table in tables:
        table.selection_remove(table.selection())
