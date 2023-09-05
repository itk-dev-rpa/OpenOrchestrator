import sys
from OpenOrchestrator.Scheduler.Application import Application as s_app
from OpenOrchestrator.Orchestrator.Application import Application as o_app

if len(sys.argv) != 2:
    print("Usage: -o to start Orchestrator. -s to start Scheduler")
elif sys.argv[1] == '-s':
    s_app()
elif sys.argv[1] == '-o':
    o_app()
else:
    print("Usage: -o to start Orchestrator. -s to start Scheduler")