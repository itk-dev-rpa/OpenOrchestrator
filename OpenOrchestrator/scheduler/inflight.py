"""Per-machine registry of in-flight trigger IDs.

Used by :mod:`OpenOrchestrator.scheduler.runner` to remember which triggers
this scheduler instance has flipped to RUNNING in the database but has not
yet finished cleanly. The registry is persisted as a small JSON file so it
survives a scheduler crash or reboot:

- ``runner.run_trigger`` calls :func:`add` after the DB row is set to RUNNING.
- ``runner.end_job`` / ``runner.fail_job`` / ``runner.kill_job`` call
  :func:`remove` once the job has finished.
- ``runner.reconcile_orphans`` reads the registry on scheduler startup and
  marks any still-RUNNING orphans as FAILED.

Without this, a scheduler that crashes between ``begin_*_trigger`` and the
job finishing leaves the trigger in RUNNING state with no real process,
and the pending-trigger queries (which only look at IDLE rows) never pick
it up again. See issues #152 and #106.

The file lives at ``%APPDATA%\\OpenOrchestrator\\inflight.json`` on Windows
and ``~/.OpenOrchestrator/OpenOrchestrator/inflight.json`` elsewhere.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Iterable
from uuid import UUID

_LOCK = threading.Lock()


def _path() -> Path:
    """Return the in-flight JSON file path, creating parent dirs as needed.

    Returns:
        Absolute path to ``inflight.json`` in the per-user data directory.
    """
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / ".OpenOrchestrator"
    folder = base / "OpenOrchestrator"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "inflight.json"


def _load() -> list[str]:
    """Read the persisted in-flight list.

    Returns:
        List of trigger IDs as strings, or ``[]`` if the file is missing,
        unreadable, or malformed.
    """
    p = _path()
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(x) for x in data]
            return []
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: Iterable[str]) -> None:
    """Atomically replace the persisted in-flight list.

    Writes to a temporary file in the same directory and then ``os.replace``\\ s
    it over the destination, which is atomic on both Windows and POSIX.

    Args:
        items: Trigger IDs (as strings) to persist.
    """
    p = _path()
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(list(items), f)
    os.replace(tmp, p)


def add(trigger_id: UUID | str) -> None:
    """Record that this scheduler is now running the given trigger.

    No-op if the ID is already present.

    Args:
        trigger_id: Identifier of the trigger that was just flipped to RUNNING.
    """
    s = str(trigger_id)
    with _LOCK:
        items = _load()
        if s not in items:
            items.append(s)
            _save(items)


def remove(trigger_id: UUID | str) -> None:
    """Record that this scheduler has finished with the given trigger.

    No-op if the ID is not present.

    Args:
        trigger_id: Identifier of the trigger whose job just ended.
    """
    s = str(trigger_id)
    with _LOCK:
        items = _load()
        if s in items:
            items.remove(s)
            _save(items)


def get_all() -> list[str]:
    """Return all trigger IDs currently marked as in-flight on this machine.

    Returns:
        Snapshot of the trigger ID list at the time of the call.
    """
    with _LOCK:
        return _load()


def clear() -> None:
    """Forget every in-flight trigger.

    Provided for tests and manual recovery; not used by the scheduler itself.
    """
    with _LOCK:
        _save([])
