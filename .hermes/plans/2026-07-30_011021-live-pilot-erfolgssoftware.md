# Live-Pilot Erfolgssoftware Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Die aktuelle lokale Gen-2-Referenz zu einem geschützten, nur für Pokale Meier betriebenen Live-Piloten entwickeln, der Terminabläufe automatisch dokumentiert, Kunden klare nächste Schritte zeigt, Buchungen und CRM-Synchronisation kontrolliert automatisiert und geprüfte Award-/Silber-Upsells unterstützt.

**Architecture:** Der Pilot bleibt zunächst eine einzelne Pokale-Meier-Instanz, keine verkaufbare SaaS. Die vorhandene SQLite/WSGI-Referenz wird in eine containerisierte Web-App mit PostgreSQL, einem separaten Hintergrund-Worker und einer auditierbaren Integrationsschicht überführt. Alle externen Eingänge (Buchung, TL;DV, Zoho) werden idempotent in eine Integrations-Inbox geschrieben und erst dann fachlich verarbeitet.

**Tech Stack:** Python 3.11+, FastAPI/Starlette, PostgreSQL, SQLAlchemy/Alembic, Redis + RQ oder Celery, Docker Compose, Caddy oder Nginx, GitHub Actions, Sentry/Healthchecks; EU-gehostete Infrastruktur und verschlüsseltes Backup.

---

## Leitplanken

- **Produktphase:** Mehrmonatiger Eigenbetrieb mit ca. zehn echten Pokale-Meier-Kunden; noch keine offene Mandanten-SaaS.
- **Kein Browser-zu-CRM:** Zoho, TL;DV und Buchungssystem werden nur serverseitig über Webhooks/API-Worker angesprochen. Tokens liegen nur im Secret Store.
- **Kein freier CRM-Sync:** Zuerst eine explizite Feld-Mapping-Tabelle und ausgehende Whitelist. Konflikte und Fehler landen in einer manuellen Sync-Queue. Das ersetzt die bisherige „Zoho nur lesend“-Entscheidung erst nach fachlicher Freigabe.
- **Gamification:** nur bestätigte, auditierte Ereignisse; Termin „abgeschlossen“ ist nicht gleich „Punkt gutgeschrieben“.
- **Kundensicht:** strikte Organisationsgrenze und nur freigegebene Inhalte; interne KI-Entwürfe, Transkripte und Prüfhistorie bleiben intern.

## Vor dem ersten Deployment: verbindliche Entscheidungen

### Task 1: Pilot-Betriebsrahmen festlegen

**Objective:** Den Live-Piloten rechts- und betriebssicher eingrenzen.

**Files:**
- Create: `docs/live-pilot/operating-model.md`
- Create: `docs/live-pilot/data-processing-register.md`
- Create: `docs/live-pilot/field-visibility-matrix.md`

**Steps:**
1. Einen festen Pilotkunden-Kreis, Datenschutzinformationen, AVV/Unterauftragnehmer und Aufbewahrungsfristen festlegen.
2. Für Termine, Transkripte, Nachweise, Awards, CRM-Daten und Wissensdateien jeweils Eigentümer, Zweck, Sichtbarkeit und Lösch-/Archivregel dokumentieren.
3. Für die vier Rollen `admin`, `designer`, `berater`, `kundenservice` eine Feldsichtbarkeitsmatrix abschließen; Kundenrolle separat nur lesend.
4. Entscheiden, ob Zoho CRM nur Stammdaten liefert oder welche genau definierten Felder zurückgeschrieben werden dürfen.

**Verification:** Jede automatisierte Datenbewegung hat Datenquelle, Ziel, Rechtsgrundlage, Aufbewahrung und verantwortliche Person.

### Task 2: Infrastruktur und Recovery-Ziel festlegen

**Objective:** Nicht mehr von einem lokalen Rechner und SQLite als Betriebsdatenbank abhängen.

**Files:**
- Create: `deploy/docker-compose.production.yml`
- Create: `deploy/Caddyfile`
- Create: `docs/live-pilot/backup-restore-runbook.md`
- Create: `.env.example`

