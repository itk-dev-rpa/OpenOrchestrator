"""Scheduler app: tkinter-based runner for triggered processes.

Polls the database for due triggers and launches the configured
processes. Uses tkinter (rather than NiceGUI) because it runs as a
local desktop process on the RPA worker machine. Started via
``python -m OpenOrchestrator s``.
"""
