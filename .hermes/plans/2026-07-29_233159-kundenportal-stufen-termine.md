# Erfolgssystem Gen 2 – Kundenportal, Stufen und Termine Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Das bisher lokale interne Erfolgsportal wird zu einer sicheren, mehrmandantenfähigen Web-Anwendung mit interner Verwaltung, Kundenzugängen, beratungsstufenbasierten Terminen, geteilter Termindokumentation, TL;DV-gestützter KI-Auswertung und späteren Zoho-/JTL-Synchronisationen.

**Architecture:** Die aktuelle statische HTML-Datei bleibt als UI-Prototyp und fachliche Referenz erhalten. Gen 2 erhält einen Server, eine Datenbank, eine sichere Anmeldung und getrennte Rollen/Ansichten. Ein API- und Ereignis-Layer verbindet später TL;DV, Zoho CRM und JTL; der Kern bleibt dabei unabhängig von den einzelnen Anbietern.

**Tech Stack:** React/TypeScript-Frontend, Server-API (TypeScript), relationale Datenbank (PostgreSQL), Authentifizierung mit serverseitigen Sessions/Rollen, n8n für Integrations-Orchestrierung, bestehende Pokale-Meier-CI.

---

## 1. Zielbild und verbindliche Trennung

### Interne Pokale-Meier-Ansicht
- Interne Nutzer anlegen, deaktivieren und rollenbasiert berechtigen.
- Kunden anlegen, bearbeiten, archivieren; Löschen nur als kontrolliertes Soft Delete mit Audit-Nachweis.
- Prozessstufe, Termine, Aufgaben, Freigaben, interne Notizen, Adressen und externe System-IDs verwalten.
- Interne Notizen dürfen nie in der Kundenansicht auftauchen.

### Kundenansicht
- Jeder Kundenorganisation wird ein oder mehrere Kunden-Logins zugeordnet.
- Kunden sehen nur ihre eigene Organisation, ihre eigenen Termine, bestätigten Gesprächsinhalte, Aufgaben, Meilensteine und Gamification.
- Kunden buchen, verschieben oder stornieren Termine innerhalb freigegebener Regeln.
- Kunden legen ihre eigenen erfolgreichen Endkunden an. Erst ein deduplizierter und bestätigter Endkunde löst Gamification aus.
- Kunden können nur gemeinsame Felder bearbeiten; interne Felder bleiben getrennt.

### Integrationsansicht
- Zoho CRM wird voraussichtlich führend für CRM-Kontakte, Firmen und Kunden-/Adressstammdaten.
- JTL bleibt führend für Aufträge, Rechnungen, Lieferungen und operative Auftragsdaten.
- Das Erfolgssystem speichert nur die benötigten Spiegel-IDs und fachliche Prozessdaten; es darf keine konkurrierende Stammdatenquelle werden.
- TL;DV liefert Gesprächsaufzeichnung/Zusammenfassung an einen kontrollierten Import-Endpunkt; es ist nicht die Prozessdatenbank.

## 2. Offene fachliche Entscheidungen vor der Implementierung

1. Die vollständigen echten Beratungsstufen, Termine, Fragen, Pflichtfelder, Entscheidungsregeln und Folgeaufgaben aus Miro bereitstellen. Bis dahin keine Stufenlogik erfinden.
2. Für jede Terminart festlegen: buchbar durch Kunde, buchbar durch intern, Dauer, Vorlauf, Storno-Regel, benötigte Teilnehmer, Videolink/Ort und Nachbereitung.
3. Definieren, wann ein vom Kunden erfasster Endkunde zählt: nur neu angelegt, zusätzlich geprüft, oder erst nach realem Folgeauftrag.
4. Rollen bestätigen: `Systemadmin`, `Beratungsleitung`, `Berater`, `Designer/Produktion`, `Lesen intern`, `Kunden-Admin`, `Kunden-Mitglied`.
5. Datenquelle für Adressen entscheiden: Zoho CRM als Standardspiegel, JTL als operative Validierung; bei Konflikt die führende Quelle pro Feld dokumentieren.
6. TL;DV-Zugang prüfen: verfügbarer API-/Webhook-Zugang, Meeting-ID-Übergabe, Datenfelder, Rechte, Aufbewahrung und DSGVO-Freigabe.

