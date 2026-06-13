"""Send reminders for appointments happening soon.

Intended to be run periodically by cron, e.g. every 15 minutes:

    */15 * * * * cd /path/to/backend && .venv/bin/python -m app.jobs.send_reminders

This is the recommended approach for multi-instance deployments, since it
runs in a single place and avoids duplicate sends.
"""

from app.core.reminders import run_due_reminders


def main() -> None:
    count = run_due_reminders()
    print(f"Reminders sent: {count}")


if __name__ == "__main__":
    main()
