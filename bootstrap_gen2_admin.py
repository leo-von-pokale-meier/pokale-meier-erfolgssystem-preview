"""Create the first administrator for a local Gen-2 database.

Run only on a trusted machine. The password is requested interactively and is
never written to this file or command history.
"""
from __future__ import annotations

import argparse
import getpass

from gen2_foundation import FoundationStore


def main() -> None:
    parser = argparse.ArgumentParser(description='Ersten Admin für die Pokale-Meier-Erfolgssoftware anlegen.')
    parser.add_argument('--database', default='erfolgssoftware.sqlite3', help='Pfad zur SQLite-Datenbank')
    parser.add_argument('--name', required=True, help='Name des Administrators')
    parser.add_argument('--email', required=True, help='E-Mail-Adresse des Administrators')
    args = parser.parse_args()

    password = getpass.getpass('Neues Passwort (mindestens 12 Zeichen): ')
    confirmation = getpass.getpass('Passwort wiederholen: ')
    if password != confirmation:
        raise SystemExit('Passwörter stimmen nicht überein.')

    user = FoundationStore(args.database).bootstrap_admin(args.name, args.email, password)
    print(f"Admin angelegt: {user['email']} (ID {user['id']})")


if __name__ == '__main__':
    main()