## 3. Datenmodell zuerst erstellen

### Task 1: Organisations- und Nutzerbasis

**Objective:** Sichere Trennung zwischen Pokale Meier, Kundenorganisationen und deren Nutzern schaffen.

**Files:**
- Create: `apps/api/src/modules/auth/*`
- Create: `apps/api/src/modules/organizations/*`
- Create: `apps/api/src/modules/users/*`
- Create: `packages/database/schema/*`
- Test: `apps/api/test/auth-and-tenancy.test.ts`

**Schritte:**
1. Tabellen/Entitäten für `Organization`, `User`, `Membership`, `Role`, `Session`, `AuditLog` anlegen.
2. Jeder Datensatz erhält `organizationId`; interne Pokale-Meier-Nutzer bekommen eine eigene interne Organisation.
3. Serverseitige Passwort-Hashing-, Einladungs- und Session-Logik implementieren; keine LocalStorage-Rollen als Sicherheitsmechanismus verwenden.
4. Jede API-Abfrage erzwingt Mandantentrennung und Berechtigungsprüfung.
5. Failing Tests für Organisationsgrenzen und Rechte schreiben, dann Implementierung testen.

**Validation:** Ein Kundenlogin kann weder URL-manipuliert noch über die API Daten eines anderen Kunden lesen oder ändern. Jede Rollenänderung erscheint im Audit-Log.

### Task 2: Kundenakte und externe Identitäten

**Objective:** Die bestehende interne Kundenmaske auf eine persistente, integrationsfähige Kundenakte heben.

**Files:**
- Modify: `packages/database/schema/*`
- Create: `apps/api/src/modules/customers/*`
- Create: `apps/web/src/features/internal-customers/*`
- Test: `apps/api/test/customer-record.test.ts`

**Schritte:**
1. Kundenakte mit Organisation, Kontaktpersonen, Liefer-/Rechnungsadresse, Status sowie interner/externer Sichtbarkeit modellieren.
2. Externe IDs getrennt speichern: `zohoAccountId`, `zohoContactId`, `jtlCustomerNumber`, später `jtlOrderIds`.
3. Soft Delete/Archivierung statt physischem Löschen implementieren.
4. Änderungsprotokoll pro Feld/Version ergänzen: Autor, Zeit, Quelle, vorheriger und neuer Wert.
5. Bestehende UI-Felder aus `pokale-meier-erfolgsportal.html` nachbauen und Datenmigration aus der lokalen Exportdatei als einmaligen Import vorbereiten.

**Validation:** Ein Admin kann Kunden anlegen, ändern und archivieren. Ein Berater hat nur freigegebene Schreibrechte. Interne Notizen bleiben über jede Kunden-API unsichtbar.

### Task 3: Prozessvorlagen statt fest codierter Stufen

**Objective:** Beratungsstufen, Terminarten, Pflichtfelder und Folgeentscheidungen als administrierbare Vorlagen umsetzen.

**Files:**
- Create: `apps/api/src/modules/process-templates/*`
- Create: `apps/web/src/features/process-builder/*`
- Test: `apps/api/test/process-template.test.ts`

**Schritte:**
1. Entitäten `Program`, `Stage`, `AppointmentType`, `FieldDefinition`, `DecisionRule`, `TaskTemplate` erstellen.
2. Startstruktur Bronze, Silber und Leuchtfeuer nur als editierbare Initialvorlage abbilden.
3. Die echten Miro-Skripte in Vorlagen überführen: Reihenfolge, Terminfragen, Pflichtantworten, Entscheidungspfade, automatische Folgeaufgaben.
4. Versionierte Veröffentlichung einführen: laufende Kunden behalten ihre Prozessversion; neue Kunden bekommen die aktuell veröffentlichte Version.
5. Interne Vorschau bauen, die prüft, ob jede Stufe vollständig buchbar und auswertbar ist.

**Validation:** Eine veröffentlichte Vorlage kann nachträglich weiterentwickelt werden, ohne die historische Terminlogik eines laufenden Kunden zu verändern.

### Task 4: Termine, Buchung und geteilte Gesprächsakte

**Objective:** Kunden und interne Berater arbeiten an derselben Termininstanz, aber mit getrennten Sichtbarkeiten.

