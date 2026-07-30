"""Local Gen-2 foundation for the Pokale Meier Erfolgsportal.

This module intentionally has no cloud credentials. It provides a persistent SQLite
model, password hashing, role checks, organisation scoping and an immutable audit log.
A production deployment still needs HTTPS, managed backups and an external secret store.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROLES = {
    'admin': {'*'},
    'designer': {'organisations.read', 'appointments.read', 'customers.read'},
    'berater': {'organisations.read', 'organisations.write', 'appointments.read', 'appointments.write', 'customers.read', 'customers.write', 'gamification.write'},
    'kundenservice': {'organisations.read', 'appointments.read', 'appointments.write', 'customers.read'},
}

# Confirmed Gen-2 starting rules. Every score-relevant event stays auditable,
# and counts only after verification. Delivered awards deliberately carry more
# value than a generic task point.
ACHIEVEMENT_RULES = {
    'award_delivered': {'points': 12, 'badge': None},
    'award_photo_uploaded': {'points': 1, 'badge': None},
    'online_gallery_uploaded': {'points': 5, 'badge': None},
    'referral_program_created': {'points': 10, 'badge': None},
    'physical_incentive_system': {'points': 10, 'badge': None},
    'bronze_completed': {'points': 10, 'badge': 'Bronze abgeschlossen'},
    'silver_completed': {'points': 20, 'badge': 'Silber abgeschlossen'},
    'appointment_completed': {'points': 1, 'badge': None},
}


class PermissionDenied(Exception):
    pass


class ValidationError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _password_record(password: str) -> tuple[str, str]:
    if len(password) < 12:
        raise ValidationError('Passwort muss mindestens 12 Zeichen haben.')
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 310_000)
    return base64.b64encode(salt).decode('ascii'), base64.b64encode(digest).decode('ascii')


def _password_matches(password: str, salt: str, digest: str) -> bool:
    candidate = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), base64.b64decode(salt), 310_000)
    return hmac.compare_digest(base64.b64encode(candidate).decode('ascii'), digest)


class FoundationStore:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        self._initialise()

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialise(self) -> None:
        with self._connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS organisations (
                    id INTEGER PRIMARY KEY, name TEXT NOT NULL, website_url TEXT NOT NULL DEFAULT '',
                    lifecycle_stage TEXT NOT NULL DEFAULT 'bronze', active INTEGER NOT NULL DEFAULT 1,
                    public_profile_enabled INTEGER NOT NULL DEFAULT 0, public_description TEXT NOT NULL DEFAULT '',
                    partner_url TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, organisation_id INTEGER REFERENCES organisations(id),
                    name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, role TEXT NOT NULL,
                    password_salt TEXT NOT NULL, password_digest TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY, organisation_id INTEGER NOT NULL REFERENCES organisations(id),
                    title TEXT NOT NULL, scheduled_at TEXT NOT NULL, next_steps TEXT NOT NULL DEFAULT '',
                    next_steps_customer_visible INTEGER NOT NULL DEFAULT 1,
                    summary_status TEXT NOT NULL DEFAULT 'placeholder',
                    status TEXT NOT NULL DEFAULT 'planned', completed_at TEXT, verified_at TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS achievement_events (
                    id INTEGER PRIMARY KEY,
                    organisation_id INTEGER NOT NULL REFERENCES organisations(id),
                    appointment_id INTEGER REFERENCES appointments(id),
                    event_type TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    verified_at TEXT, public_approved INTEGER NOT NULL DEFAULT 0, public_title TEXT NOT NULL DEFAULT '',
                    created_by INTEGER NOT NULL REFERENCES users(id),
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_achievement_leaderboard
                    ON achievement_events(organisation_id, verified_at);
            ''')
            # Additive migrations keep existing local test data usable without
            # weakening the audit trail or rebuilding the database.
            appointment_columns = {row['name'] for row in conn.execute('PRAGMA table_info(appointments)')}
            for definition in (
                "status TEXT NOT NULL DEFAULT 'planned'",
                'completed_at TEXT',
                'verified_at TEXT',
            ):
                name = definition.split()[0]
                if name not in appointment_columns:
                    conn.execute(f'ALTER TABLE appointments ADD COLUMN {definition}')
            organisation_columns = {row['name'] for row in conn.execute('PRAGMA table_info(organisations)')}
            for definition in ('public_profile_enabled INTEGER NOT NULL DEFAULT 0', "public_description TEXT NOT NULL DEFAULT ''", "partner_url TEXT NOT NULL DEFAULT ''"):
                name = definition.split()[0]
                if name not in organisation_columns:
                    conn.execute(f'ALTER TABLE organisations ADD COLUMN {definition}')
            achievement_columns = {row['name'] for row in conn.execute('PRAGMA table_info(achievement_events)')}
            if 'appointment_id' not in achievement_columns:
                conn.execute('ALTER TABLE achievement_events ADD COLUMN appointment_id INTEGER REFERENCES appointments(id)')
            for definition in ('public_approved INTEGER NOT NULL DEFAULT 0', "public_title TEXT NOT NULL DEFAULT ''"):
                name = definition.split()[0]
                if name not in achievement_columns:
                    conn.execute(f'ALTER TABLE achievement_events ADD COLUMN {definition}')
            conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_achievement_one_verified_appointment ON achievement_events(appointment_id) WHERE appointment_id IS NOT NULL')
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY, organisation_id INTEGER REFERENCES organisations(id),
                    actor_user_id INTEGER REFERENCES users(id), action TEXT NOT NULL,
                    payload TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL
                );
            ''')

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row else None

    def _require(self, actor_id: int, permission: str) -> dict[str, Any]:
        with self._connection() as conn:
            user = self._row(conn.execute('SELECT * FROM users WHERE id = ?', (actor_id,)).fetchone())
        if not user or not user['active'] or user['role'] not in ROLES:
            raise PermissionDenied('Aktiver Zugang erforderlich.')
        permissions = ROLES[user['role']]
        if '*' not in permissions and permission not in permissions:
            raise PermissionDenied('Berechtigung fehlt.')
        return user

    def _audit(self, conn: sqlite3.Connection, organisation_id: int | None, actor_id: int | None, action: str, payload: dict[str, Any]) -> None:
        conn.execute('INSERT INTO audit_log (organisation_id, actor_user_id, action, payload, created_at) VALUES (?, ?, ?, ?, ?)',
                     (organisation_id, actor_id, action, json.dumps(payload, ensure_ascii=False), _now()))

    def bootstrap_admin(self, name: str, email: str, password: str) -> dict[str, Any]:
        if not _text(name) or not _text(email):
            raise ValidationError('Name und E-Mail sind erforderlich.')
        salt, digest = _password_record(password)
        with self._connection() as conn:
            exists = conn.execute("SELECT 1 FROM users WHERE role = 'admin' AND active = 1").fetchone()
            if exists:
                raise ValidationError('Ein aktiver Admin ist bereits eingerichtet.')
            cursor = conn.execute('INSERT INTO users (name, email, role, password_salt, password_digest, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                                  (_text(name), _text(email).lower(), 'admin', salt, digest, _now()))
            user_id = cursor.lastrowid
            self._audit(conn, None, user_id, 'admin.bootstrapped', {'email': _text(email).lower()})
        return self.user(user_id)

    def user(self, user_id: int) -> dict[str, Any]:
        with self._connection() as conn:
            row = conn.execute('SELECT id, organisation_id, name, email, role, active, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
        if not row:
            raise ValidationError('Zugang wurde nicht gefunden.')
        return dict(row)

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            row = conn.execute('SELECT * FROM users WHERE email = ? AND active = 1', (_text(email).lower(),)).fetchone()
        if not row or not _password_matches(password, row['password_salt'], row['password_digest']):
            return None
        return self.user(row['id'])

    def create_internal_user(self, actor_id: int, name: str, email: str, role: str, password: str) -> dict[str, Any]:
        self._require(actor_id, 'users.manage')
        if role not in ROLES or role == 'admin':
            raise ValidationError('Nur die bestätigten internen Rollen sind erlaubt; weitere Admins werden separat angelegt.')
        if not _text(name) or not _text(email):
            raise ValidationError('Name und E-Mail sind erforderlich.')
        salt, digest = _password_record(password)
        with self._connection() as conn:
            cursor = conn.execute('INSERT INTO users (name, email, role, password_salt, password_digest, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                                  (_text(name), _text(email).lower(), role, salt, digest, _now()))
            user_id = cursor.lastrowid
            self._audit(conn, None, actor_id, 'internal_user.created', {'user_id': user_id, 'role': role})
        return self.user(user_id)

    def create_organisation(self, actor_id: int, name: str, website_url: str = '') -> dict[str, Any]:
        self._require(actor_id, 'organisations.write')
        if not _text(name):
            raise ValidationError('Firmenname ist erforderlich.')
        now = _now()
        with self._connection() as conn:
            cursor = conn.execute('INSERT INTO organisations (name, website_url, created_at, updated_at) VALUES (?, ?, ?, ?)',
                                  (_text(name), _text(website_url), now, now))
            organisation_id = cursor.lastrowid
            self._audit(conn, organisation_id, actor_id, 'organisation.created', {'name': _text(name)})
        return self.organisation(organisation_id)

    def organisation(self, organisation_id: int) -> dict[str, Any]:
        with self._connection() as conn:
            row = conn.execute('SELECT * FROM organisations WHERE id = ?', (organisation_id,)).fetchone()
        if not row:
            raise ValidationError('Kundenorganisation wurde nicht gefunden.')
        return dict(row)

    def update_public_profile(self, actor_id: int, organisation_id: int, enabled: bool,
                              description: str = '', partner_url: str = '') -> dict[str, Any]:
        """Expose a partner profile only after explicit organisation-level approval."""
        self._require(actor_id, 'organisations.write')
        self.organisation(organisation_id)
        with self._connection() as conn:
            conn.execute(
                'UPDATE organisations SET public_profile_enabled = ?, public_description = ?, partner_url = ?, updated_at = ? WHERE id = ?',
                (int(bool(enabled)), _text(description), _text(partner_url), _now(), organisation_id),
            )
            self._audit(conn, organisation_id, actor_id, 'organisation.public_profile_updated', {
                'enabled': bool(enabled), 'has_description': bool(_text(description)), 'has_partner_url': bool(_text(partner_url)),
            })
        return self.organisation(organisation_id)

    def create_customer(self, actor_id: int, organisation_id: int, name: str, email: str, password: str) -> dict[str, Any]:
        self._require(actor_id, 'customers.write')
        self.organisation(organisation_id)
        if not _text(name) or not _text(email):
            raise ValidationError('Name und E-Mail sind erforderlich.')
        salt, digest = _password_record(password)
        with self._connection() as conn:
            cursor = conn.execute('INSERT INTO users (organisation_id, name, email, role, password_salt, password_digest, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                  (organisation_id, _text(name), _text(email).lower(), 'customer', salt, digest, _now()))
            user_id = cursor.lastrowid
            self._audit(conn, organisation_id, actor_id, 'customer.created', {'user_id': user_id})
        return self.user(user_id)

    def archive_customer(self, actor_id: int, customer_id: int) -> None:
        self._require(actor_id, 'customers.archive')
        with self._connection() as conn:
            customer = conn.execute("SELECT organisation_id FROM users WHERE id = ? AND role = 'customer'", (customer_id,)).fetchone()
            if not customer:
                raise ValidationError('Kundenzugang wurde nicht gefunden.')
            conn.execute('UPDATE users SET active = 0 WHERE id = ?', (customer_id,))
            self._audit(conn, customer['organisation_id'], actor_id, 'customer.archived', {'user_id': customer_id})

    def create_appointment(self, actor_id: int, organisation_id: int, title: str, scheduled_at: str, next_steps: str = '') -> dict[str, Any]:
        self._require(actor_id, 'appointments.write')
        self.organisation(organisation_id)
        if not _text(title) or not _text(scheduled_at):
            raise ValidationError('Titel und Terminzeit sind erforderlich.')
        now = _now()
        with self._connection() as conn:
            cursor = conn.execute('INSERT INTO appointments (organisation_id, title, scheduled_at, next_steps, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                                  (organisation_id, _text(title), _text(scheduled_at), _text(next_steps), now, now))
            appointment_id = cursor.lastrowid
            self._audit(conn, organisation_id, actor_id, 'appointment.created', {'appointment_id': appointment_id, 'summary_status': 'placeholder'})
            row = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
        return dict(row)

    def visible_appointments(self, user_id: int) -> list[dict[str, Any]]:
        with self._connection() as conn:
            user = conn.execute('SELECT organisation_id, role, active FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user or not user['active']:
                raise PermissionDenied('Aktiver Zugang erforderlich.')
            if user['role'] == 'customer':
                rows = conn.execute('SELECT * FROM appointments WHERE organisation_id = ? ORDER BY scheduled_at', (user['organisation_id'],)).fetchall()
            else:
                self._require(user_id, 'appointments.read')
                rows = conn.execute('SELECT * FROM appointments ORDER BY scheduled_at').fetchall()
        return [dict(row) for row in rows]

    def complete_appointment(self, actor_id: int, appointment_id: int) -> dict[str, Any]:
        """Close a meeting operationally; this alone never creates points."""
        self._require(actor_id, 'appointments.write')
        now = _now()
        with self._connection() as conn:
            appointment = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
            if not appointment:
                raise ValidationError('Termin wurde nicht gefunden.')
            if appointment['status'] != 'planned':
                raise ValidationError('Termin ist bereits abgeschlossen oder geprüft.')
            conn.execute(
                "UPDATE appointments SET status = 'completed', completed_at = ?, updated_at = ? WHERE id = ?",
                (now, now, appointment_id),
            )
            self._audit(conn, appointment['organisation_id'], actor_id, 'appointment.completed', {'appointment_id': appointment_id})
            row = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
        return dict(row)

    def verify_appointment_completion(self, actor_id: int, appointment_id: int) -> dict[str, Any]:
        """Create the one audited point event after an internal review."""
        self._require(actor_id, 'gamification.write')
        now = _now()
        with self._connection() as conn:
            appointment = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
            if not appointment:
                raise ValidationError('Termin wurde nicht gefunden.')
            if appointment['status'] != 'completed':
                raise ValidationError('Nur abgeschlossene Termine können geprüft werden.')
            if conn.execute('SELECT 1 FROM achievement_events WHERE appointment_id = ?', (appointment_id,)).fetchone():
                raise ValidationError('Dieser Termin wurde bereits als Erfolg bestätigt.')
            rule = ACHIEVEMENT_RULES['appointment_completed']
            cursor = conn.execute(
                'INSERT INTO achievement_events (organisation_id, appointment_id, event_type, points, verified_at, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (appointment['organisation_id'], appointment_id, 'appointment_completed', rule['points'], now, actor_id, now),
            )
            conn.execute("UPDATE appointments SET status = 'verified', verified_at = ?, updated_at = ? WHERE id = ?", (now, now, appointment_id))
            self._audit(conn, appointment['organisation_id'], actor_id, 'appointment.verified', {
                'appointment_id': appointment_id, 'event_id': cursor.lastrowid, 'points': rule['points'],
            })
            row = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
        return dict(row)

    def organisation_journey(self, organisation_id: int) -> dict[str, Any]:
        """Return a customer-safe process snapshot without exposing another tenant."""
        score = self.organisation_score(organisation_id)
        with self._connection() as conn:
            next_appointment = conn.execute(
                "SELECT * FROM appointments WHERE organisation_id = ? AND status = 'planned' ORDER BY scheduled_at, id LIMIT 1",
                (organisation_id,),
            ).fetchone()
        if 'Bronze abgeschlossen' not in score['badges']:
            target_name, target_points = 'Bronze abschließen', 10
        elif 'Silber abgeschlossen' not in score['badges']:
            target_name, target_points = 'Silber abschließen', 20
        else:
            target_name, target_points = 'Nächsten sichtbaren Erfolg bestätigen', score['points']
        return {
            'organisation_id': organisation_id,
            'points': score['points'],
            'badges': score['badges'],
            'next_appointment': dict(next_appointment) if next_appointment else None,
            'next_award': target_name,
            'points_to_next_award': max(0, target_points - score['points']),
        }

    def audit_entries(self, organisation_id: int) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute('SELECT * FROM audit_log WHERE organisation_id = ? ORDER BY id', (organisation_id,)).fetchall()
        return [dict(row) for row in rows]

    def record_achievement(self, actor_id: int, organisation_id: int, event_type: str, verified: bool = False) -> dict[str, Any]:
        self._require(actor_id, 'gamification.write')
        if event_type not in ACHIEVEMENT_RULES:
            raise ValidationError('Unbekannte Erfolgsart.')
        self.organisation(organisation_id)
        rule = ACHIEVEMENT_RULES[event_type]
        now = _now()
        with self._connection() as conn:
            cursor = conn.execute(
                'INSERT INTO achievement_events (organisation_id, event_type, points, verified_at, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (organisation_id, event_type, rule['points'], now if verified else None, actor_id, now),
            )
            event_id = cursor.lastrowid
            self._audit(conn, organisation_id, actor_id, 'achievement.recorded', {
                'event_id': event_id, 'event_type': event_type, 'points': rule['points'], 'verified': verified,
            })
            row = conn.execute('SELECT * FROM achievement_events WHERE id = ?', (event_id,)).fetchone()
        return dict(row)

    def approve_achievement_for_public(self, actor_id: int, achievement_id: int, title: str) -> dict[str, Any]:
        """Approve one verified event for the public feed; verification never implies consent."""
        self._require(actor_id, 'gamification.write')
        if not _text(title):
            raise ValidationError('Ein öffentlicher Erfolgstitel ist erforderlich.')
        with self._connection() as conn:
            event = conn.execute('SELECT * FROM achievement_events WHERE id = ?', (achievement_id,)).fetchone()
            if not event:
                raise ValidationError('Erfolg wurde nicht gefunden.')
            if not event['verified_at']:
                raise ValidationError('Nur bestätigte Erfolge dürfen veröffentlicht werden.')
            conn.execute('UPDATE achievement_events SET public_approved = 1, public_title = ? WHERE id = ?', (_text(title), achievement_id))
            self._audit(conn, event['organisation_id'], actor_id, 'achievement.public_approved', {'event_id': achievement_id, 'title': _text(title)})
            row = conn.execute('SELECT * FROM achievement_events WHERE id = ?', (achievement_id,)).fetchone()
        return dict(row)

    def organisation_score(self, organisation_id: int) -> dict[str, Any]:
        self.organisation(organisation_id)
        with self._connection() as conn:
            rows = conn.execute('SELECT event_type, points FROM achievement_events WHERE organisation_id = ? AND verified_at IS NOT NULL', (organisation_id,)).fetchall()
        events = [row['event_type'] for row in rows]
        badges = [rule['badge'] for event, rule in ACHIEVEMENT_RULES.items() if rule['badge'] and event in events]
        return {'organisation_id': organisation_id, 'points': sum(row['points'] for row in rows), 'badges': badges}

    def leaderboard(self) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute('''
                SELECT o.id, o.name, o.website_url, o.lifecycle_stage, o.public_profile_enabled,
                       o.public_description, o.partner_url, COALESCE(SUM(e.points), 0) AS points,
                       COUNT(e.id) AS success_count
                FROM organisations o
                LEFT JOIN achievement_events e ON e.organisation_id = o.id AND e.verified_at IS NOT NULL
                WHERE o.active = 1
                GROUP BY o.id
                ORDER BY points DESC, o.name COLLATE NOCASE
            ''').fetchall()
        return [dict(row) for row in rows]

    def public_leaderboard(self) -> list[dict[str, Any]]:
        """Return only profiles whose organisation has approved public visibility."""
        return [row for row in self.leaderboard() if row['public_profile_enabled']]

    def recent_public_successes(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return individually approved, verified successes for the public activity stream."""
        bounded_limit = max(1, min(int(limit), 100))
        with self._connection() as conn:
            rows = conn.execute('''
                SELECT e.id, e.event_type, e.points, e.public_title AS title, e.verified_at,
                       o.id AS organisation_id, o.name AS organisation_name, o.partner_url, o.website_url
                FROM achievement_events e JOIN organisations o ON o.id = e.organisation_id
                WHERE e.verified_at IS NOT NULL AND e.public_approved = 1
                  AND o.active = 1 AND o.public_profile_enabled = 1
                ORDER BY e.verified_at DESC, e.id DESC LIMIT ?
            ''', (bounded_limit,)).fetchall()
        return [dict(row) for row in rows]
