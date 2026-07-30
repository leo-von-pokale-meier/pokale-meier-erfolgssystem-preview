# Vollständiges Erfolgsportal – Kundenportal, Awards und Erfolgskunden

> **For Hermes:** Dieses Dokument ist der verbindliche fachliche Ausbauplan. Es beschreibt absichtlich noch **keine technische Implementierung**.

**Ziel:** Die Kundenansicht wird von einer kompakten Übersicht zu einem echten, mehrseitigen Kundenportal ausgebaut. Jeder Pokale-Meier-Kunde kann seine tatsächlichen Erfolgskunden, ihre Stufe, Nachweise und Aktionen pflegen; Pokale Meier steuert pro Kundenorganisation ein eigenes Award-/Stufenprogramm mit mindestens drei und maximal zehn Stufen.

**Leitidee:** Es gibt drei sauber getrennte Ebenen: (1) die Pokale-Meier-Kundenorganisation im Portal, (2) deren Erfolgskunden und (3) das kundenspezifische Award-Programm. Ein Erfolgskunde zählt erst dann für Fortschritt, Award und Bestenliste, wenn die für seine Stufe festgelegten Nachweise/Aktionen bestätigt sind.

**Bestehende Basis, die erhalten und verbunden wird:** Die statische Kundenansicht liefert die bewährte Kundensprache und die Bereiche Fortschritt, Etappen, Awards, Rangliste und Wissensspeicher. Die lokale Gen-2-Basis liefert Organisationsgrenze, Rollen, Termine, Audit-Log, bestätigte Erfolgsereignisse und Ranglistenberechnung. Die neue Fachversion verbindet beides; sie ersetzt keines davon durch einen funktionsärmeren Onepager.

---

## 1. Verbindliche Begriffe und Abgrenzung

| Begriff | Bedeutung |
|---|---|
| **Portal-Kunde / Kundenorganisation** | Der direkte Pokale-Meier-Kunde mit eigenem Login und eigenem Erfolgsportal. |
| **Erfolgskunde** | Ein Endkunde des Portal-Kunden, bei dem dieser einen konkreten Kundenerfolg/Award erzielt hat. Nicht mit der Portal-Kundenorganisation verwechseln. |
| **Kommender Erfolgskunde** | Vom Portal-Kunden selbst erfasster Name, einer Zielstufe zugeordnet, noch ohne bestätigten Award-Erfolg. |
| **Bisheriger Erfolgskunde** | Ein tatsächlicher, für eine Stufe bestätigter Kundenerfolg. Er erscheint in „Meine Kunden“, in „Meine Awards“ und – bei Freigabe – in „Neue Kundenerfolge“ der Bestenliste. |
| **Stufe** | Kundenspezifische Award-Stufe. Sie hat Reihenfolge, Name, Nutzen/Erklärung, Award-Design, Punkteschwelle und zentrale Aktions-Checkliste. |
| **Aktionsdefinition** | Eine je Stufe zentral definierte, wiederverwendbare Aktion, etwa „Google-Bewertung einholen“. Sie enthält Pflichtstatus, Punkte, Nachweisart und Reihenfolge. |
| **Aktionsabschluss** | Die konkrete, einem Erfolgskunden zugeordnete Erledigung einer Aktionsdefinition inklusive Status, Datum, Nachweis und Bestätigung. |

**Nicht Bestandteil:** Dies wird kein Aftersales-System und keine konkurrierende CRM-, JTL- oder Buchhaltungsdatenquelle. Stammdaten, Empfehlungen und Buchhaltung werden als klar abgegrenzte Portalbereiche geführt bzw. später mit ihren führenden Systemen verbunden.

---

## 2. Ziel-Navigation: echte Unterseiten statt Onepager

Die Kundenansicht erhält einen stabilen Seitenrahmen mit eigener URL/Route pro Bereich, Brotkrumen und einem jeweiligen Detailpfad. Inhalte dürfen nicht mehr nur per Anker in einer langen Seite versteckt werden.

