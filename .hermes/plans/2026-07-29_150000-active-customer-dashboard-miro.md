# Erfolgsportal Gen 1 – internes Kunden-Dashboard mit Miro-Boards

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Das Erfolgsportal erhält ein internes Dashboard mit allen aktiven Kunden und ihrem jeweiligen Miro-Board, ohne die beiden getrennten Projekte Erfolgsportal und Impact Frame Designer zu vermischen.

**Architecture:** Das bisherige statische Gen-1-Portal bleibt eine eigenständige HTML-Anwendung. Zuerst entsteht eine versionierte, lokal nutzbare Dashboard-Generation mit einer kleinen, testbaren Kundendaten-Schicht. Die Miro-Anbindung wird als getrennte Adapter-Schicht ergänzt: Kein API-Token liegt in HTML, JavaScript, Git oder Browser-Speicher. In der ersten Live-Generation wird das Dashboard intern auf einem kontrollierten Rechner bereitgestellt; nach realer Nutzung wird es iterativ erweitert.

**Tech Stack:** Bestehend: HTML, CSS, Vanilla JavaScript, `localStorage`, Python `unittest`. Ergänzend: Git; für die produktive Miro-Synchronisation ein kleiner serverseitiger Adapter mit Miro-OAuth/API-Zugang und sicher abgelegten Zugangsdaten.

---

## Ausgangslage

- Projekt: `C:/Users/mhaen/Documents/Pokale-Meier-Erfolgsportal`
- Es gibt derzeit **kein Git-Repository** und damit keinen verlässlichen Rollback-Punkt.
- Das Portal enthält bereits eine interne Kundenansicht und lokale Datensätze, aber noch kein Dashboard für aktive Kunden mit Miro-Verknüpfungen.
- Aktive Kunden haben je ein eigenes Miro-Board. Die Boards sind die führende Arbeitsquelle für den jeweiligen Kunden.
- Die Datei `impact-frame-designer.html` liegt bewusst in einem anderen Projekt und wird weder importiert noch mitversioniert.

## Zielbild Generation 1.1

Die Startansicht zeigt ausschließlich aktive Vorgänge/Kunden in einer handlungsorientierten Übersicht. Jede Kundenkarte enthält:

1. Kundenname und interner Verantwortlicher
2. aktuelle Erfolgsstufe (z. B. Bronze, Silber, abgeschlossen/pausiert)
3. nächster konkreter Schritt inkl. Termin/Frist, sofern vorhanden
4. Fortschritt und zuletzt aktualisierter Stand
5. einen sichtbaren Link/Button **„Miro-Board öffnen“**
6. eine Ampel für Handlungsbedarf (normal, heute fällig, überfällig)
7. eine sichtbare Quelle/Sync-Information: manuell gepflegt oder letzter erfolgreicher Miro-Abruf

Nicht Teil von Gen 1.1: Schreiben in Miro, automatische Kundenanlage, Mitarbeiterrechte, externe Kundenzugänge oder eine Vermischung mit dem Impact-Frame-Designer.

## Versionierungs- und Rollback-Regeln

- Einmalig zunächst eine lokale Git-Historie anlegen; davor keine weiteren Funktionsänderungen.
- Der aktuelle getestete Portalstand wird als erster Commit und Tag `v1.0.0-ci-baseline` konserviert.
- Neue Arbeit erfolgt ausschließlich auf beschreibenden Feature-Branches, etwa `feat/active-customer-dashboard`.
- Jede abgeschlossene, geprüfte Teilfunktion bekommt einen kleinen Commit und einen Changelog-Eintrag.
- Vor jeder internen Live-Schaltung wird ein Release-Tag erstellt, z. B. `v1.1.0-rc.1`, danach `v1.1.0`.
- Rollback bedeutet: vorherigen Tag lokal in einer separaten Vorschau bereitstellen und erst nach Sichtprüfung gezielt zurückschalten. Kein `git reset --hard` auf unbekannte Arbeitsstände.
- API-Tokens, Exportdateien mit Kundendaten, `.env`-Dateien und lokale Miro-Caches werden über `.gitignore` ausgeschlossen. Eine private Remote-Sicherung wird erst nach Freigabe des Zielsystems angelegt.

---

### Task 1: Den bestehenden Stand als unveränderliche Basis sichern

**Objective:** Der aktuell geprüfte CI-Stand ist unabhängig von späteren Änderungen wiederherstellbar.

**Files:**
- Create: `.gitignore`
- Create: `CHANGELOG.md`
- Modify: keine Produktdatei

**Step 1: Git-Status und mögliche sensible Dateien prüfen**

Run:
```bash
git status --short --branch || true
```

Expected: Das Arbeitsverzeichnis ist derzeit noch kein Repository.

**Step 2: `.gitignore` erstellen**