**Steps:**
1. EU-Hosting auswählen; getrennte produktive PostgreSQL-Datenbank, App-Container, Worker-Container und Reverse Proxy bereitstellen.
2. TLS am Reverse Proxy erzwingen; die App selbst ist nicht direkt aus dem Internet erreichbar.
3. Secrets ausschließlich über Host-/CI-Secret-Store einspielen: Datenbank, Sitzungs-Schlüssel, Zoho, TL;DV, Buchungssystem, Mail.
4. Verschlüsselte tägliche Datenbank-Backups, Aufbewahrung und einen monatlichen Restore-Test einrichten.
5. Health-Endpunkt, strukturierte Logs und Alarmierung bei fehlgeschlagenen Integrationsjobs konfigurieren.

**Verification:** Restore in eine leere Staging-Datenbank; Zugang nur per HTTPS; kein Secret im Git-Verlauf oder Container-Log.

## Kernanwendung für den Pilotbetrieb

### Task 3: WSGI/SQLite-Referenz in eine migrationsfähige App überführen

**Objective:** Die bestehenden Regeln aus `gen2_foundation.py` produktionsfähig und testbar weiterführen.

**Files:**
- Migrate: `gen2_foundation.py` → `app/domain/`
- Migrate: `gen2_app.py` → `app/web/`
- Create: `app/db/models.py`
- Create: `alembic/versions/`
- Modify: `test_gen2_foundation.py`, `test_gen2_gamification.py`, `test_gen2_app.py`

**Steps:**
1. **RED:** Tests für PostgreSQL-kompatible Persistenz, Migration und atomare Terminbestätigung schreiben.
2. `organisations`, `users`, `appointments`, `achievement_events` und `audit_log` als relationale Modelle plus Migrationen anlegen.
3. Die bewährte Zweistufenregel erhalten: `planned → completed → verified`; nur `verified` erzeugt genau ein `appointment_completed`-Ereignis.
4. Jede Statusänderung und jede Integrationswirkung mit Actor, Zeit, Quellsystem und idempotentem Event-Key auditieren.
5. **GREEN:** Unit- und Integrationssuite gegen eine temporäre PostgreSQL-Datenbank ausführen.

**Verification:** Der aktuelle Schutz gegen doppelte Terminpunkte, Kunden-Mandantentrennung und Audit-Protokoll bleibt vollständig grün.

### Task 4: Produktionsreife Anmeldung und Berechtigungen

**Objective:** Den lokalen signierten Cookie-Prototyp durch sichere, widerrufbare Sessions ersetzen.

**Files:**
- Create: `app/security/auth.py`
- Create: `app/web/routes/auth.py`
- Create: `app/security/csrf.py`
- Modify: `app/db/models.py`
- Create: `tests/security/test_auth.py`

**Steps:**
1. **RED:** Tests für Passwort-Hashing (Argon2id), Session-Widerruf, CSRF, Rate-Limit und Mandantentrennung schreiben.
2. Kurzlebige Server-Sessions mit Rotation beim Login und sicherem, HTTPS-only Cookie implementieren.
3. Passwort-Reset per einmaligem, zeitgebundenem Token sowie TOTP-MFA verpflichtend mindestens für interne Rollen umsetzen.
4. Rollenberechtigungen zentralisieren; jede Route erzwingt Organisation und Freigabestatus serverseitig.
5. Login- und Berechtigungsereignisse auditieren.

**Verification:** Automatisierter Test weist nach, dass ein Kundenlogin keine fremde Organisation, keinen internen Entwurf und keinen Token anderer Sessions sehen kann.

### Task 5: Terminakte als dokumentierter Prozessmotor

**Objective:** Aus jedem gebuchten Termin automatisch eine nachvollziehbare, pflegearme Akte machen.

**Files:**
- Create: `app/domain/appointments.py`
- Create: `app/web/routes/appointments.py`
- Create: `app/templates/appointments/`
- Create: `tests/domain/test_appointment_lifecycle.py`

**Steps:**
1. Terminmodell um externen Buchungsbezug, Terminart, Teilnehmer, Checklisten-Vorlage, Status, interne Zusammenfassung, kundensichtbare Zusammenfassung und verpflichtenden nächsten Schritt erweitern.
2. Terminarten mit absichtlich versionierten Platzhalterfragen anlegen; noch keine fachlich erfundenen Beratungsfragen hinterlegen.
3. Nach Terminende automatisch einen internen Entwurf erzeugen bzw. importieren, aber immer mit Status `needs_review`.
4. Erst mit interner Freigabe die kuratierte Zusammenfassung und der nächste Schritt in die Kundenakte übernehmen.
5. Ein konsistentes „Etappe“-UI auf Terminliste, Kundenakte, Dashboard und Award-Fortschritt verwenden.