| Navigation in dieser festen Reihenfolge | Seite / Detailseiten | Zweck |
|---|---|---|
| **Dashboard** | `/portal/uebersicht` | **Erste Ansicht nach dem Login.** Gesamtpunktestand, Leuchtfeuer-Score, „Mein Fortschritt“ mit Bronze/Silber/Leuchtfeuer, „Dein nächster Termin“, nächste offene Aktion und kompakter Feed der eigenen Kundenerfolge. |
| **Meine Etappen** | `/portal/etappen`, `/portal/etappen/:id` | Bestehenden Termin-/Beratungsfahrplan, Vorbereitung, kundensichtbare Ergebnisse und nächste Schritte vollständig weiterführen. |
| **Meine Awards** | `/portal/awards`, `/portal/awards/stufen/:id`, `/portal/awards/stufen/:id/aktionen` | Kundenspezifisches Award-Programm, Stufenvisuals, Fortschritt, Regeln und Aktionen darstellen; intern auch konfigurieren. |
| **Meine Kunden** | `/portal/meine-kunden`, `/portal/meine-kunden/kommend`, `/portal/meine-kunden/bisherig`, `/portal/meine-kunden/:id` | Kommende und bisherige Erfolgskunden getrennt führen, Erfolge belegen und Aktionen abarbeiten. |
| **Bestenliste** | `/portal/bestenliste`, `/portal/bestenliste/neue-erfolge` | Eigene Position und sichtbar freigegebene Erfolge anderer Portal-Kunden. |
| **Empfehlungen / Affiliate** | `/portal/empfehlungen` | Empfehlungsprogramm, persönliche Empfehlungslinks, registrierte Empfehlungen, Status und Erfolgsauswertung. |
| **Partner** | `/portal/partner`, `/portal/partner/:id` | Eigene Dienstleistung mit Profil und Anzeige veröffentlichen; der Leuchtfeuer-Score dient Interessenten als klarer Vertrauensindikator. |
| **Wissensspeicher** | `/portal/wissen`, `/portal/wissen/:id` | Bestehende Bereiche Terminwissen, Praxiswissen und Vorlagen ausbauen, nicht durch Terminnotizen ersetzen. |

Interne Mitarbeiter erhalten zusätzlich eine **Kundenverwaltung** mit Kundenliste, Suche und einem eindeutig sichtbaren Kontextwechsel „Kundenportal öffnen als [Organisation]“. Dieser Wechsel ist auditierbar und öffnet dieselben Inhalte in der Kundenansicht, jedoch mit den passenden internen Bearbeitungswerkzeugen.

**Nutzericon oben rechts:** Stammdaten, Buchhaltung und weitere persönliche Einstellungen sind bewusst **keine Hauptreiter**. Sie liegen im Nutzer-Menü als eigene Unterseiten: `/portal/stammdaten`, `/portal/buchhaltung`, Profil/Zugang, Benachrichtigungen und Hilfe.

### 2.1 Dashboard: verbindliche erste Ansicht

Nach dem Login landet jeder Portal-Kunde im Dashboard – nicht in einer Unterseite. Es beantwortet auf einen Blick vier Fragen: **Wo stehe ich? Was ist mein nächster Termin? Was bringt mich voran? Was ist neu?**

- **Leuchtfeuer-Score und Gesamtpunkte:** große, verständliche Kennzahl mit Erklärung, aus welchen bestätigten Erfolgen und Aktionen sie entsteht.
- **Mein Fortschritt:** drei klar erkennbare Journey-Karten **Bronze**, **Silber** und **Leuchtfeuer**. Erreichte Stufen leuchten; die nächste Stufe zeigt Fortschritt und noch nötige Schritte; spätere Stufen sind zurückhaltend dargestellt.
- **Dein nächster Termin:** bleibt zentral und prominent: Datum, Uhrzeit, Format/Ort, Ansprechpartner, Vorbereitung, zugehörige Materialien und ein direkter Weg zur Etappen-Akte.
- **Nächste sinnvolle Aktion:** genau eine priorisierte, offene Aktion aus Etappen oder Erfolgskunden, plus Link zur vollständigen Aufgabe.
- **Zuletzt erzielt:** die jüngsten bestätigten Kundenerfolge, neue Freigaben und neue Punktebewegungen.

---

## 3. „Meine Kunden“: fachliches Verhalten

### 3.1 Startseite „Meine Kunden"

Die Startseite zeigt zwei gleichwertige Bereiche, keine vermischte chronologische Liste:

1. **Kommende Erfolgskunden**
   - pro Award-Stufe gruppiert,
   - klarer Zielstatus: „vorgemerkt“, „in Arbeit“, „bereit zur Übergabe“,
   - Name, Firma optional, vorgesehene Stufe, verantwortliche Person, Zieltermin und kurze Notiz,
   - sichtbarer Button **„Erfolgskunden hinzufügen“**,
   - der Portal-Kunde darf neue Einträge selbst erstellen und die eigenen offenen Einträge bearbeiten/archivieren.

2. **Bisherige Erfolgskunden**
   - pro Award-Stufe gruppiert und nach bestätigtem Datum sortiert,
   - Card mit Name des Gewinners, Stufen-Badge, Award-Design, Fortschritt der Aktionen, bestätigtem Datum und Freigabestatus für die Bestenliste,
   - Filter nach Stufe, Zeitraum, Aktion offen/erledigt und Freigabestatus,
   - jeder Eintrag führt auf eine eigene Erfolgskunden-Akte.

