# OpenOrchestrator

Read the documentation [here](https://itk-dev-rpa.github.io/OpenOrchestrator-docs).

Package is located at [Pypi](https://pypi.org/project/OpenOrchestrator/).

## Usage for Orchestrator admins

OpenOrchestrator provides a commandline interface (cli) to start the different parts
of the application.

For a full explanation run `python -m OpenOrchestrator -h` in the command line.

The most common commands would be:

`python -m OpenOrchestrator o`  for orchestrator.

`python -m OpenOrchestrator s`  for scheduler.

## Usage for RPA developers

Import the connection module to your RPA code and get access to the orchestrator methods;

- logging status to OpenOrchestrator
- getting credentials and constants from OpenOrchestrator
- creating, getting and updating job elements in a queue

Run the code with arguments

```bash
python run.py "<process name>" "<connection string>" "<secret key>" "<arguments>"
```

```python
# run.py
# connect to OpenOrchestrator and log something
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

oc = OrchestratorConnection.create_connection_from_args()
oc.log_trace("open orchestrator connected.")
```

## Installation

Requires Python 3.10 or later.

Install using `pip install OpenOrchestrator`

### Creating or upgrading a database

If you need to create a new database or upgrade to a new revision follow these steps:

1. Download this repository either via Github or Git.
2. Open a command line in the project folder.
3. Run the following commands:

```bash
python -m venv .venv
.venv\scripts\activate
pip install .[alembic]

python -m OpenOrchestrator upgrade "<Your connection string here>"
```

This will automatically bring you to the newest revision of the database.

## Contributing

### Setup

To start developing for OpenOrchestrator pull the current develop branch using GIT.

In the new folder run the following commands in the command line:

```bash
python -m venv .venv
.venv\scripts\activate
pip install -e .
```

This will create a new virtual environment and install the project in 'editable' mode.
This means that any changes to the code is automatically included in the installation.

### Automated Tests

OpenOrchestrator contains automated tests.

Before running the tests you need to define the following environment variables:

```bash
SET CONN_STRING="<connection string to test db>"
```

Examples of connection strings:

- mssql+pyodbc://localhost\SQLEXPRESS/OO_Unittest?driver=ODBC+Driver+17+for+SQL+Server
- sqlite+pysqlite:///test_db.db

To run tests execute the following command from the main directory:

```bash
python -m unittest discover
```

### Manual Tests

Not all functionality is covered by automated tests. Especially the Scheduler app is not covered well.

Refer to the `manual_tests.txt` file for a list of things that should be tested.

### Creating new database revisions

If your update requires a change to the database schemas you need to create a new revision schema in the `alembic` folder.

This can mostly be done automatically by the following steps:

1. First make sure your database is on the __previous__ version of the database schema.

2. Make sure any new ORM classes are imported in `alembic/env.py`.

3. Then run the following command (replacing the connection string and message):

    ```bash
    alembic -x "connection_string" revision --autogenerate -m "Some useful message"
    ```

    This will create a new file in the `alembic/versions` folder with a random prefix and then your message as the name.

4. Open the file and make sure the contents make sense. Obvious changes are detected automatically
but some changes might not be.

5. Update the expected revision number in `db_util.py > check_database_revision`.
