"""This module contains convenience functions related to ttk.Treeview objects."""

import os

from nicegui import ui

def create_table(title: str, column_labels: list[str], pagination: int = 5) -> ui.table:
    columns = [{'id': label, 'label': label, 'field': label, 'align': 'left'} for label in column_labels]
    table = ui.table(columns, [], title=title, pagination=pagination, row_key='ID')
    table.classes("w-full")
    return table

    

'''def copy_selected_rows_to_clipboard(table: ttk.Treeview) -> None:
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
    pass


def deselect_tables(*tables) -> None:
    """Deselects all selected rows in the given tables."""    
    pass
'''