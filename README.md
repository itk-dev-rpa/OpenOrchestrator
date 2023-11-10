# OpenOrchestrator

Read the documentation [here](https://itk-dev-rpa.github.io/OpenOrchestrator-docs).

Package is located at https://pypi.org/project/OpenOrchestrator/

## Usage for Orchestrator admins
This module is used to run Orchestrator or Scheduler from the command line.

`python -m OpenOrchestrator -o`  for orchestrator.

`python -m OpenOrchestrator -s`  for scheduler.

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
# connect to OpenOprchestrator and log something
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

oc = OrchestratorConnection.create_connection_from_args()
oc.log_trace("open orchestrator connected.")
``` 


## Setup
Requires Python 3.10 or later.

Install using `pip install OpenOrchestrator`
