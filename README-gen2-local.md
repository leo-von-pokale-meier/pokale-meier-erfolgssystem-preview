# Pokale Meier Erfolgssoftware · Gen 2 (lokaler Testbetrieb)

Die Gen-2-Webanwendung ist eine **lokale Referenzimplementierung**: SQLite,
Rollen, Audit-Log, Passwort-Hashing sowie signierte Login-Sitzungen. Sie darf
nicht direkt ins Internet gestellt werden.

## Lokalen Testzugang anlegen

In Git Bash im Projektordner:

```bash
python bootstrap_gen2_admin.py --database erfolgssoftware.sqlite3 --name 'Dein Name' --email 'deine@email.de'
```

Das Passwort wird verdeckt abgefragt und nicht als Befehlsparameter gespeichert.

## Lokalen Server starten

Der Sitzungsschlüssel muss zufällig sein und darf nie committed oder geteilt werden:

```bash
export PM_ERFOLGS_PORTAL_SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python gen2_app.py
```

Danach nur auf diesem PC öffnen: <http://127.0.0.1:8765>.

## Sicherheitsgrenze

Für einen produktiven Betrieb fehlen bewusst noch: HTTPS-Reverse-Proxy,
Secret-Management, Passwort-Reset/MFA, verschlüsselte und getestete Backups,
Monitoring sowie eine DSGVO-/Berechtigungsprüfung. Die öffentliche GitHub-Pages-
Vorschau bleibt davon strikt getrennt und erhält keine echten Daten.