**Verification:** Ein Termin lässt sich ohne manuelle Doppelpflege von „gebucht“ bis „kundensichtbar bestätigt“ durchspielen; jeder Übergang ist auditierbar.

## Automationen zu den fünf Geschäftszielen

### Task 6: Terminbuchungen über einen sicheren Adapter automatisieren

**Objective:** Buchungen erzeugen oder aktualisieren zuverlässig Terminakten.

**Files:**
- Create: `app/integrations/booking/adapter.py`
- Create: `app/web/routes/webhooks_booking.py`
- Create: `app/jobs/booking_events.py`
- Create: `tests/integrations/test_booking_webhook.py`

**Steps:**
1. Prüfen, ob Zoho Bookings im vorhandenen Zoho-One-Tenant verfügbar und fachlich passend ist; sonst den ausgewählten Kalenderanbieter festlegen.
2. Eine Webhook-Inbox mit Signaturprüfung, Rohpayload-Verschlüsselung/Minimierung, Event-ID und Idempotenzschlüssel bauen.
3. Events `created`, `rescheduled`, `cancelled` in Terminakten übersetzen, ohne handgepflegte Felder zu überschreiben.
4. Buchungsbestätigung und die vorbereitende nächste Mission an die richtige Kundenorganisation koppeln.
5. Nicht zuordenbare Buchungen in eine interne Klärliste senden statt still einen falschen Kunden zuzuordnen.

**Verification:** Derselbe Webhook kann dreimal eintreffen und erzeugt trotzdem genau eine Terminakte; Verschiebung und Storno bleiben nachvollziehbar.

### Task 7: TL;DV-Import als freizugebende Dokumentationspipeline

**Objective:** Transkript und KI-Entwurf reduzieren Pflegeaufwand, ohne unkontrolliert Kundendaten zu veröffentlichen.

**Files:**
- Create: `app/integrations/tldv/adapter.py`
- Create: `app/jobs/tldv_import.py`
- Create: `app/domain/document_review.py`
- Create: `tests/integrations/test_tldv_import.py`

**Steps:**
1. TL;DV-API/Webhook, Meeting-ID-Mapping, Datenminimierung, AVV und Aufbewahrung vorab freigeben.
2. Meeting- und Termin-ID eindeutig verknüpfen; unklare Zuordnungen niemals automatisch veröffentlichen.
3. Terminartspezifischen KI-Entwurf nur intern speichern: Zusammenfassung, Entscheidungen, offene Nachweise, nächster Schritt.
4. Berater-Freigabe als Pflichtschritt implementieren; Kundensicht erhält ausschließlich die freigegebene Kurzfassung.
5. Fehler und fehlende Transkripte in die interne Work-Queue legen.

**Verification:** Ein importiertes Transkript wird ohne Freigabe niemals in der Kundenansicht angezeigt; der Freigabeweg ist im Auditlog sichtbar.

### Task 8: Zoho-CRM-Synchronisation als kontrollierte Outbox

**Objective:** Daten zuverlässig ins CRM übertragen, ohne Schleifen, Überschreiben oder Schattenstammdaten.

**Files:**
- Create: `app/integrations/zoho/crm_client.py`
- Create: `app/integrations/zoho/mapping.py`
- Create: `app/jobs/zoho_outbox.py`
- Create: `docs/live-pilot/zoho-field-mapping.md`
- Create: `tests/integrations/test_zoho_outbox.py`

**Steps:**
1. Erst lesend CRM-Organisation/Kontakt/Auftrag über die externe Zoho-ID verknüpfen.
2. Freigeben, welche Felder zurückgeschrieben werden dürfen: beispielsweise nächster Termin, zuletzt bestätigte Stufe, freigegebener nächster Schritt – niemals interne Notizen oder Rohtranskripte.
3. Jeder ausgehende Schreibvorgang wird als Outbox-Eintrag mit Payload-Hash, Version, Retry-Zähler und Ergebnis gespeichert.
4. Fehlgeschlagene oder fachlich kollidierende Einträge benötigen eine interne Entscheidung; keine blinde Wiederholung.
5. Erst danach eine kleine, explizite Schreibfreigabe in Zoho aktivieren.

