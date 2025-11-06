"""This module contains miscellaneous utility functions."""

import platform


def get_scheduler_name():
    """Get the name of the Scheduler application."""
    return platform.node()
