# OpenOrchestrator

OpenOrchestrator is a Python toolkit for orchestrating, monitoring, and running automation scripts (RPA bots) on Windows. It ships an admin web UI (Orchestrator), a worker-side runner (Scheduler), and an SDK that bots use to log, fetch credentials and manage queue work.

End-user documentation: [OpenOrchestrator-docs](https://itk-dev-rpa.github.io/OpenOrchestrator-docs).
Package on PyPI: [OpenOrchestrator](https://pypi.org/project/OpenOrchestrator/).

## Architecture

| Component | Purpose | Started by |
|---|---|---|
| **Orchestrator** | NiceGUI admin UI for triggers, queues, jobs, logs, constants, credentials | `python -m OpenOrchestrator o` |
| **Scheduler** | tkinter runner that polls the DB and launches due processes | `python -m OpenOrchestrator s` |
| **OrchestratorConnection** | SDK imported by RPA scripts for logging and DB access | `from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection` |

Components communicate **only through a shared SQL database** (MSSQL or SQLite). For the data model, trigger lifecycle, and process launch flow, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

### Project layout

```
OpenOrchestrator/
├── common/                 Shared utilities (datetime, crypto, NiceGUI connection frame)
├── database/               SQLAlchemy ORM + query helpers + Alembic data types
├── orchestrator/           NiceGUI admin app (tabs, popups)
├── scheduler/              tkinter runner (poll loop, process lifecycle)
├── orchestrator_connection/  Public SDK consumed by RPA scripts
└── tests/                  Unit + Selenium UI tests
```

## Usage for Orchestrator admins

OpenOrchestrator provides a CLI for the deployable parts. For full help run `python -m OpenOrchestrator -h`.

```bash
python -m OpenOrchestrator o    # Start the Orchestrator (web UI)
python -m OpenOrchestrator s    # Start a Scheduler (worker)
python -m OpenOrchestrator u <conn_string>   # Apply DB migrations
```

## Usage for RPA developers

Import the connection module in your RPA code to access the Orchestrator:

- log status (trace/info/error)
- fetch credentials and constants
- create, read, update queue elements

Run your script with the arguments the Scheduler passes:

```bash
python run.py "<process name>" "<connection string>" "<secret key>" "<arguments>"
```

```python
# run.py
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

oc = OrchestratorConnection.create_connection_from_args()
oc.log_trace("OpenOrchestrator connected.")
```

## Installation

Requires Python 3.11 or later.

```bash
pip install OpenOrchestrator
```

### Creating or upgrading a database

```bash
python -m venv .venv
.venv\Scripts\activate
pip install OpenOrchestrator[alembic]

python -m OpenOrchestrator upgrade "<connection string>"
```

This applies all migrations up to the latest revision. Acceptable connection strings:

- `mssql+pyodbc://<host>/<db>?driver=ODBC+Driver+17+for+SQL+Server`
- `sqlite+pysqlite:///<path>.db`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, code standards, testing, and the migration workflow.

## License

[MIT](LICENSE)
