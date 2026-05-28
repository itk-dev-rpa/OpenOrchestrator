# Contributing to OpenOrchestrator

Thanks for considering a contribution. This document covers local setup, the standards the code is held to, and the PR/release flow.

For a high-level picture of the system, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) first.

## Local setup

```bash
git clone https://github.com/itk-dev-rpa/OpenOrchestrator.git
cd OpenOrchestrator
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev,alembic]
```

Editable install (`-e`) means your code changes are picked up without reinstall.

## Branching and PRs

- `main` holds the latest released code.
- `develop` is the integration branch — open feature PRs against it.
- Use feature branches named `feature/<short-description>`, fix branches `fix/<short-description>`.
- **Every PR must update [changelog.md](changelog.md)** under the `[Unreleased]` section. The [Changelog workflow](.github/workflows/Changelog.yml) enforces this.
- Releases are cut from `develop → main`, tagged, and published to PyPI by [python-publish.yml](.github/workflows/python-publish.yml).

## Code standards

Two linters run on every PR ([Linting.yml](.github/workflows/Linting.yml)):

- **pylint** — config in [.pylintrc](.pylintrc). Disables `C0301` (line length, handled by flake8), `I1101/E1101` (C-extension member access), `R0913/R0914` (too many args/locals).
- **flake8** — invoked with `--extend-ignore=E501,E251`.

Run locally before pushing:

```bash
pylint --rcfile=.pylintrc OpenOrchestrator --good-names=OpenOrchestrator
flake8 --extend-ignore=E501,E251 OpenOrchestrator
```

### Style conventions

- **Type hints** are required on all public functions and methods. Use modern syntax (`str | None`, not `Optional[str]`) — the project targets Python 3.11+.
- **Docstrings** use **Google style** with `Args:`, `Returns:`, `Raises:` sections. Every module, class, and public function gets one. See [database/db_util.py](OpenOrchestrator/database/db_util.py) for examples.
- **Imports**: stdlib → third-party → local (`OpenOrchestrator.*`), separated by blank lines.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for module-level constants.
- **Errors** raised by the database layer should use the typed exceptions from [database/exceptions.py](OpenOrchestrator/database/exceptions.py) (e.g. `TriggerNotFoundError`) rather than generic `ValueError`.
- **No comments restating what the code does.** Only comment when the *why* is non-obvious (constraints, workarounds, surprising behavior).

## Testing

The test suite uses `unittest` and discovers tests under `OpenOrchestrator/tests/`.

```bash
set CONN_STRING=sqlite+pysqlite:///test_db.db
python -m unittest discover
```

Acceptable connection strings:

- `sqlite+pysqlite:///test_db.db` — fastest; what CI uses.
- `mssql+pyodbc://localhost\SQLEXPRESS/OO_Unittest?driver=ODBC+Driver+17+for+SQL+Server` — closer to production.

UI tests under `tests/ui_tests/` use Selenium against a headless Chrome and start a NiceGUI server on a random port. They take significantly longer than the unit tests and require Chrome to be installed.

Coverage gaps (open follow-ups): the Scheduler tkinter UI, the four orchestrator popups, `crypto_util`, `datetime_util`, and `truncated_string` are not yet covered.

## Database migrations

Schema changes require an Alembic revision under [alembic_migrations/versions/](alembic_migrations/versions/):

1. Make sure your local DB is on the **previous** revision.
2. If you added new ORM classes, import them in [alembic_migrations/env.py](alembic_migrations/env.py).
3. Generate the revision:

   ```bash
   alembic -x "<connection_string>" revision --autogenerate -m "Short description"
   ```

4. Open the generated file under `alembic_migrations/versions/` and verify the up/down operations. Autogenerate catches the obvious cases but misses things like check constraints, server defaults, and renames — fix these by hand.
5. Update the expected revision hash in `db_util.check_database_revision`.
6. Test the migration end-to-end: `python -m OpenOrchestrator upgrade <conn_string>` against a fresh DB.

## Reporting bugs / requesting features

Use the [issue tracker](https://github.com/itk-dev-rpa/OpenOrchestrator/issues). Include the OpenOrchestrator version (`pip show OpenOrchestrator`), Python version, and a minimal reproduction.
