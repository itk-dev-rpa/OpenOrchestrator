"""This module is used to run Orchestrator or Scheduler from the command line.
Usage: python -m OpenOrchestrator [-o|-s]"""

import argparse

from OpenOrchestrator.scheduler.application import Application as s_app
from OpenOrchestrator.orchestrator.application import Application as o_app

parser = argparse.ArgumentParser(
    prog="OpenOrchestrator",
    description="OpenOrchestrator is used to orchestrate, monitor and run Python based automation scripts in Windows."
)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-o", "--orchestrator", action="store_true", help="Start the Orchestrator application.")
group.add_argument("-s", "--scheduler", action="store_true", help="Start the Scheduler application.")

parser.add_argument("-p", "--port", type=int, help="Set the desired port for Orchestrator. Only works with -o.")
parser.add_argument("-d", "--dont_show", action="store_false", help="Set if you don't want Orchestrator to open in the browser automatically. Only works with -o.")

args = parser.parse_args()
print(args)

if args.orchestrator:
    o_app(port=args.port, show=args.dont_show)
elif args.scheduler:
    s_app()