**Files:**
- Create: `apps/api/src/modules/appointments/*`
- Create: `apps/web/src/features/appointments/*`
- Create: `apps/web/src/features/customer-portal/*`
- Test: `apps/api/test/appointments.test.ts`

**Schritte:**
1. `Appointment` mit Terminart, Prozessstufe, Teilnehmern, Status, Zeit, Buchungsquelle und Meeting-Referenz anlegen.
2. Verfügbarkeits-/Buchungsregeln zunächst mit internen Zeitfenstern abbilden; erst danach Kalenderanbieter anbinden.
3. Pro Termin eine geteilte Gesprächsakte mit Feldwerten erstellen. Jedes Feld erhält Sichtbarkeit `internal`, `shared` oder `customer`.
4. Kunden können nur die freigegebenen Buchungs- und Eingabefelder sehen; interne Nachbereitung und Coaching-Notizen bleiben intern.
5. Nach Abschluss erzeugt die Terminart die nächsten Aufgaben/Terminvorschläge entsprechend der veröffentlichten Prozessvorlage.

**Validation:** Kunde bucht einen berechtigten Termin, sieht bestätigte gemeinsame Inhalte und kann keine internen Auswertungen lesen. Interne Bearbeitung aktualisiert nur die erlaubten Kundenfelder.

### Task 5: TL;DV-Import und KI-Auswertung pro Terminart

**Objective:** Eine TL;DV-Aufzeichnung/Summary wird sicher dem richtigen Beratungstermin zugeordnet und in die gemeinsame Gesprächsakte übernommen.

**Files:**
- Create: `apps/api/src/modules/integrations/tldv/*`
- Create: `apps/api/src/modules/ai-evaluations/*`
- Create: `n8n/workflows/tldv-appointment-import.json`
- Test: `apps/api/test/tldv-import.test.ts`

**Schritte:**
1. Erst den tatsächlichen TL;DV-Integrationsweg verifizieren (API, Webhook, Export oder n8n-Connector); keine Zugangsdaten im Projekt ablegen.
2. Jede Terminart verweist auf genau eine versionierte `AiEvaluationScript`-Vorlage mit erwarteten Feldern, Zusammenfassungsregeln und Sichtbarkeiten.
3. TL;DV-Ereignis an Meeting-ID/Termin-ID matchen; unklare Zuordnung in eine interne Klärliste statt automatisch in einen Kunden zu schreiben.
4. KI-Ausgabe als Entwurf speichern, Felder gegen Terminvorlage validieren und intern freigeben lassen.
5. Erst nach Freigabe die `shared`-Felder in die Kundenansicht übertragen; Quellenlink, Rohdaten-Referenz, Skriptversion und Freigabe protokollieren.

**Validation:** Falsche oder nicht zuordenbare Zusammenfassung wird niemals einem Kunden sichtbar. Eine freigegebene Zusammenfassung befüllt nur die passenden gemeinsamen Felder und bleibt nachvollziehbar versioniert.

### Task 6: Kunden-Erfolge und Gamification

**Objective:** Kunden können eigene Erfolge erfassen; nur definierte, prüfbare Ereignisse treiben ihre Bestenliste an.

**Files:**
- Create: `apps/api/src/modules/customer-successes/*`
- Create: `apps/api/src/modules/gamification/*`
- Create: `apps/web/src/features/customer-leaderboard/*`
- Test: `apps/api/test/gamification.test.ts`

**Schritte:**
1. Entitäten für `CustomerSuccess`, Nachweis, Prüfstatus, verantwortlichen Kundenbenutzer und Zeitstempel anlegen.
2. Ein neuer Endkunde erzeugt zunächst ein Ereignis `pending`; erst nach der gewählten Regel wird es `approved` und zählt.
3. Monats-, Jahres- und Gesamtrangliste immer aus nachvollziehbaren, bestätigten Ereignissen berechnen.
4. Gleichstände, Korrekturen, Stornos, Zeitfenster, Sichtbarkeit und Belohnungen in Konfiguration festlegen.
5. Kundenansicht mit persönlichem Fortschritt, Freischaltungen und Bestenliste bauen; keine Namen/Daten anderer Kunden ohne explizite Freigabe zeigen.

