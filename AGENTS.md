# Agent-Arbeitsregeln · Pokale Meier Erfolgssoftware

## Matt-Pocock-Skillset ist Standard

Für jede nicht-triviale Aufgabe sind die im aktiven Agentenprofil verfügbaren
Matt-Pocock-Skills als Standard-Arbeitsweise zu verwenden. Die Auswahl erfolgt
nach der tatsächlichen Aufgabe, nicht pauschal.

- **Orientierung & Klärung:** `wayfinder`, `ask-matt`, `to-questionnaire`,
  `decision-mapping`, `domain-modeling`, `ubiquitous-language`.
- **Spezifikation & Planung:** `to-spec`, `to-tickets`, `codebase-design`.
- **Implementierung & Qualität:** `tdd`, `diagnose`, `diagnosing-bugs`,
  `code-review`, `resolving-merge-conflicts`, `git-guardrails` (soweit im
  Profil installiert und für die Aufgabe passend).
- **Recherche, Wissensarbeit & Übergabe:** `research`, `claude-handoff`,
  `obsidian-vault` sowie die passenden Schreib-/Lehrskills.

Vor Beginn einer passenden Aufgabe den relevanten Skill laden und dessen
Vorgehen befolgen. Keine unpassenden Skills nur der Vollständigkeit halber
laden. Wenn ein benötigter Skill im aktiven Profil nicht verfügbar ist, den
Namen und die Auswirkung transparent nennen; keine sicherheitsrelevanten
Installationen oder dauerhafte Hooks ohne ausdrückliche Freigabe erzwingen.

## Verbindlicher Arbeitsablauf

1. Ziel, vorhandenen Kontext und betroffene Dateien prüfen.
2. Bei Architektur-, Produkt- oder unklaren Anforderungen zunächst klären und
   spezifizieren, bevor Implementierung beginnt.
3. Bei Codeänderungen testspezifiziert arbeiten; vor Abschluss passende Tests
   oder andere reale Verifikation ausführen.
4. Ergebnisse nur mit tatsächlich ausgeführten Prüfungen, roher Werkzeugausgabe
   oder klar benannten Grenzen als verifiziert melden.
5. Bei komplexen, wiederkehrenden Erkenntnissen eine wartbare Skill- oder
   Projektdokumentation statt nur einer einmaligen Chatnotiz pflegen.

## Projektgrenzen

- Erfolgssoftware und Impact Frame Designer bleiben fachlich, technisch und in
  der Kommunikation getrennt.
- Die Gen-2-Referenzimplementierung ist nur für lokalen Testbetrieb vorgesehen.
  Keine echten Kundendaten, Zugangsdaten oder Produktionssecrets committen.
- Sicherheits-, Datenschutz- und Produktionsentscheidungen dürfen nicht aus
  einer Demo-Annahme abgeleitet werden.
