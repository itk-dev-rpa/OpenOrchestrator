"""This module is used to run Orchestrator or Scheduler from the command line."""

import argparse
import subprocess

from OpenOrchestrator.scheduler.application import Application as s_app
from OpenOrchestrator.orchestrator.application import Application as o_app


def main():
    """The main entry point of the CLI."""
    parser = argparse.ArgumentParser(
        prog="OpenOrchestrator",
        description="OpenOrchestrator is used to orchestrate, monitor and run Python-based automation scripts in Windows."
    )

    subparsers = parser.add_subparsers(title="Subcommands", required=True)

    o_parser = subparsers.add_parser("orchestrator", aliases=["o"], help="Start the Orchestrator application.")
    o_parser.add_argument("-p", "--port", type=int, help="Set the desired port for Orchestrator.")
    o_parser.add_argument("-d", "--dont_show", action="store_false", help="Set if you don't want Orchestrator to open in the browser automatically.")
    o_parser.set_defaults(func=orchestrator_command)

    s_parser = subparsers.add_parser("scheduler", aliases=["s"], help="Start the Scheduler application.")
    s_parser.set_defaults(func=scheduler_command)

    u_parser = subparsers.add_parser("upgrade", aliases=["u"], help="Upgrade the database to the newest revision or create a new database from scratch.")
    u_parser.add_argument("connection_string", type=str, help="The connection string to the database")
    u_parser.set_defaults(func=upgrade_command)

    args = parser.parse_args()
    args.func(args)


def orchestrator_command(args: argparse.Namespace):
    """Start the Orchestrator app.

    Args:
        args: The arguments Namespace object.
    """
    o_app(port=args.port, show=args.dont_show)


def scheduler_command(args: argparse.Namespace):  # pylint: disable=unused-argument
    """Start the Scheduler app."""
    s_app()


def upgrade_command(args: argparse.Namespace):
    """Upgrade the database to the newest revision using alembic.

    Args:
        args: The arguments Namespace object.
    """
    confirmation = input("Are you sure you want to upgrade the database to the newest revision? This cannot be undone. (y/n)").strip()
    if confirmation == "y":
        # Check if database is already stamped
        result = subprocess.run(["alembic", "-x", args.connection_string, "current"], check=True, capture_output=True)
        if result.stdout == b'':
            response = input("It seems like you are either creating a new database or trying to upgrade a legacy database. Please choose an option: (new/legacy/cancel)").strip()
            if response == "legacy":
                subprocess.run(["alembic", "-x", args.connection_string, "stamp", "b67b7649b282"], check=True)
            elif response != "new":
                print("Upgrade canceled")
                return

        subprocess.run(["alembic", "-x", args.connection_string, "upgrade", "head"], check=True)
        print("Database upgraded to the newest revision!")
    else:
        print("Upgrade canceled")


if __name__ == '__main__':
    main()