Ausschließen: `.env`, `.env.*`, `*.token`, `secrets/`, `miro-cache/`, `exports/`, Python-Caches und Editor-Dateien. Die vorhandenen, bewusst versionierten Tests und SVG-Logos bleiben eingeschlossen.

**Step 3: Initialen Baseline-Test ausführen**

Run:
```bash
python -m unittest -v
node portal-check.js
```

Expected: alle bestehenden Tests erfolgreich.

**Step 4: Git initialisieren und Basis committen**

Run:
```bash
git init -b main
git add .
git diff --cached --check
git commit -m "chore: establish ci portal baseline"
git tag -a v1.0.0-ci-baseline -m "Tested Pokale Meier CI portal baseline"
```

**Step 5: Baseline verifizieren**

Run:
```bash
git status --short --branch
git tag --list
git log --oneline --decorate -1
```

Expected: sauberer `main`-Branch, Tag `v1.0.0-ci-baseline`, kein untracked Kunden- oder Geheimnis-Export.

### Task 2: Aktive-Kunden-Modell gemeinsam festlegen

**Objective:** Es gibt ein kleines, eindeutiges Datenmodell statt einer unstrukturierten Miro-Board-Liste.

**Files:**
- Create: `docs/active-customer-dashboard-data-model.md`
- Modify: `test_portal_structure.py`

**Step 1: Vorhandene Kundenobjekte und deren Renderer prüfen**

Zu prüfen: Kundendatensatz, Status, nächste Aktion und lokale Speicherung in `pokale-meier-erfolgsportal.html`.

**Step 2: Datenvertrag dokumentieren**

Minimaler Datensatz:
```json
{
  "id": "stable-internal-id",
  "name": "Kundenname",
  "owner": "interne verantwortliche Person",
  "status": "active",
  "stage": "bronze",
  "nextAction": "Onboarding vorbereiten",
  "dueDate": "2026-07-30",
  "miroBoardUrl": "https://miro.com/app/board/.../",
  "miroBoardId": "optional-known-board-id",
  "source": "manual",
  "lastSyncedAt": null
}
```

Statuswerte für Gen 1.1: `active`, `paused`, `completed`, `archived`. Das Dashboard zeigt nur `active`; pausierte Kunden werden separat filterbar, aber nicht gelöscht.

**Step 3: Fehlertests zuerst ergänzen**

Tests müssen mindestens beweisen:
- nur `active` erscheint im Dashboard;
- jeder aktive Datensatz hat eine valide HTTPS-Miro-URL;
- überfällige und heute fällige nächste Schritte sind unterscheidbar;
- ein Miro-Link wird mit `target="_blank"` und sicherem `rel="noopener noreferrer"` gerendert.

**Step 4: Test bewusst ausführen**

Run:
```bash
python -m unittest -v
```

Expected: FAIL, weil Dashboard und Datenvertrag noch nicht implementiert sind.

**Step 5: Commit**

```bash
git add docs/active-customer-dashboard-data-model.md test_portal_structure.py
git commit -m "test: define active customer dashboard contract"
```

### Task 3: Dashboard Generation 1.1 als nutzbare interne Ansicht bauen

**Objective:** Ein internes Team kann aktive Kunden sehen, priorisieren und direkt das richtige Miro-Board öffnen.

**Files:**
- Modify: `pokale-meier-erfolgsportal.html`
- Modify: `test_portal_structure.py`
- Modify: `portal-check.js` falls die dortige Validierung betroffen ist

**Step 1: Implementierung nur auf Feature-Branch starten**

```bash
git switch -c feat/active-customer-dashboard
```

**Step 2: Bestehende Kundenobjekte um den Datenvertrag erweitern**

Keine echten Kundendaten als Demo committen. Für Entwicklung nur eindeutig als Testdaten markierte Platzhalter verwenden; reale Daten werden später lokal oder über die Schnittstelle geladen.

**Step 3: Dashboard-Renderer implementieren**

- aktive Kunden nach Fälligkeit priorisieren;
- Karten/Zeilen mit Stufe, nächster Aktion, Fälligkeits-Ampel und Miro-Button;
- leeren Zustand für keine aktiven Kunden;
- klare Anzeige von `Quelle` und `letzter Sync`;
- keine Datenübertragung an Dritte im Frontend.

**Step 4: Einfache Pflegeaktion ergänzen**

Der interne Nutzer kann einen Kunden lokal anlegen oder bearbeiten, einschließlich Miro-Board-URL. Eingaben validieren; kein Speichern ohne gültige Miro-URL bei aktivem Kunden.

**Step 5: Tests und Browser-Smoketest ausführen**

```bash
python -m unittest -v
node portal-check.js
python -m http.server 8766 --bind 127.0.0.1
```

Expected: Tests grün, Startseite liefert HTTP 200, Miro-Button wird korrekt gerendert.

**Step 6: Commit und Release Candidate markieren**