**Validation:** Ein unbestätigter oder zurückgezogener Eintrag verändert keinen Score. Änderungen sind auditierbar und die Rangliste ist reproduzierbar.

### Task 7: Zoho- und JTL-Integrationsbasis

**Objective:** Saubere, rückspielbare Synchronisation ohne konkurrierende Stammdaten oder Doppelanlage schaffen.

**Files:**
- Create: `apps/api/src/modules/integrations/zoho/*`
- Create: `apps/api/src/modules/integrations/jtl/*`
- Create: `n8n/workflows/zoho-customer-sync.json`
- Create: `n8n/workflows/jtl-order-sync.json`
- Test: `apps/api/test/external-sync.test.ts`

**Schritte:**
1. Feldmapping, führendes System und Konfliktregel pro Feld schriftlich definieren.
2. Zuerst lesende, idempotente Synchronisation bauen: Zoho-Firma/Kontakt/Adressen und JTL-Kundennummer/Aufträge einlesen.
3. Synchronisationsereignisse, Zeitstempel, Quell-ID, Fehlerstatus und manuellen Wiederanstoß speichern.
4. Erst nach erfolgreicher Beobachtungsphase gezielte Rückschreibungen erlauben – jeweils mit Freigabe und ohne stille Überschreibung.
5. n8n-Workflows mit Funktionsbeschreibung, Fehlerpfad und Datenminimierung dokumentieren.

**Validation:** Wiederholter Import erzeugt keine Dubletten. Ein Konflikt wird sichtbar protokolliert. Das Portal schreibt in dieser Phase keine Stammdaten zurück.

### Task 8: Produktionstauglichkeit und Freigabe

**Objective:** Aus dem Vorschau-Link wird ein sicherer Team- und Kundenbetrieb.

**Files:**
- Create: `infra/*`
- Create: `.github/workflows/*`
- Create: `docs/security-and-operations.md`
- Test: `apps/api/test/authorization-regression.test.ts`

**Schritte:**
1. Die öffentliche GitHub-Pages-Vorschau nur für UI-Demos nutzen; keine Kunden- oder Zugangsdaten dort speichern.
2. Geschütztes Hosting, Datenbank-Backups, TLS, Monitoring, Fehlerprotokoll und getrennte Umgebungen `preview`/`production` einrichten.
3. Datenschutz-/Aufbewahrungskonzept für Gesprächsdaten und TL;DV-Auswertungen festlegen.
4. Rechte-, Mandanten- und Sichtbarkeitsregressionen automatisiert testen.
5. Mit mindestens drei echten Kunden in einem begrenzten Pilotlauf testen, Feedback einarbeiten und erst dann ausrollen.

**Validation:** Ein externer Sicherheits-/Rechtecheck bestätigt Mandantentrennung; der Pilot arbeitet mit echten Terminen, realer Auswertung und wiederherstellbaren Daten.

## Bestehende Dateien und ihr Platz in Gen 2

- `pokale-meier-erfolgsportal.html`: bleibt Referenz für die bewährte interne Kundeneingabe und CI, wird nicht als Sicherheits-/Datenbasis weiterverwendet.
- `portal-core.js`: fachliche Startpunkte für Rollen, Kunden, Adressen, Vereinbarungen und Gamification; wird durch serverseitige Domänenlogik ersetzt bzw. migriert.
- `test_portal_structure.py`, `test_portal_core.js`, `test_internal_workspace.py`: behalten wir als Regression für den Prototyp; Gen 2 erhält zusätzlich API-, Rechte-, Tenant- und End-to-End-Tests.

## Risiken und Leitplanken

- Die aktuelle Pages-Vorschau ist öffentlich und LocalStorage-basiert; sie darf nie echte Kundendaten oder Logins enthalten.
- TL;DV-Anbindung ist technisch und datenschutzrechtlich erst nach Access-/API-Prüfung verbindlich planbar.
- Ohne Miro-Terminskripte können wir das Framework bauen, aber keine finale Beratungslogik behaupten.
- Versionierung muss vor dem ersten echten Kundentermin stehen, damit nachträgliche Prozessänderungen historische Inhalte nicht verfälschen.
- Zoho und JTL werden zunächst lesend und mit klarer Systemführerschaft angebunden.