**Verification:** Ein bestätigter Termin aktualisiert die erlaubten Zoho-Felder exakt einmal; ein API-Ausfall führt zu sichtbarer Retry-Queue statt Datenverlust.

### Task 9: Award- und Silber-Upsell als hilfreiche, bestätigte Route

**Objective:** Den Sog nach der sichtbaren nächsten Stufe erzeugen, ohne Punkte manipulieren zu können.

**Files:**
- Modify: `app/domain/gamification.py`
- Create: `app/domain/award_offers.py`
- Create: `app/web/routes/customer_journey.py`
- Create: `tests/domain/test_award_offers.py`

**Steps:**
1. Die derzeitigen bestätigten Event-Regeln zentral als versionierte Regeln ablegen; Storno/Korrektur wird durch Korrekturereignis statt Löschen modelliert.
2. Dashboard, Terminakte, Kundenakte und interne Übersicht aus derselben Journey-Projektion speisen: aktueller Stand, nächster Schritt, Nachweisstatus, Award-Nähe.
3. Nach einem bestätigten Erfolg eine passende, informative Silber-Option zeigen: Nutzen, nächster Nachweis, erforderliche interne Freigabe; kein automatischer Warenkorb und kein falscher Zeitdruck.
4. Award-Bestellung, Auslieferung und Bestätigung separat führen; nur die bestätigte Auslieferung zählt die festgelegten Punkte.
5. Prüfen, ob öffentliche Rankings rechtlich und vertraglich nur über explizite Organisationseinwilligung erscheinen dürfen; Standard bleibt nicht öffentlich.

**Verification:** Kunden können keinen Punktestand selbst ändern; Korrekturen bleiben lückenlos sichtbar; ein Silber-Angebot erscheint nur im fachlich passenden, bestätigten Kontext.

## Betrieb und Pilot-Auswertung

### Task 10: Pilot-Release, Monitoring und Lernschleife

**Objective:** Sicher livegehen und vor einer SaaS-Entscheidung echte Betriebserfahrung gewinnen.

**Files:**
- Create: `.github/workflows/test-and-deploy.yml`
- Create: `docs/live-pilot/release-checklist.md`
- Create: `docs/live-pilot/monthly-review.md`

**Steps:**
1. Staging und Produktion trennen; jede Migration zuerst gegen anonymisierte Staging-Daten testen.
2. CI mit Unit-, Integrations-, Mandantentrennungs-, Security- und Migrationschecks aufsetzen.
3. Release-Checkliste: Backup erfolgreich, Restore aktuell, Secrets geprüft, Migration rückwärts bewertet, Monitoring aktiv, Datenschutzänderung dokumentiert.
4. Drei Generationen im Eigenbetrieb steuern: klein nutzbarer Kern → reale Nutzung mit zehn Kunden → Messung und Ausbau.
5. Monatlich messen: manueller Minutenaufwand je Termin, Anteil auto-dokumentierter Termine, offene Prüfungen, Buchungs-zu-Termin-Quote, CRM-Sync-Fehler, Silber-Interesse und tatsächliche Upsells.

**Verification:** Drei Monate stabiler Pilotbetrieb mit wiederholtem Restore-Test, keiner Mandantenverletzung und klar messbarer Reduktion der Terminpflege, bevor ein SaaS-Produktmodell entschieden wird.

## Risiken und offene Entscheidungen

- **Zoho-Schreibzugriff:** widerspricht dem bisherigen „nur lesend“-Start. Erst nach Feldfreigabe, Testtenant und Outbox/Retry aktivieren.
- **TL;DV:** API, Webhook, Meeting-Zuordnung und DSGVO/AVV sind noch nicht spezifiziert; bis dahin bleibt der Terminimport manuell oder CSV-basiert.
- **Buchungssystem:** Zoho Bookings-Verfügbarkeit und gewünschter Kalenderprozess müssen geprüft werden, bevor der Adapter gebaut wird.
- **Hosting:** Eine konkrete EU-Hosting- und Backup-Entscheidung ist erforderlich; GitHub Pages bleibt ausschließlich die fiktive, statische Demo.
- **SaaS erst später:** Erst wenn Prozessvorlagen, Datenmodell, Support-Aufwand, Onboarding und Kosten im Eigenbetrieb mehrfach validiert sind, werden Organisationen als isolierte SaaS-Tenants weiter abstrahiert.