Oben steht eine kleine, verständliche Kennzahlensammlung: bestätigte Erfolge gesamt, Erfolge je Stufe, noch offene Aktionen und Anzahl vorgemerkter kommender Erfolgskunden.

### 3.2 Neuer kommender Erfolgskunde

Ein Portal-Kunde kann selbstständig mindestens den **Namen** und die **Zielstufe** erfassen. Die Eingabemaske startet bewusst klein und erweitert sich erst bei Bedarf:

- Pflicht: Name des Erfolgskunden, Zielstufe.
- Optional: Firma, Ansprechpartner, Ziel-/Übergabetermin, Notiz, Bild-/Designwunsch.
- Systemfelder: Organisation, Ersteller, Erstelldatum, Status, Audit-Historie.
- Ein Erfolgskunde kann nur einer aktiven Stufe der eigenen Kundenorganisation zugeordnet werden.
- Dublettenwarnung innerhalb derselben Kundenorganisation: gleicher normalisierter Name plus gleiche Firma.

Der Eintrag erzeugt **noch keine Punkte** und erscheint noch nicht öffentlich.

### 3.3 Übergang zu „bisherigem Erfolgskunden"

Der Portal-Kunde beantragt aus dem kommenden Eintrag heraus „Erfolg bestätigen“. Er ergänzt dann mindestens Award-/Übergabedatum und die je Stufe verlangten Aktionen/Nachweise.

Statusfolge:

`kommend → in_bearbeitung → nachweis_eingereicht → intern_pruefen → bestaetigt`

Nur der Übergang nach `bestaetigt` verschiebt den Erfolgskunden nach „Bisherige Erfolgskunden“, löst die dafür vorgesehenen Punkte aus und kann – bei Einwilligung – in der Bestenliste erscheinen. Eine Korrektur oder Stornierung erfolgt auditierbar und entfernt Punkte über ein Korrekturereignis, nie durch stilles Löschen.

---

## 4. „Meine Awards“: globales Stufenprogramm je Kundenorganisation

### 4.1 Konfigurationsprinzip

Pokale Meier legt **für jede Kundenorganisation einmalig** ihr eigenes Award-Programm fest. Dieses Programm ist global für alle Erfolgskunden dieser Organisation. Es startet mit mindestens drei Stufen und kann kontrolliert bis zehn Stufen erweitert werden.

- Nur interne Rollen mit Award-Verantwortung dürfen Stufen, Punkte, Designs und Aktionsvorlagen ändern oder veröffentlichen.
- Der Portal-Kunde kann **niemals** neue Stufen hinzufügen. Er sieht und nutzt ausschließlich die für seine Organisation durch das Admin-Board angelegten Stufen; Punktwerte, Pflichtaktionen und Award-Designs kann er nicht manipulieren.
- Neue Stufen bleiben zunächst `Entwurf`, werden geprüft und dann `veröffentlicht`.
- Bereits bestätigte Erfolgskunden behalten eine unveränderbare Momentaufnahme von Stufe, Design, Punkte- und Aktionsregeln. Eine spätere Änderung verfälscht keine Geschichte.

### 4.1a Kundensicht: drei sichtbare Stufen, keine leeren Zukunftsversprechen

In „Meine Awards“ sieht der Portal-Kunde anfänglich nur die drei Stufen **Bronze**, **Silber** und **Leuchtfeuer**. Weitere mögliche Stufen vier bis zehn bleiben vollständig unsichtbar, bis Pokale Meier sie für genau diese Organisation im Admin-Board ergänzt und veröffentlicht.

- **Aktiv/vergeben:** Stufen mit mindestens einem bestätigten Erfolg sind hell, farbig und vollständig bedienbar dargestellt.
- **Bronze:** ist als erreichbare erste Stufe sichtbar und zeigt den konkreten Weg dorthin.
- **Silber und Leuchtfeuer:** bleiben ausgegraut, solange sie dieser Organisation noch nicht vergeben wurden; die Karten erklären nur die nächste Hürde, ohne ein nicht freigeschaltetes Design vorzutäuschen.
- Sobald eine Stufe erstmals erreicht bzw. vergeben wurde, wird sie hell geschaltet und zeigt Award-Visual, Erfolgshistorie, Aktionen und erreichte Punkte.
- Das Admin-Board kann später eine vierte bis zehnte Stufe hinzufügen. Erst nach Veröffentlichung ist sie im Kundenportal sichtbar; sie folgt unmittelbar auf die bisher höchste sichtbare Stufe.

