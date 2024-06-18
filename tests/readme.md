# Tests

Before running the tests you need to define the connection string to your test database
as a environment variable:

```bash
SET CONN_STRING= *connection string here*
```

Examples of connection strings:
- mssql+pyodbc://localhost\SQLEXPRESS/OO_Unittest?driver=ODBC+Driver+17+for+SQL+Server
- sqlite+pysqlite:///test_db.db

To run tests execute the following command from the main directory:

```bash
python -m unittest discover tests
```