```bash
git add pokale-meier-erfolgsportal.html test_portal_structure.py portal-check.js
git diff --cached --check
git commit -m "feat: add active customer dashboard"
git tag -a v1.1.0-rc.1 -m "Internal active-customer dashboard candidate"
```

### Task 4: Miro-Anbindung sicher vorbereiten

**Objective:** Die spätere Live-Synchronisation wird technisch und datenschutzgerecht vorbereitet, ohne Zugangsdaten in das Portal zu bringen.

**Files:**
- Create: `docs/miro-integration.md`
- Create: `.env.example`
- Modify: `.gitignore`

**Step 1: Miro-Zugriffsweg klären**

Benötigt wird eine von Pokale Meier kontrollierte Miro-Developer-App oder ein geeigneter organisationsverwalteter Zugang mit Leseberechtigung auf die Kundenboards. Die aktuell gültigen Miro-OAuth-Scopes und API-Endpunkte sind vor Umsetzung gegen die Miro-Entwicklerdokumentation zu prüfen.

**Step 2: Verantwortliche Datenquelle festlegen**

Entscheidung dokumentieren:
- Wird die Kundenliste aus einer zentralen Miro-Übersicht gezogen, oder
- wird eine gepflegte Kundenliste verwendet, die jeweils die Miro-Board-ID enthält?

Empfehlung für Gen 1.1: gepflegte interne Kundenliste als führende Zuordnung; Miro liefert ergänzende Board-Metadaten. Das ist robuster, weil Board-Namen nicht automatisch eine verlässliche Kunden-ID sind.

**Step 3: Serverseitigen Sync-Adapter als nächste Generation abgrenzen**

Der Adapter liest Board-Titel, URL und Änderungszeit aus Miro und speichert nur die minimal nötigen Metadaten. Das Browser-Portal ruft ausschließlich den eigenen Adapter auf. Keine Miro-Tokens in HTML/JavaScript.

**Step 4: Dokumentation und Secrets-Template committen**

```bash
git add docs/miro-integration.md .env.example .gitignore
git commit -m "docs: define secure miro synchronization boundary"
```

### Task 5: Interne Bereitstellung und kontrollierte Live-Generation

**Objective:** Das Team kann die neue Version kontrolliert testen; Rückwechsel bleibt möglich.

**Files:**
- Create: `docs/internal-deployment.md`
- Modify: `CHANGELOG.md`

**Step 1: Zielzugriff entscheiden**

Für den Start entweder:
- Windows-Rechner/Server im internen Netz mit abgesichertem Zugriff, oder
- eine freigegebene private Hosting-Umgebung.

Ein öffentlicher Link ohne Authentifizierung ist für Kunden- und Prozessdaten ausgeschlossen.

**Step 2: Release-Checkliste dokumentieren**

Checkliste: Backup, Release-Tag, Tests, Zugriff nur intern, Test mit zwei anonymisierten Testkunden, Miro-Link öffnen, Rückrolltest auf `v1.0.0-ci-baseline`.

**Step 3: Interne Generation ausrollen**

Nach erfolgreicher Prüfung `v1.1.0` taggen. Den lokalen Status und deployed Stand im Changelog festhalten, ohne Geheimnisse oder Kundendaten einzuchecken.

**Step 4: Nach drei echten Nutzungen Feedback in eine Folgeversion überführen**

Auswerten: fehlende Spalten, Such-/Filterbedarf, Statuslogik, Miro-Sync-Qualität. Erst dann Gen 1.2 planen.

---

## Akzeptanzkriterien

- Aktive Kunden stehen auf der Startansicht und sind nach Handlungsbedarf priorisiert.
- Jeder aktive Kunde öffnet mit einem Klick das passende Miro-Board.
- Pausierte/abgeschlossene Kunden verfälschen die aktive Übersicht nicht.
- Kein echter Kunde, keine Board-URL mit sensiblen Daten und kein Token wird in Git versioniert.
- Jeder getestete Stand ist über einen Git-Tag rückholbar.
- Die Lösung bleibt vollständig vom Impact Frame Designer getrennt.

## Benötigte Entscheidung/Zugänge vor Miro-Live-Sync

1. Wer darf die interne Übersicht nutzen (nur Leo, definierte Mitarbeitende, später weitere Rollen)?
2. Was ist die führende Kundenliste: Miro-Übersichtsboard oder interne Stammdatenliste?
3. Soll Miro zunächst nur per Klick geöffnet werden (empfohlen für erste Live-Generation) oder sofort Metadaten automatisch synchronisieren?
4. Welcher interne Bereitstellungsort ist freigegeben: Windows-Server, Synology, oder eine andere private Umgebung?
5. Zugang zu einer Miro-Developer-App bzw. autorisierte OAuth-Verbindung – erst beim Sync-Schritt einrichten, nie im Chat oder im Repository speichern.