### 4.2 Pflichtfelder einer Stufe

| Feld | Zweck |
|---|---|
| Reihenfolge 1–10 | bestimmt die visuelle Journey und die Sortierung |
| Stufenname | zum Beispiel Bronze, Silber, Leuchtfeuer – frei pro Kundenorganisation |
| Kurzversprechen | warum die Stufe für den Portal-Kunden wertvoll ist |
| Award-Design | ein zentral hochgeladenes Design/Visual für diese Stufe |
| Design-Varianten | optional Mockup, Produktionsfreigabe, ausgeliefertes Referenzbild |
| Freischaltregel | Punkte- und/oder bestätigte-Erfolge-Schwelle |
| Punktwert „Erfolg bestätigt“ | Punkte, die bei bestätigtem Erfolg dieser Stufe vergeben werden |
| Aktions-Checkliste | zentrale Liste aus Pflicht-/optionalen Aktionen inklusive Punkten und Nachweisen |
| Sichtbarkeit | intern, nur eigener Portal-Kunde, Bestenliste mit Einwilligung |
| Version / Status | Entwurf, veröffentlicht, ersetzt, archiviert |

Das hochgeladene Award-Design ist eine zentrale Medienreferenz und wird konsistent wiederverwendet: auf Stufen-Karten, im Fortschritt, bei „Meine Kunden“, auf der Erfolgsdetailseite und bei neuen Erfolgen in der Bestenliste. Es wird nicht pro Bildschirm separat hochgeladen oder dupliziert.

### 4.3 Initiale Stufenstruktur

Für die erste vollständige Fassung werden mindestens diese drei editierbaren Stufen als Ausgangsprogramm angelegt. Namen, Reihenfolge, Punkte und Pflichtstatus bleiben pro Kundenorganisation konfigurierbar.

| Stufe | Beispielhafte zentrale Aktionen |
|---|---|
| **Stufe 1** | Google-Bewertung einholen; Referenzbild mit Award erhalten; Feedback erhalten |
| **Stufe 2** | Nach Empfehlung gefragt; Referenzbild erhalten; Erfolgsposting veröffentlicht |
| **Stufe 3** | Kunde in nächste Stufe gebracht; Neukunde durch Empfehlung gewonnen; Erfolgsvideo oder Podcast gedreht |

Es darf weitere Aktionen geben. Sie werden nicht in jedem Erfolgskunden einzeln frei erfunden, sondern zentral in der Stufen-Konfiguration definiert und beim Anlegen eines Erfolgs als versionierte Checkliste übernommen.

---

## 5. Erfolgskunden-Akte: Uploads, Checkliste und Freigabe

Die Detailseite eines bisherigen Erfolgskunden ist die operative Akte für genau einen realen Kundenerfolg.

### 5.1 Kopfbereich

- Name des Gewinners / Erfolgskunden
- zugehörige Stufe und zentral hinterlegtes Award-Visual
- Status, Übergabedatum, Bestätigungsdatum
- Fortschrittsanzeige für Pflichtaktionen und Punkte
- Sichtbarkeit: nur eigene Organisation / für interne Verwaltung / für Bestenliste freigegeben

### 5.2 Referenzbild und Nachweise

Je Erfolgskunden-Akte gibt es einen klaren Uploadbereich:

- **Referenzbild des Kunden**: Bild des Award-/Erfolgsmoments, Metadaten, Urheber-/Freigabestatus und interne Prüfung.
- **Weitere Nachweise**: abhängig von der Aktionsdefinition, beispielsweise URL zum Erfolgsposting, Link zur Google-Bewertung, Feedbacktext, Empfehlungsreferenz, Video-/Podcast-Link.
- Jeder Upload/Nachweis erhält Ersteller, Zeitpunkt, Status und Prüfer; er bleibt bis zur Freigabe intern bzw. nur in der eigenen Kundenorganisation sichtbar.
- Kein automatisch öffentlicher Upload. Die ausdrückliche Einwilligung für die Bestenliste wird separat erfasst.

### 5.3 Zentrale Checkliste, konkrete Ausführung

Die Stufen-Konfiguration bestimmt die Checklistenpunkte. Die Erfolgskunden-Akte zeigt daraus konkrete, abhakte Einträge:

| Beispielaktion | Nachweis | Standardstatus |
|---|---|---|
| Persönlich überreicht? | Übergabedatum, optional Foto | offen / erledigt / intern bestätigt |
| Erfolgsposting veröffentlicht? | URL oder Screenshot | offen / Nachweis eingereicht / bestätigt |
| Bewertung erhalten? | Link oder Screenshot | offen / Nachweis eingereicht / bestätigt |
| Empfehlung gesichert? | Empfehlungsreferenz / CRM-Verknüpfung | offen / geprüft / bestätigt |
| Upsell platziert? | Angebots-/Auftragsreferenz | offen / geprüft / bestätigt |

