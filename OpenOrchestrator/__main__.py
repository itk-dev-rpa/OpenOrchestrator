"""This module is used to run Orchestrator or Scheduler from the command line.
Usage: python -m OpenOrchestrator [-o|-s]"""

import sys
from OpenOrchestrator.scheduler.application import Application as s_app
from OpenOrchestrator.orchestrator.application import Application as o_app


def _print_usage():
    print("Usage: -o to start Orchestrator. -s to start Scheduler")


if len(sys.argv) != 2:
    _print_usage()
elif sys.argv[1] == '-s':
    s_app()
elif sys.argv[1] == '-o':
    o_app()
else:
    _print_usage()
