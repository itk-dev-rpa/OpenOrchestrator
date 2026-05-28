# Architecture

This document gives new developers a working mental model of OpenOrchestrator. For end-user docs see the [docs site](https://itk-dev-rpa.github.io/OpenOrchestrator-docs/).

## Components

OpenOrchestrator is a single Python package that ships **three deployable parts**, all backed by one shared database.

| Component | Stack | Entry point | Purpose |
|---|---|---|---|
| **Orchestrator** | NiceGUI (web) | `python -m OpenOrchestrator o` | Admin UI: triggers, queues, jobs, logs, constants, credentials |
| **Scheduler** | tkinter (desktop) | `python -m OpenOrchestrator s` | Polls the DB for due triggers and launches the configured Python processes on a worker machine |
| **OrchestratorConnection** | library | imported by RPA scripts | SDK that the launched processes use to log, fetch credentials/constants, and read/write queue elements |

The Orchestrator and Scheduler communicate **only through the database** — there is no direct RPC. Many Schedulers can run against one Orchestrator/database; jobs are dispatched via the trigger `priority` field and an optional `scheduler_whitelist`.

### Why tkinter for Scheduler?

The Scheduler is intentionally a local desktop process: it runs on the RPA worker machine where the bots execute, often unattended, and needs no remote UI. The Orchestrator is a web admin app and uses NiceGUI. The two settings tabs ([scheduler/settings_tab.py](../OpenOrchestrator/scheduler/settings_tab.py) vs [orchestrator/tabs/settings_tab.py](../OpenOrchestrator/orchestrator/tabs/settings_tab.py)) deliberately use different UI stacks for this reason — do not "consolidate" them.

## Data model

All ORM classes inherit from a single SQLAlchemy `DeclarativeBase` in [database/base.py](../OpenOrchestrator/database/base.py). Tables:

- **Triggers** — polymorphic on `type` ([database/triggers.py](../OpenOrchestrator/database/triggers.py)):
  - `SingleTrigger` — runs once at `next_run`.
  - `ScheduledTrigger` — recurring, driven by a `cron_expr` (cronsim).
  - `QueueTrigger` — fires when at least `min_batch_size` elements with status `NEW` exist for `queue_name`.
  - Common fields: `process_path` (file path or git URL), `is_git_repo`, `git_branch`, `is_blocking`, `priority`, `scheduler_whitelist`, `process_status`.
- **Queues** — [database/queues.py](../OpenOrchestrator/database/queues.py). Work items consumed by `QueueTrigger`-driven processes. Status: `NEW → IN_PROGRESS → DONE | FAILED | ABANDONED`.
- **Jobs** — [database/jobs.py](../OpenOrchestrator/database/jobs.py). One row per launched process. Tracks `start_time`, `end_time`, `status` (`RUNNING/DONE/FAILED/KILLED`) and the `scheduler_name` that launched it.
- **Logs** — [database/logs.py](../OpenOrchestrator/database/logs.py). Trace/Info/Error entries written by processes via `OrchestratorConnection`. Linked to a `Job` via `job_id`.
- **Schedulers** — [database/schedulers.py](../OpenOrchestrator/database/schedulers.py). Heartbeat row per running Scheduler instance (`machine_name` is PK).
- **Constants / Credentials** — [database/constants.py](../OpenOrchestrator/database/constants.py). Shared config; credential passwords are AES-encrypted with a key managed by [common/crypto_util.py](../OpenOrchestrator/common/crypto_util.py).

Schema migrations live under [alembic_migrations/](../alembic_migrations/) and are applied via `python -m OpenOrchestrator upgrade <conn_string>`.

## Trigger lifecycle

Implemented in [scheduler/runner.py](../OpenOrchestrator/scheduler/runner.py).

```
            ┌─────────┐
            │  IDLE   │◄────────────────────┐
            └────┬────┘                     │
                 │ poll_triggers picks it   │ end_job (recurring)
                 ▼                          │
            ┌─────────┐   process exits ok  │
   ┌───────►│ RUNNING ├──────────────────►──┘
   │        └────┬────┘
   │             │ user disables in UI
   │             ▼                process exits
   │        ┌─────────┐           ┌─────────┐
   │        │ PAUSING ├────────►──┤ PAUSED  │
   │        └────┬────┘           └────┬────┘
   │             │ user re-enables     │ user re-enables
   │             └─────────────────────┘
   │
   │  uncaught exception          user kills via UI
   │        │                            │
   │        ▼                            ▼
   │   ┌────────┐                  ┌─────────┐  taskkill   ┌────────┐
   │   │ FAILED │                  │ KILLING ├────────────►│ KILLED │
   │   └────────┘                  └─────────┘             └────────┘
   │
   └── Single triggers go to DONE on success (terminal state)
```

`poll_triggers` sorts pending triggers by `(-priority, type)` where Single > Scheduled > Queue. `is_blocking=True` triggers wait for any other running job on the same Scheduler to finish.

## Process launch

When the Scheduler runs a trigger, it:

1. Optionally clones a git repo (`is_git_repo=True`) into `~/Desktop/Scheduler_Repos/<uuid>/` and finds `main.py`.
2. Spawns a Python subprocess with `[python, path, process_name, conn_string, crypto_key, args, trigger_id, job_id]`.
3. The launched process receives those args and instantiates `OrchestratorConnection.create_connection_from_args()` to log, fetch credentials, etc.
4. On exit, the Scheduler updates trigger and job status, then deletes the cloned repo folder if any.

## Package layout

```
OpenOrchestrator/
├── __main__.py                 # CLI: o | s | upgrade
├── common/                     # Shared utils (datetime, crypto, NiceGUI connection frame)
├── database/                   # ORM models + query helpers (db_util et al.) + Alembic data types
├── orchestrator/               # NiceGUI admin app
│   ├── application.py          # NiceGUI app entry
│   ├── tabs/                   # Top-level tabs (triggers, queues, jobs, logs, constants, schedulers, settings)
│   ├── popups/                 # Modal create/edit dialogs (BasePopup-based)
│   ├── ui_util.py              # UI test instrumentation (auto-id props for Selenium)
│   ├── datetime_input.py       # Custom date/time picker
│   └── input_chips_blur.py     # Custom InputChips with blur-event commit
├── scheduler/                  # tkinter runner
│   ├── application.py
│   ├── runner.py               # Trigger polling + process lifecycle (see above)
│   ├── run_tab.py              # Run tab UI
│   ├── settings_tab.py         # Connection settings UI (tkinter)
│   └── util.py                 # Scheduler name resolution etc.
├── orchestrator_connection/    # Public SDK consumed by RPA scripts
│   └── connection.py
└── tests/
    ├── *.py                    # Unit + integration tests (unittest, against SQLite or MSSQL)
    └── ui_tests/               # Selenium-based UI tests
```

## See also

- Diagram sources: [.Illustrations/Architecture.drawio](../.Illustrations/Architecture.drawio), [.Illustrations/Scheduler.drawio](../.Illustrations/Scheduler.drawio)
- Contributing guide: [CONTRIBUTING.md](../CONTRIBUTING.md)
- Changelog: [changelog.md](../changelog.md)