Jede Aktionsdefinition erhält mindestens: Bezeichnung, Erläuterung, `pflichtig` oder `optional`, Nachweisart, Punktwert, mögliche Statusfolge und Sichtbarkeit. Optionale Aktionen dürfen die Punkte erhöhen, aber dürfen eine Stufe nicht ungewollt sperren; für eine bestätigte Stufe sind nur die als Pflicht markierten Aktionen entscheidend.

---

## 6. Gamification: Punkte wieder an bestätigte Aktionen koppeln

### 6.1 Regel

Die bisherige Gen-2-Leitplanke bleibt verbindlich: **Nur bestätigte, auditierbare Ereignisse zählen.** Ein Häkchen des Portal-Kunden ist ein eingereichter Nachweis, aber noch keine Punktegutschrift.

Die bekannte bestehende Ausgangslogik wird nicht verworfen: ausgelieferter Award, Award-Foto, Galerie, Empfehlungsprogramm, Anreizsystem, Bronze/Silber-Abschluss und bestätigter Termin sind bereits als bestätigungspflichtige Ereignisse angelegt. Sie wird durch die neuen zentralen Aktionsvorlagen erweitert, statt eine parallele Punktelogik zu schaffen.

### 6.2 Punktelogik je Stufe

- Jede Award-Stufe besitzt einen Punktwert für einen intern bestätigten Erfolg.
- Jede zentrale Aktion kann einen eigenen Punktwert besitzen.
- Punkte entstehen erst beim Status `intern bestätigt`.
- Wiederholte Klicks, erneute Uploads oder doppelte Bestätigung dürfen nicht doppelt punkten.
- Stornierungen/Korrekturen erzeugen ein eigenes Gegenereignis mit Begründung, Autor und Zeitstempel.
- Dashboard, Award-Fortschritt, Erfolgskunden-Akte und Bestenliste lesen denselben berechneten Punktestand.

### 6.3 Anfangsannahmen für die Gewichtung

Das vollständige Punktesystem wird später gemeinsam verfeinert. Für die erste fachliche und technische Fassung gilt jedoch bewusst eine einfache Richtung: **der physische Award und das Erreichen einer Journey-Stufe sind die stärksten Punktetreiber.** Kleine Dokumentationsaktionen sind wertvoll, können einen echten Kundenerfolg aber nicht überholen.

| Bestätigtes Ereignis | vorläufige Gewichtung |
|---|---:|
| Physischer Award nachweislich überreicht/ausgeliefert | 100 Punkte |
| Bronze erstmals erreicht | 150 Punkte |
| Silber erstmals erreicht | 350 Punkte |
| Leuchtfeuer erstmals erreicht | 750 Punkte |
| Bestätigter Erfolgskunde je Stufe | 50 Punkte plus ggf. Stufenbonus |
| Veröffentlichung eines geprüften Erfolgspostings | 25 Punkte |
| Referenzbild/Awardfoto geprüft | 20 Punkte |
| Google-Bewertung bzw. qualifiziertes Feedback geprüft | 30 Punkte |
| Qualifizierte Empfehlung gesichert | 75 Punkte |
| Neukunde aus Empfehlung bestätigt | 200 Punkte |
| Upsell nachweislich platziert | 75 Punkte |
| Bestätigter Termin | 10 Punkte |

Diese Werte sind ausdrücklich **Annahmen für Generation 1 des Punktesystems**. Vor dem Rollout werden sie als Punktekatalog geprüft, versioniert und pro Aktion/Stufe zentral anpassbar gemacht; die Grundregel „physischer Award und Bronze/Silber/Leuchtfeuer dominieren“ bleibt erhalten.

---

## 7. Rangliste: Leuchtfeuer-Score, Kundendetails und neue Kundenerfolge

Die Rangliste ist eine eigene Portal-Unterseite und zeigt künftig eine allgemeine Rangfolge der teilnehmenden Pokale-Meier-Kunden nach **Leuchtfeuer-Score** – nie nach der technischen Bezeichnung „Erfolgspunkte“. Die Detailansicht eines gelisteten Kunden gehört in diesen Bereich: Ein Klick auf eine Ranglisten-Kachel öffnet dessen Kundenprofil innerhalb der Rangliste, nicht die interne Erfolgskunden-Akte.

### 7.1 Allgemeine Kundenrangliste

Jede sichtbare Kunden-Kachel zeigt mindestens:

