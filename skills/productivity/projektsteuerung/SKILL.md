---
name: projektsteuerung
description: "Use for Pokale Meier project portfolio, priorities, tasks, and generations."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Projektsteuerung

## System of Record

| Ebene | Verbindliche Heimat |
|---|---|
| Strategie, Priorität, Generation, WIP und Blocker | GitHub Organization Project **„Pokale Meier – Portfolio und Umsetzung“** (#2) |
| Umsetzungsauftrag, Akzeptanzkriterien, Blocking Edges und Review | Issue/PR im verantwortlichen Repository |
| Dauerhaftes Produkt- und Betriebswissen | Repository-Dokumentation |

Repositories sind technische Heimat einer entschiedenen Umsetzung – nicht die erste Ablage für eine neue Idee.

## Verbindlicher Ablauf

1. **Einordnen statt vorschnell bauen.** Bestehende Projekte, Repositories, Initiative und offene Issues prüfen. Neue Ideen als `Inbox` erfassen; kein neues Repository ohne mindestens zwei Systemgrenzen (eigenes Deployment/Release, Berechtigungen/Secrets, anderer Owner/Team oder unabhängig versionierbares Paket).
2. **Nur eine strategische Initiative aktiv.** Genau eine strategische Initiative darf `In Arbeit` sein. Anderes bleibt `Bereit`, `Blockiert` oder `Parkplatz`.
3. **Gen 1 konkretisieren.** Für jede aktive Initiative: Nutzer, kleinster real nutzbarer Live-Stand, Lernsignal, Owner, nächster Schritt und Blocker festhalten.
4. **Arbeit in vertikale Tickets schneiden.** Für mehrsitzige Vorhaben zuerst `skills/engineering/to-spec`, dann `skills/engineering/to-tickets` nutzen. Jedes Ticket ist ein einzeln prüfbarer End-to-End-Slice, passt in eine frische Sitzung und benennt nur echte Blocking Edges. Arbeite stets die unblocked Frontier.
5. **Live lernen.** `skills/productivity/live-generationen` anwenden: GEN1 live und eng, GEN2 aus realem Engpass, GEN3 stabilisieren oder skalieren.
6. **Status beweisen.** Bei jedem Abschluss Project und Issue mit Live-Stand, Lernsignal, Ergebnis/Nachweis, nächstem kleinsten Schritt und Blocker aktualisieren. Ohne belegten Live- oder Prüfnachweis ist nichts „Erledigt“.

## Pflichtfelder für konkrete Arbeit
- `Arbeitsstatus`, `Art`, `Bereich`, `Wirkung`, `Priorität`
- `Generation`, `Arbeitspaket`, `Nächster Schritt`
- `Abhängigkeit / Blocker`, `Ausführungsart`, `Qualitätssicherung`
- `Ergebnis / Nachweis`; bei aktiver Arbeit außerdem genau ein verantwortlicher Assignee.

## Arbeitsrhythmus
Vor jeder Umsetzung die aktuelle Project-#2-Sicht und die offenen Issues des Ziel-Repositories lesen. Nur Aufgaben in `GEN1 – Aktive Arbeit` mit geklärten Blocking Edges anfangen. Unklare Ziele, Nutzen, Prioritäten oder Entscheidungen zuerst mit `leos-projekt` und anschließend gezieltem Grilling klären; nicht raten.

## Abgrenzungen
- Keine parallelen, voneinander driftenden Tasklisten in Portfolio und Repository führen: Portfolio steuert, Issue spezifiziert.
- Keine Statuseskalation, Generationenzuordnung oder neue Initiative ohne belastbare Fakten bzw. ausdrückliche Entscheidung.
- Kundenwirksame, irreversible oder datenverändernde Schritte zuerst als sicheren, reversiblen Pilot oder nach Freigabe.

## Verifikation
- [ ] Ein Portfolio-Item zeigt Generation, Owner, nächsten Schritt und Blocker.
- [ ] Das verantwortliche Repository enthält verlinkte, akzeptanzfähige Issues für die aktive Umsetzung.
- [ ] Gen 1 ist real nutzbar bzw. klar als noch nicht live markiert.
- [ ] Nachweise und Lernsignale sind nicht bloß behauptet.
