import argparse
import subprocess
import sys


def get_config_file(env_arg: str) -> str:  # pragma: no cover
    if env_arg == 'prod':
        return 'production.ini'
    return 'development.ini'


def run_command(command: list[str]):  # pragma: no cover
    """
    Executes a command using subprocess and handles potential errors.

    Args:
        command: The command to execute as a list of strings.
    """
    print(f"Executing: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, text=True)
        print("✅ Command finished successfully.")
    except subprocess.CalledProcessError as e:
        print(
            f"❌ Command failed with exit code {e.returncode}.",
            file=sys.stderr
        )
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(
            "❌ Error: 'alembic' command not found.",
            "Please ensure Alembic is installed and in your system's PATH.",
            file=sys.stderr
        )
        sys.exit(1)


def main():  # pragma: no cover
    """
    A command-line wrapper for Alembic to simplify database migrations.
    """
    parser = argparse.ArgumentParser(
        description="A simplified wrapper for Alembic database migrations.",
        epilog="Example: python migrate.py up head -e prod"
    )

    # Add an environment flag, defaulting to 'dev'
    parser.add_argument(
        '-e', '--environment',
        choices=['dev', 'prod'],
        default='dev',
        help="The target environment (dev or prod). Determines the .ini file used."
    )

    # Use subparsers for commands like 'create', 'upgrade', etc.
    subparsers = parser.add_subparsers(
        dest='command',
        required=True,
        help="The migration command to run."
    )

    # --- Command: create ---
    # Creates a new migration file.
    parser_create = subparsers.add_parser(
        'create',
        help='Create a new migration file.'
    )
    parser_create.add_argument(
        'message',
        type=str,
        help='A descriptive message for the migration.'
    )
    parser_create.add_argument(
        '--no-autogenerate',
        action='store_true',
        help="Create an empty migration file instead of auto-generating from model changes."
    )

    # --- Command: up ---
    # Replaces 'upgrade' and the old 'up' alias for a single, clear command.
    parser_up = subparsers.add_parser(
        'up',
        help='Upgrade the database to a later version.'
    )
    parser_up.add_argument(
        'revision',
        type=str,
        nargs='?',
        default='+1',
        help="The target revision. Examples: 'head' (latest), '+1' (one step up), '<revision_id>'. Defaults to '+1'."
    )

    # --- Command: down ---
    # Replaces 'downgrade' and the old 'down' alias.
    parser_down = subparsers.add_parser(
        'down',
        help='Downgrade the database to an earlier version.'
    )
    parser_down.add_argument(
        'revision',
        type=str,
        nargs='?',
        default='-1',
        help="The target revision. Examples: 'base' (first migration), '-1' (one step down), '<revision_id>'. Defaults to '-1'."
    )

    # --- Simple, no-argument commands ---
    subparsers.add_parser('history', help="View the full migration history.")
    subparsers.add_parser(
        'current', help="Show the current database revision.")

    args = parser.parse_args()

    # Determine the config file and build the base command
    config_file = get_config_file(args.environment)
    base_alembic_command = ["alembic", "-c", config_file]

    # Map the simplified commands to the full Alembic commands
    final_command = []
    if args.command == 'create':
        alembic_args = ["revision", "-m", args.message]
        if not args.no_autogenerate:
            alembic_args.append("--autogenerate")
        final_command = base_alembic_command + alembic_args

    elif args.command == 'up':
        final_command = base_alembic_command + ["upgrade", args.revision]

    elif args.command == 'down':
        final_command = base_alembic_command + ["downgrade", args.revision]

    elif args.command in ['history', 'current']:
        final_command = base_alembic_command + [args.command]

    # Execute the final command
    if final_command:
        run_command(final_command)
    else:
        # This case should not be hit if subparsers are configured correctly
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