- Rangplatz, Name bzw. freigegebener Firmenname und Partner-Link, sofern ein Partnerprofil veröffentlicht ist,
- **Leuchtfeuer-Score** als primäre Kennzahl,
- Anzahl der bisher **bestätigten Kundenerfolge** neben dem Score,
- aktuelle Stufe bzw. den Status im Erfolgsprozess,
- eine kurze, vom Kunden eingereichte und intern freigegebene Vorstellungszeile zur Dienstleistung oder zum aktuellen Fokus.

Das Spitzenfeld für die Plätze **1 bis 3** ist visuell hervorgehoben. Es zeigt zusätzlich zum Rang und Score besonders klar den aktuellen Prozessstatus des jeweiligen Kunden, zum Beispiel „arbeitet an Silber“, „Leuchtfeuer erreicht“ oder „Nachweise zur Prüfung eingereicht“, sowie die Vorstellungszeile. Damit bleibt die Spitze verständlich und nicht nur eine anonyme Punkteanzeige.

### 7.2 Einzelansicht eines Ranglisten-Kunden

Die Einzelansicht ist die öffentliche bzw. teilnehmerbezogene Visitenkarte im Ranglistenbereich. Sie enthält nur ausdrücklich freigegebene Daten:

- Name/Firma, Logo, Dienstleistung, Vorstellungszeile und Partner-Link,
- Leuchtfeuer-Score, Rangplatz, Anzahl bisheriger bestätigter Kundenerfolge und aktuelle Prozessstufe,
- freigegebene Awards bzw. Award-Vorschauen und eine chronologische Auswahl freigegebener neuer Kundenerfolge,
- Hinweis, wie der Score als Vertrauensindikator entsteht, ohne interne Einzelregeln, Korrekturen oder nicht freigegebene Nachweise offenzulegen.

Diese Ansicht ist strikt von „Meine Kunden“ und der internen Erfolgskunden-Akte getrennt. Sie erlaubt weder die Bearbeitung fremder Daten noch die Einsicht in private Nachweise, Einwilligungen oder Audit-Ereignisse.

### 7.3 Dynamische Einspalten-Liste „Neue Kundenerfolge“

Neben bzw. unter der Rangliste steht eine dynamische Liste **in genau einer Spalte**. Sie wird absteigend nach bestätigtem Erfolg aktualisiert und erzeugt jeden Listeneintrag ausschließlich aus einem tatsächlich bestätigten bisherigen Erfolgskunden; kommende Einträge erscheinen niemals.

Jeder Eintrag zeigt:

- Gewinnername bzw. zulässige Anonymisierung, Zeitpunkt und erreichte Stufe,
- kleine Vorschau des zentral gepflegten Award-Designs direkt in der Listenansicht,
- den zugehörigen Portal-Kunden mit klickbarem **Partner-Link**, wenn dessen Partnerprofil freigegeben ist,
- für genau diesen Erfolg gewonnene Punkte als nachvollziehbare Ereigniskennzahl,
- optional ein freigegebenes Referenzbild und einen kurzen Erfolgstext.

Es ist je Organisation konfigurierbar, ob Gewinnername, Firmenname, Award-Visual, Bild und/oder Text sichtbar werden dürfen. Standard: nicht öffentlich, nur innerhalb der eigenen Kundenorganisation und für Pokale Meier. Bei fehlender Namens- oder Bildfreigabe wird keine scheinbare Erfolgskarte erfunden; die Rangliste zeigt nur die zulässige anonymisierte Information. „Neue Kundenerfolge“ ergänzt die Gesamt-Rangfolge und die persönliche Journey, ersetzt sie aber nicht.

---

## 8. Bestehende Portalbereiche vollständig einbinden

### Meine Etappen und Termine

Der bestehende Fortschritts- und Etappenbereich wird mehrseitig fortgeführt: bevorstehende Termine, vergangene Termine, Vorbereitung, kundensichtbare Ergebnisse, Materialien, Aufgaben und nächste Schritte. Interne Mitarbeiter können Termine vollständig anlegen, ändern, verschieben, abschließen und bestätigen. Kunden sehen und bearbeiten nur explizit freigegebene Inhalte.

### Wissensspeicher

Terminwissen, Praxiswissen und Vorlagen bleiben eigenständige Inhalte mit Kategorien, Suche, Veröffentlichungsstatus und Zuordnung zu Stufe/Termin. Ein Link aus einer Aktion oder Etappe führt auf den passenden Wissenseintrag statt Text zu kopieren.

### Stammdaten

Zeigt Organisation, Ansprechpartner, Liefer-/Rechnungsadresse und Kommunikationsdaten. Jeder Wert zeigt Quelle und Bearbeitungsregel: Portal-Kunde kann Korrektur vorschlagen; interne Freigabe bzw. späterer Zoho/JTL-Abgleich kontrolliert die Übernahme. Das Portal wird nicht zur Schattenstammdatenquelle.

