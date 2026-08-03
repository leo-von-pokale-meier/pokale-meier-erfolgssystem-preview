---
name: github-organization-project-template
description: Use when creating reusable GitHub organization Projects.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# GitHub Organization Project Templates

## Operating Model

| Layer | Source of truth |
|---|---|
| Organization Project | portfolio, priority, current work, blockages, next milestone |
| Repository issue / PR | concrete implementation and review |
| Repository documentation | durable product and operational knowledge |

Use an item-free marked template and a separate **Portfolio und Umsetzung** instance. Never create a repository merely for an idea; capture it in the Project Inbox first.

## Workflow and Fields
- Keep built-in `Status`; use `Arbeitsstatus`: `Inbox`, `Klären`, `Bereit`, `Jetzt`, `In Arbeit`, `Blockiert`, `Review`, `Erledigt`, `Parkplatz`.
- Capture `Art`, `Bereich`, `Wirkung`, `Priorität`, `Nächster Schritt`, `Abhängigkeit / Blocker`, and `Entscheidung nötig`.
- Model live delivery with `Generation`: `GEN1 – Aktive Arbeit`, `GEN2 – innerhalb 3 Monate`, `GEN3 – innerhalb 6 Monate`, `Next Generation – nach GEN3`.
- Every concrete task gets a `Generation` and `Arbeitspaket` (for example Analyse & Zielbild, Daten & Schnittstellen, Umsetzung, Test & Freigabe, Live-Betrieb & Lernen, Dokumentation).
- Explicit WIP rule: only one strategic initiative is simultaneously `In Arbeit`.

## Required Views
`Roadmap`, `Cockpit`, `Aktive Arbeit (GEN1)`, `Generation 2`, `Generation 3`, `Zielbild`, `Parkplatz`, `Abhängigkeiten`.

## Verification
Before reporting success, remotely verify Project title, fields/options, named views/filters, and that concrete tasks are distributed across generations. Do not maintain drifting technical subtask descriptions in the portfolio: create or link the owning repository issue.