### Empfehlungen / Affiliate

Zeigt Empfehlungsprogramm, Freigabe-/Teilnahmestatus, persönlichen Link bzw. Code, Erfassungsformular, eingereichte Empfehlungen und ihren Status. Eine bestätigte Empfehlung kann – sofern die Stufenregel dies vorsieht – als Nachweis an eine Erfolgskunden-Akte gekoppelt werden und dann Punkte auslösen.

### Partner

Der Bereich **Partner** ist das sichtbare Schaufenster der Portal-Kunden für ihre eigene Dienstleistung – nicht ein weiteres internes Kundenverzeichnis. Jeder teilnehmende Portal-Kunde kann ein Partnerprofil anlegen und nach interner Freigabe veröffentlichen:

- Dienstleistungsname, Kategorie, Kurzbeschreibung und Leistungsversprechen,
- Logo/Titelbild, Website, Kontakt-/Anfrageweg und Einsatzgebiet,
- optionale Referenzbilder und ausgewählte, ausdrücklich freigegebene Kundenerfolge,
- aktueller **Leuchtfeuer-Score** direkt neben der Dienstleistungsanzeige – inklusive kurzer Erklärung, dass der Score aus bestätigten Erfolgen, Awards und qualitätsrelevanten Aktionen entsteht,
- Sichtbarkeit und Veröffentlichung erfolgen nur nach Prüfung durch Pokale Meier; ein Portal-Kunde kann sein Profil entwerfen und Änderungen einreichen, aber nicht selbst öffentlich schalten.

Der Leuchtfeuer-Score ist hier kein bloßer Ranglistenwert: Er macht gegenüber Interessenten nachvollziehbar, wie belastbar und aktiv ein Partner sein Erfolgssystem nutzt. Details einzelner Nachweise, private Kundendaten und interne Punktkorrekturen bleiben dabei verborgen.

### Buchhaltung

Zeigt Angebote, Rechnungen, Zahlstatus, Fälligkeit, Download und Rückfragen. Schreibende Rechnungs- oder Zahlungslogik bleibt bei JTL bzw. dem führenden Finanzprozess. Portal-Änderungen erzeugen höchstens eine nachvollziehbare Rückfrage, keine stille Zahlungsänderung.

---

## 9. Rechte, Sichtbarkeit und Audit

| Aktion | Portal-Kunde | Pokale-Meier intern |
|---|---|---|
| Kommenden Erfolgskunden anlegen/bearbeiten | ja, innerhalb eigener Organisation | ja |
| Bisherigen Erfolg zur Prüfung einreichen | ja | ja |
| Erfolg abschließend bestätigen/stornieren | nein | ja, berechtigte Rolle |
| Stufen/Award-Design/Aktionsvorlagen ändern | lesen | ja, Award-Verantwortung |
| Weitere Award-Stufe hinzufügen/veröffentlichen | nein | ja, Award-Verantwortung |
| Referenzbild/Nachweis hochladen | ja | ja |
| Upload öffentlich/für Bestenliste freigeben | Einwilligung erteilen | Prüfung und Veröffentlichung |
| Punkte verändern | nein | nur über bestätigte bzw. Korrekturereignisse |
| Partnerprofil anlegen/ändern | Entwurf und Änderung einreichen | prüfen, freigeben, veröffentlichen |
| Kundenportal einer Organisation öffnen | nur eigene Organisation | ja, Kontextwechsel wird auditiert |
| Stammdaten, Affiliate und Buchhaltung | eigene Daten gemäß Feldrechten | voller fachlicher Zugriff entsprechend Rolle |

Alle relevanten Aktionen erfassen mindestens Organisation, Erfolgskunde bzw. Stufe, handelnde Person, Zeitpunkt, vorherigen/neuen Status und Begründung bei Korrektur.

---

## 10. Fachliche Akzeptanzkriterien der vollständigen Version

Die Inhaltsversion gilt als vollständig, wenn folgende Nutzerwege ohne Lücke beschrieben und im späteren Portal möglich sind:

1. Pokale Meier legt für einen neuen Portal-Kunden ein Programm mit mindestens drei Stufen, je Award-Design und zentralen Aktionen an und veröffentlicht es.
2. Das Dashboard ist die erste Ansicht und zeigt Gesamtpunkte, Leuchtfeuer-Score, „Mein Fortschritt“ mit Bronze/Silber/Leuchtfeuer sowie „Dein nächster Termin“ zentral an.
3. Der Portal-Kunde sieht unter „Meine Awards“ ausschließlich Bronze, Silber und Leuchtfeuer. Nicht vergebene Silber-/Leuchtfeuer-Stufen sind ausgegraut; weitere Stufen sind unsichtbar, bis sie intern ergänzt und veröffentlicht wurden.
4. Der Portal-Kunde trägt unter „Meine Kunden → Kommende Erfolgskunden“ selbstständig einen Namen für eine gewählte, sichtbare Zielstufe ein.
5. Aus diesem Eintrag entsteht durch Nachweise und Checkliste ein prüfbarer Erfolg; nach interner Bestätigung erscheint er unter „Bisherige Erfolgskunden“ mit richtigem Stufen-Visual.
6. Referenzbild, Erfolgsposting, Bewertung, Empfehlung und Upsell können stufenspezifisch dokumentiert, geprüft und punktetechnisch korrekt gewertet werden.
7. Die allgemeine Rangliste zeigt Teilnehmer nach Leuchtfeuer-Score, bestätigte Kundenerfolge, Prozessstatus, Vorstellungszeile und für die drei Spitzenplätze eine hervorgehobene Statusdarstellung.
8. Die Einzelansicht eines Ranglisten-Kunden zeigt nur freigegebene Profil-, Award- und Erfolgsvorschauen; sie trennt sich vollständig von fremden Akten und privaten Nachweisen.
9. Ein bestätigter und freigegebener Erfolg erscheint in der einspaltigen dynamischen Liste „Neue Kundenerfolge“ mit Gewinnername bzw. Anonymisierung, Stufe, Award-Vorschau, Partner-Link und den für diesen Erfolg gewonnenen Punkten.
10. Ein freigegebenes Partnerprofil stellt die eigene Dienstleistung mit Leuchtfeuer-Score als Vertrauensindikator dar, ohne private Kunden- oder Nachweisdaten offenzulegen.
11. Alte Kernbereiche – Etappen/Termine, Wissensspeicher, Empfehlungen/Affiliate sowie Stammdaten und Buchhaltung im Nutzer-Menü – sind als ausbaufähige Unterseiten vorhanden und nicht verloren.
12. Interne Mitarbeiter können für jeden Kunden in dessen Portal wechseln und Termine, Materialien, Awards, Visuals und Prüfungen vollständig bearbeiten, ohne dass andere Kundenorganisationen Daten sehen.

---

## 11. Geplante technische Reihenfolge – erst nach fachlicher Freigabe

1. Die festgelegten Anfangsannahmen für das Punktesystem als versionierten zentralen Punktekatalog hinterlegen und anschließend mit echten Nutzungserfahrungen verfeinern.
2. Datenmodell für `AwardProgram`, `AwardStage`, `StageActionDefinition`, `SuccessCustomer`, `SuccessAction`, `EvidenceAsset`, `Consent` und `ScoreEvent` fachlich finalisieren.
3. Rechte- und Sichtbarkeitsmatrix gegen die bestehenden Gen-2-Rollen ergänzen.
4. Mehrseiten-Navigation und bestehende Kundenansichtsbereiche in eine durchgängige Informationsarchitektur überführen.
5. Award-/Stufenverwaltung intern, danach „Meine Kunden“ mit kommend/bisherig implementieren.
6. Nachweise, Checklisten, Bestätigung und idempotente Punktelogik implementieren.
7. Allgemeine Rangliste, Ranglisten-Einzelansicht und die einspaltige Liste „Neue Kundenerfolge“ ausschließlich aus bestätigten, freigegebenen Daten aufbauen.
8. Partner, Empfehlungen/Affiliate sowie Stammdaten und Buchhaltung im Nutzer-Menü als getrennte Portalmodule einbinden.
9. Jeden Nutzerweg mit Rollen-, Mandanten-, Punkte- und Sichtbarkeitstests absichern.

**Versionsregel:** Dieses Fachkonzept ist die verbindliche Quelle für die vollständige Portalversion. Jede spätere Konzept-, UI- oder technische Versionsänderung muss die Anforderungen aus Kapitel 7 – Leuchtfeuer-Score, Kunden-Einzelansicht, Top-3-Status, bestätigte Kundenerfolge, Award-Vorschau, Punkte des Ereignisses und Partner-Link – erhalten oder eine explizit dokumentierte fachliche Änderung enthalten.

**Bewusste Nicht-Entscheidung bis zur technischen Umsetzung:** Konkrete technische Framework-Wechsel, Hosting und externe Integrationen werden nicht vorgezogen. Erst diese fachliche Fassung inklusive der vorläufigen Punktelogik freigeben, dann wird sie auf der vorhandenen Gen-2-Basis implementiert.
