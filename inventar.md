# Inventar: Globales Claude-Code-Setup (~/.claude)

Reiner Befund, keine Empfehlungen. Alle Bytes sind Roh-Bytes der zitierten/extrahierten Originaltexte; Tokens = Bytes ÷ 4, gerundet — explizit eine Schätzung. Quellen wurden ausschließlich gelesen, nichts unter `~/.claude` verändert.

---

## 1. Regel-Tabelle

Spalten: ID | Regel (≤20 Wörter) | Fundort | Ladezeitpunkt | Durchsetzung | Tokens (Bytes/4)

### 1.1 CLAUDE.md (`~/.claude/CLAUDE.md`, 7241 Bytes, Stand 2026-09-03)

| ID | Regel | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| R001 | Hauptmodell ist Planer/Prüfer, nicht Arbeiter | CLAUDE.md:3 | immer | Text | 24 |
| R002 | Rollenverteilung dieser Datei gilt nur für die Hauptsession | CLAUDE.md:3 | immer | Text | 16 |
| R003 | Als Subagent ist das Briefing der Auftrag, selbst ausführen | CLAUDE.md:3 | immer | Text | 25 |
| R004 | Hauptmodell ist Fable | CLAUDE.md:3 | immer | Text | 6 |
| R005 | Bei Fable-Limit übernimmt Opus dieselbe Rolle bis Fable wieder da ist | CLAUDE.md:3 | immer | Text | 33 |
| R006 | Bei Fable-Limit: kritisches Coding via Opus-Subagent, Fable-Subagent-Aufgaben an Opus | CLAUDE.md:3 | immer | Text | 36 |
| R007 | PLAN: Aufgabe in Schritte zerlegen, messbare Akzeptanzkriterien aufschreiben | CLAUDE.md:5 | immer | Text | 45 |
| R008 | DELEGIEREN: Arbeitspakete an `executor`/`verifier`, Suchaufgaben an `Explore` | CLAUDE.md:6 | immer | Text | 35 |
| R009 | Eingebauten general-purpose-Agenten nicht mehr für Arbeitspakete nutzen | CLAUDE.md:6 | immer | Text | 20 |
| R010 | `model`-Parameter bei Opus-/Fable-Aufruf explizit mitgeben, sonst gilt Default | CLAUDE.md:6 | immer | Text | 49 |
| R011 | Weiterarbeiten während Subagents laufen, nicht blockierend warten | CLAUDE.md:6 | immer | Text | 18 |
| R012 | Fund-basierte Folgearbeit per SendMessage weiterführen, briefbare an frischen Agent; Weiterführen ist schneller, nicht billiger | CLAUDE.md:6 | immer | Text | 70 |
| R013 | Hauptmodell schreibt selbst keinen Code, auch kritisches Coding geht an Opus-Subagent | CLAUDE.md:6 | immer | Text | 22 |
| R014 | Scheitert Opus an kritischer Kernlogik: Eskalation an Fable-Subagent | CLAUDE.md:6 | immer | Text | 24 |
| R015 | PRÜFEN: Ergebnis mit frischem Blick gegen Akzeptanzkriterien prüfen; erfüllt=fertig | CLAUDE.md:7 | immer | Text | 24 |
| R016 | Nicht erfüllt: konkretes Feedback an Executor, weitere Runde | CLAUDE.md:7 | immer | Text | 20 |
| R017 | Bei langen Arbeitspaketen in Intervallen mitprüfen, nicht erst am Ende | CLAUDE.md:7 | immer | Text | 18 |
| R018 | Mehrdeutiger Auftrag → Skill `grilling` vorschalten vor dem Planen | CLAUDE.md:10 | immer | Text | 18 |
| R019 | Größeres Feature → Skill `to-spec` vor Delegation, Spec wird Briefing | CLAUDE.md:11 | immer | Text | 21 |
| R020 | Code-Arbeitspaket im PRÜFEN-Schritt → Skill `matt-code-review` als Option | CLAUDE.md:12 | immer | Text | 19 |
| R021 | Begriffe des Setups → Pointer auf `~/.claude/CONTEXT.md` | CLAUDE.md:13 | immer | Text | 12 |
| R022 | Nur winzige Aufgaben macht das Hauptmodell direkt selbst | CLAUDE.md:15 | immer | Text | 18 |
| R023 | Alles andere läuft über den Executor, teures Modell bleibt fürs Denken reserviert | CLAUDE.md:15 | immer | Text | 27 |
| R024 | Delegieren bleibt Standard, aber diszipliniert | CLAUDE.md:19 | immer | Text | 13 |
| R025 | So viele Agents wie nötig; kleine Aufgabe = genau einer | CLAUDE.md:20 | immer | Text | 22 |
| R026 | Laufende Agents beobachten, eingreifen bei Kursabweichung/Kontextmangel | CLAUDE.md:21 | immer | Text | 23 |
| R027 | Delegation verbindlich: Subagent-Ergebnisse nicht selbst neu erarbeiten | CLAUDE.md:22 | immer | Text | 23 |
| R028 | Kritische eigene Arbeit (Pläne, Architektur, Specs, lange Läufe) von Fable-Verifier mit frischem Kontext prüfen lassen | CLAUDE.md:23 | immer | Text | 56 |
| R029 | Ein Verifier pro Gegenstand, keine Verifikations-Kaskaden | CLAUDE.md:23 | immer | Text | 15 |
| R030 | Finales Urteil bleibt beim Hauptmodell | CLAUDE.md:23 | immer | Text | 9 |
| R031 | Starke Modelle für mehrdeutige, schwer umkehrbare, schwer prüfbare Entscheidungen | CLAUDE.md:27 | immer | Text | 24 |
| R032 | Günstige Modelle für klar spezifizierte, verifizierbare Aufgaben | CLAUDE.md:27 | immer | Text | 26 |
| R033 | Hauptmodell selbst: Anforderungen, Architektur, Edge-Case-Liste, finales Testurteil — nicht delegieren | CLAUDE.md:31 | immer | Text | 54 |
| R034 | Subagent Fable: Frisch-Kontext-Verifikation kritischer Arbeit; Kernlogik nach gescheiterter Opus-Runde | CLAUDE.md:32 | immer | Text | 45 |
| R035 | Subagent Opus: kritische Kernlogik, architektur-nahe Implementierung, subtiles Debugging, Multi-Datei-Refactoring | CLAUDE.md:33 | immer | Text | 37 |
| R036 | Subagent Sonnet: Default-Executor für Routine-Coding, Stories, Tests, Traceability, Mechanik | CLAUDE.md:34 | immer | Text | 41 |
| R037 | Gilt für alle Agent-Tool-Aufgaben, außer Nutzer sagt im Einzelfall anderes | CLAUDE.md:36 | immer | Text | 26 |
| R038 | Haiku wird derzeit nicht eingesetzt | CLAUDE.md:36 | immer | Text | 9 |
| R039 | Briefing-Regeln gelten für jedes Briefing an executor/verifier, modellunabhängig | CLAUDE.md:40 | immer | Text | 19 |
| R040 | Briefing im ersten Anlauf vollständig: Auftrag, Wozu, Constraints, Akzeptanzkriterien | CLAUDE.md:41 | immer | Text | 32 |
| R041 | Geltungsbereich im Briefing explizit benennen, Executor generalisiert nicht still | CLAUDE.md:42 | immer | Text | 34 |
| R042 | Stil/Output-Form über Positiv-Beispiele steuern, nicht über Verbotslisten | CLAUDE.md:43 | immer | Text | 20 |
| R043 | Versionskritische API-Entscheidungen fürs Briefing vorab selbst per Context7 klären | CLAUDE.md:44 | immer | Text | 27 |
| R044 | Bei Frontend/Design: konkrete visuelle Richtung vorgeben oder 3–4 Richtungen vorschlagen lassen | CLAUDE.md:45 | immer | Text | 31 |
| R045 | Generische AI-Ästhetik (Inter/Roboto, Purple-Gradients, Schema-F) explizit ausschließen | CLAUDE.md:45 | immer | Text | 25 |
| R046 | Arbeitspaket aus Ticket: Briefing nennt die Ticket-ID | CLAUDE.md:46 | immer | Text | 19 |
| R047 | TRACEABILITY.md-Abgleich gegen Code periodisch als eigenes Paket beauftragen | CLAUDE.md:46 | immer | Text | 23 |
| R048 | Scope/Länge/Akzeptanz-Wissen steht in Agent-Definitionen, nicht im Briefing | CLAUDE.md:48 | immer | Text | 33 |
| R049 | Briefing beschränkt sich auf Auftrag, Wozu, Constraints, Akzeptanzkriterien | CLAUDE.md:48 | immer | Text | 22 |
| R050 | Arbeitspaket mit Fundliste als Ergebnis (Review/Audit/Prüfung) → an `verifier` | CLAUDE.md:48 | immer | Text | 34 |
| R051 | Soll Gefundenes auch behoben werden → an `executor` | CLAUDE.md:48 | immer | Text | 15 |
| R052 | Ob zusätzlich Verifier prüft: je Paket entscheiden, bei kritischen Paketen ja | CLAUDE.md:48 | immer | Text | 24 |
| R053 | Eine Session trägt ein Thema | CLAUDE.md:52 | immer | Text | 8 |
| R054 | Themenwechsel durch Nutzer → Hauptmodell schlägt Handoff in frische Session vor | CLAUDE.md:52 | immer | Text | 25 |
| R055 | Je Phase (PLAN/DELEGIEREN/PRÜFEN) mindestens einmal melden, auch während Subagents laufen | CLAUDE.md:54 | immer | Text | 37 |
| R056 | Geschriebene Dokumente: Länge am Bedarf ausrichten, Substanz abdecken und enden | CLAUDE.md:54 | immer | Text | 31 |
| R057 | Ein Paket hat einen Gegenstand; Implementierung, Protokoll und Ingest sind drei Pakete | CLAUDE.md:40 | immer | Text | 22 |
| R058 | Braucht ein Paket ein Dokument, nennt das Briefing Abschnitt oder Zeilen statt Voll-Read | CLAUDE.md:40 | immer | Text | 29 |

**Zeilen ohne Regelinhalt (CLAUDE.md):** 1 (Titel), 2, 4, 8, 9 (reine Überschrift „Pointer an den Entscheidungspunkten:“), 14, 16, 17 (Überschrift), 18, 24, 25 (Überschrift), 26, 28, 29–30 (Tabellenkopf/Trenner), 35, 37, 38 (Überschrift), 39, 47, 49, 50 (Überschrift), 51, 53.

### 1.2 rules/context7.md (`~/.claude/rules/context7.md`, 2397 Bytes, Stand 2026-09-12)

| ID | Regel | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| C001 | Context7 ist für versionskritische Fakten zu Drittanbieter-Code, kein Reflex | context7.md:5 | immer* / Pointer** | Text | 20 |
| C002 | Regel überschreibt explizit die MCP-Server-eigene "use even when..."-Anweisung | context7.md:5 | immer*/Pointer** | Text | 24 |
| C003 | Trigger: Antwort hängt von Version ab (Config-Keys, umbenannte/entfernte APIs, Major-Migration) | context7.md:9 | immer*/Pointer** | Text | 29 |
| C004 | Trigger: Library hatte Major-Release in den letzten 12 Monaten | context7.md:10 | immer*/Pointer** | Text | 35 |
| C005 | Trigger: Library ist Nische/unbekannt, Antwort anders nicht prüfbar | context7.md:11 | immer*/Pointer** | Text | 20 |
| C006 | Trigger: Paket ist lokal nicht installiert, keine Types/Sources lesbar | context7.md:12 | immer*/Pointer** | Text | 20 |
| C007 | Trigger: API-Entscheidung prägt Executor-Briefing, falscher Guess kostet Runde | context7.md:13 | immer*/Pointer** | Text | 22 |
| C008 | Skip: API stabil/bekannt (Standardbibliotheken, Git, SQL, Core-React-Hooks) | context7.md:17 | immer*/Pointer** | Text | 26 |
| C009 | Skip: Paket installiert → erst node_modules/Typdefinitionen lesen (exakte Version) | context7.md:18 | immer*/Pointer** | Text | 36 |
| C010 | Skip: Frage betrifft eigenen Projekt-Code/Business-Logik | context7.md:19 | immer*/Pointer** | Text | 16 |
| C011 | Bei Unsicherheit erst lokalen Code lesen, nur offenen Rest nachschlagen | context7.md:21 | immer*/Pointer** | Text | 19 |
| C012 | Ablauf gilt bei Bezug zu Library/Framework/SDK/API/CLI/Cloud-Service | context7.md:25 | immer*/Pointer** | Text | 32 |
| C013 | Schritt 1: `resolve-library-id` nutzen, außer Nutzer nennt exakte `/org/project`-ID | context7.md:27 | immer*/Pointer** | Text | 33 |
| C014 | Schritt 2: Auswahl nach Namenstreffer, Relevanz, Snippet-Zahl, Reputation, Score | context7.md:28 | immer*/Pointer** | Text | 29 |
| C015 | Bei unpassenden Treffern andere Begriffe probieren; versionsspezifische ID bei Versionsangabe | context7.md:28 | immer*/Pointer** | Text | 30 |
| C016 | Schritt 3: `query-docs` mit gewählter ID, auf ein Konzept skoped, nicht Einzelwörter | context7.md:29 | immer*/Pointer** | Text | 22 |
| C017 | Mehrere Konzepte → getrennte `query-docs`-Aufrufe je Konzept (außer bei Interaktion) | context7.md:29 | immer*/Pointer** | Text | 31 |
| C018 | Schritt 4: Antwort anhand der geholten Doku geben | context7.md:30 | immer*/Pointer** | Text | 8 |

\* gemäß Vorgabe Abschnitt 6a dieses Inventars (rules/\*.md zählt zur „immer geladen“-Summe). \*\* gemäß Wortlaut in CLAUDE.md:44, executor.md:16, verifier.md:30 („Ablauf des Lookups: rules/context7.md“ — liest sich wie Nachschlage-Pointer, nicht wie Dauerlast). Siehe Widerspruch in Abschnitt 3.

**Zeilen ohne Regelinhalt (rules/context7.md):** 1 (Titel), 2, 3 (Überschrift), 4, 6, 7 (reine Einleitung „Run a lookup when…“), 8, 14, 15 (reine Einleitung „Skip the lookup when…“), 16, 20, 22, 23 (Überschrift), 24, 26.

### 1.3 agents/executor.md (`~/.claude/agents/executor.md`, 3647 Bytes, Stand 2026-09-03)

| ID | Regel | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| E001 | Default-Modell Sonnet, sofern beim Aufruf kein `model` gesetzt wird | executor.md:4 | Agent-Lauf | Harness | 25 |
| E002 | `disallowedTools: Agent` — Executor darf keine weiteren Subagents starten | executor.md:5 | Agent-Lauf | Harness | 19 |
| E003 | Briefing ist der Auftrag, selbst ausführen mit eigenen Tools | executor.md:8 | Agent-Lauf | Text | 27 |
| E004 | Rollenverteilung aus CLAUDE.md gilt für Hauptsession; Executor ist der Arbeiter | executor.md:8 | Agent-Lauf | Text | 31 |
| E005 | Briefing nennt Auftrag, Wozu, Constraints, Akzeptanzkriterien | executor.md:10 | Agent-Lauf | Text | 18 |
| E006 | Fehlt ein Teil: mit Vorhandenem arbeiten, Lücke im Bericht nennen | executor.md:10 | Agent-Lauf | Text | 24 |
| E007 | Genau beauftragten Umfang liefern — Einfachstes, das sauber funktioniert, an Systemgrenzen validiert | executor.md:12 | Agent-Lauf | Text | 31 |
| E008 | Auftrag für falsch gehalten/besserer Weg bekannt: in einem Satz sagen, trotzdem wie beauftragt weiterarbeiten | executor.md:12 | Agent-Lauf | Text | 31 |
| E009 | Teil blockiert: alles andere vollständig liefern, Fehlendes/Warum benennen | executor.md:12 | Agent-Lauf | Text | 23 |
| E010 | Mehrdeutiger Auftrag: direkteste Lesart umsetzen, Annahme im Bericht nennen | executor.md:12 | Agent-Lauf | Text | 36 |
| E011 | Frage taucht auf: erst Unabhängiges erledigen, dann Annahme/Frage nennen | executor.md:12 | Agent-Lauf | Text | 34 |
| E012 | Zusätzliche Funde (Bugs, Verbesserungen) als Folgepunkt im Bericht melden | executor.md:12 | Agent-Lauf | Text | 28 |
| E013 | Tests nur wo Auftrag/Repo sie verlangt; Scratch-Checks bleiben Scratch | executor.md:12 | Agent-Lauf | Text | 32 |
| E014 | Geschriebene Dokumente: Länge am Bedarf ausrichten, Substanz abdecken und enden | executor.md:12 | Agent-Lauf | Text | 24 |
| E015 | Gegen Akzeptanzkriterien arbeiten, „fertig“ melden sobald erfüllt | executor.md:12 | Agent-Lauf | Text | 26 |
| E016 | Entschiedenen Schritt ausführen statt ankündigen; Turn endet erst bei erfüllten Kriterien oder fehlender Info | executor.md:12 | Agent-Lauf | Text | 50 |
| E017 | Nach Testlauf: welche Tests, Grün/Rot, Abgleich gegen Akzeptanzkriterien nennen | executor.md:12 | Agent-Lauf | Text | 35 |
| E018 | Ticket-ID im Briefing: als Code-Kommentar eintragen und TRACEABILITY.md aktualisieren | executor.md:12 | Agent-Lauf | Text | 35 |
| E019 | Bei Library/Framework/SDK/API/CLI/Cloud-Bezug aktuelle Doku per Context7 statt Trainingswissen | executor.md:16 | Agent-Lauf | Text | 45 |
| E020 | Ausnahme: Refactoring, Skripte from scratch, Business-Debugging, Code-Review, allg. Konzepte ohne Context7 | executor.md:16 | Agent-Lauf | Text | 37 |
| E021 | Ablauf des Lookups: Pointer auf rules/context7.md | executor.md:16 | Agent-Lauf | Text | 10 |
| E022 | Manche Schritte brauchen Chat-Zustimmung, die der Subagent nicht einholen kann | executor.md:20 | Agent-Lauf | Text | 24 |
| E023 | Solche Schritte an Auftraggeber melden statt ausführen/warten, Rest liefern | executor.md:20 | Agent-Lauf | Text | 44 |
| E024 | Parallele Tool-Calls: unabhängige Anfragen in einer Antwort bündeln | executor.md:24 | Agent-Lauf | Text | 41 |
| E025 | Gezielt betroffene Stellen editieren statt ganze Dateien neu schreiben | executor.md:25 | Agent-Lauf | Text | 20 |
| E026 | Windows: `sed -i` wandelt CRLF→LF; bei CRLF Edit-Tool oder Python `newline=""` nutzen | executor.md:26 | Agent-Lauf | Text | 43 |
| E027 | Bericht auf Deutsch, kriterienweise gegen Akzeptanzkriterien, inkl. Testergebnis/Folgepunkte | executor.md:30 | Agent-Lauf | Text | 34 |
| E028 | Datei je Lauf einmal lesen; nach Edit nur geänderten Bereich mit offset/limit | executor.md:23 | Agent-Lauf | Text | 37 |
| E029 | Dateien über etwa 400 Zeilen nur im benötigten Ausschnitt mit offset/limit lesen | executor.md:23 | Agent-Lauf | Text | 26 |

**Zeilen ohne Regelinhalt (executor.md):** 1, 6 (Frontmatter-Begrenzer `---`), 2 (`name:`), 3 (`description:`), 7, 9, 11, 13, 15, 17, 19, 21, 23, 27, 29 (Leerzeilen), 14 („## Context7“), 18 („## Grenzen“), 22 („## Arbeitsweise“), 28 („## Bericht“) — Überschriften.

### 1.4 agents/verifier.md (`~/.claude/agents/verifier.md`, 2269 Bytes, Stand 2026-09-03)

| ID | Regel | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| V001 | Default-Modell Sonnet, sofern beim Aufruf kein `model` gesetzt wird | verifier.md:4 | Agent-Lauf | Harness | 25 |
| V002 | `disallowedTools: Agent, Edit, Write, NotebookEdit` — Verifier ändert nichts, startet keine Subagents | verifier.md:5 | Agent-Lauf | Harness | 29 |
| V003 | Briefing ist der Auftrag, selbst ausführen mit eigenen Tools | verifier.md:8 | Agent-Lauf | Text | 27 |
| V004 | Rollenverteilung aus CLAUDE.md gilt für Hauptsession; Verifier ist der Prüfer | verifier.md:8 | Agent-Lauf | Text | 31 |
| V005 | Verifikation = mit frischem Kontext gegen Spezifikation/Akzeptanzkriterien aus dem Briefing prüfen | verifier.md:10 | Agent-Lauf | Text | 35 |
| V006 | Ist-Stand selbst nachlesen, statt sich auf Executor-Bericht zu verlassen | verifier.md:10 | Agent-Lauf | Text | 23 |
| V007 | Nur melden was gefunden wird; Reparatur geschieht an anderer Stelle | verifier.md:10 | Agent-Lauf | Text | 19 |
| V008 | Jeden Fund melden, auch unsicher/niedrig-schwer, mit Confidence und Severity | verifier.md:14 | Agent-Lauf | Text | 25 |
| V009 | Filterung/finales Urteil erst im PRÜFEN-Schritt des Hauptmodells; Beitrag ist vollständige Liste | verifier.md:15 | Agent-Lauf | Text | 35 |
| V010 | Berichtsformat auf Deutsch je Fund: Ort, Fund, Beleg, Severity, Confidence | verifier.md:19–24 | Agent-Lauf | Text | 19 |
| V011 | Feld „Ort“: Datei und Zeile, wo möglich | verifier.md:20 | Agent-Lauf | Text | 9 |
| V012 | Feld „Fund“: in einem Satz | verifier.md:21 | Agent-Lauf | Text | 5 |
| V013 | Feld „Beleg“: Fundstelle, Zitat oder Kommandoausgabe | verifier.md:22 | Agent-Lauf | Text | 12 |
| V014 | Feld „Severity“: hoch/mittel/niedrig | verifier.md:23 | Agent-Lauf | Text | 9 |
| V015 | Feld „Confidence“: hoch/mittel/niedrig | verifier.md:24 | Agent-Lauf | Text | 9 |
| V016 | Abschluss-Abgleich Kriterium für Kriterium: erfüllt/nicht erfüllt/unklar | verifier.md:26 | Agent-Lauf | Text | 23 |
| V017 | Keine Funde ist gültiges Ergebnis und wird als solches gemeldet | verifier.md:26 | Agent-Lauf | Text | 18 |
| V018 | Bei Library/Framework/SDK/API/CLI/Cloud-Bezug gegen aktuelle Doku per Context7 statt Trainingswissen prüfen | verifier.md:30 | Agent-Lauf | Text | 55 |
| V019 | Ablauf des Lookups: Pointer auf rules/context7.md | verifier.md:30 | Agent-Lauf | Text | 10 |
| V020 | Manche Schritte brauchen Chat-Zustimmung, die der Subagent nicht einholen kann | verifier.md:34 | Agent-Lauf | Text | 24 |
| V021 | Solche Schritte an Auftraggeber melden statt ausführen/warten, Rest liefern | verifier.md:34 | Agent-Lauf | Text | 44 |
| V022 | Parallele Tool-Calls: unabhängige Anfragen in einer Antwort bündeln | verifier.md:38 | Agent-Lauf | Text | 41 |
| V023 | Datei je Lauf einmal lesen | verifier.md:36 | Agent-Lauf | Text | 9 |
| V024 | Dateien über etwa 400 Zeilen nur im benötigten Ausschnitt mit offset/limit lesen | verifier.md:36 | Agent-Lauf | Text | 26 |

**Zeilen ohne Regelinhalt (verifier.md):** 1, 6 (Frontmatter-Begrenzer), 2 (`name:`), 3 (`description:`), 7, 9, 11, 13, 16, 18, 25, 27, 29, 31, 33, 35, 37, 39 (Leerzeilen), 12 („## Meldepflicht“), 17 („## Berichtsformat“), 28 („## Context7“), 32 („## Grenzen“), 36 („## Arbeitsweise“) — Überschriften.

### 1.5 CONTEXT.md — nur Einträge mit Regelgehalt (Datei 5251 Bytes, nur per Pointer geladen, siehe 6c)

| ID | Regel | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| CTX001 | Pruning: bewusstes Entfernen von Sediment; jede Regel hat genau eine Quelle | CONTEXT.md:70–71 | Pointer | Text | 23 |
| CTX002 | Agent-Definition verliert eingebauten Parallel-Tool-Call-Hinweis; beide Definitionen führen ihn deshalb selbst | CONTEXT.md:57 | Pointer | Text | 32 |
| CTX003 | Repo-Standards (CODING_STANDARDS-Datei) überstimmen die eingebaute Smell-Baseline von matt-code-review | CONTEXT.md:40 | Pointer | Text | 45 |
| CTX004 | Traceability-Datei wird als Teil jedes Ticket-Arbeitspakets aktualisiert | CONTEXT.md:36 | Pointer | Text | 19 |
| CTX005 | Resume-Write: SendMessage-Fortsetzung schreibt meist den gesamten Kontext neu in den Cache, TTL-unabhängig | CONTEXT.md:68 | Pointer | Text | 155 |

Restliche CONTEXT.md-Zeilen sind Glossar (Begriff + „_Avoid_“-Synonymliste) ohne eigenständigen Verhaltens-Regelgehalt und wurden nicht einzeln kodiert.

### 1.6 Hooks (`~/.claude/hooks/*.sh`, aus Code/Kommentaren abgeleitet)

| ID | Regel (abgeleitet) | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| HK01 | Blockiert `git push` (alle Varianten, case-insensitiv) | guard-destructive.sh:56-57 | je Tool-Aufruf | Hook | 38 |
| HK02 | Blockiert `git reset --hard` | guard-destructive.sh:58-59 | je Tool-Aufruf | Hook | 44 |
| HK03 | Blockiert `git clean -f`/`-fd` | guard-destructive.sh:60-61 | je Tool-Aufruf | Hook | 42 |
| HK04 | Blockiert `git branch -D` (case-sensitiv nur bei `-D`, erlaubt `-d`) | guard-destructive.sh:62-63 | je Tool-Aufruf | Hook | 41 |
| HK05 | Blockiert `git branch --force`/`-f` | guard-destructive.sh:64-65 | je Tool-Aufruf | Hook | 45 |
| HK06 | Blockiert `git checkout .` / `git restore .` | guard-destructive.sh:66-67 | je Tool-Aufruf | Hook | 45 |
| HK07 | Blockiert nackten `git stash` (ohne Subkommando) | guard-destructive.sh:68-69 | je Tool-Aufruf | Hook | 52 |
| HK08 | Blockiert `git stash pop` | guard-destructive.sh:70-71 | je Tool-Aufruf | Hook | 52 |
| HK09 | Blockiert `git stash clear` | guard-destructive.sh:72-73 | je Tool-Aufruf | Hook | 48 |
| HK10 | Blockiert `git worktree remove --force`/`-f` | guard-destructive.sh:74-75 | je Tool-Aufruf | Hook | 58 |
| HK11 | Blockiert `rm -r`/`-rf` (rekursives Löschen) | guard-destructive.sh:84-85 | je Tool-Aufruf | Hook | 42 |
| HK12 | Blockiert `Remove-Item -Recurse` inkl. Aliase (ri, rm, rd, rmdir, del, erase) | guard-destructive.sh:86-89 | je Tool-Aufruf | Hook | 46 |
| HK13 | Blockiert `rmdir /s` / `rd /s` / `del /s` | guard-destructive.sh:90-91 | je Tool-Aufruf | Hook | 43 |
| HK14 | Blockiert `find -delete` | guard-destructive.sh:92-93 | je Tool-Aufruf | Hook | 46 |
| HK15 | Blockiert `rimraf <arg>` (nicht `rimraf --help`/bloßes `rimraf`) | guard-destructive.sh:94-97 | je Tool-Aufruf | Hook | 42 |
| HK16 | Blockiert `shutil.rmtree(...)`/`rmtree(...)`-Einzeiler | guard-destructive.sh:98-100 | je Tool-Aufruf | Hook | 44 |
| HK17 | Fehlt `jq`: Befehl sicherheitshalber komplett blockiert (fail-closed) | guard-destructive.sh:8-16 | je Tool-Aufruf | Hook | 54 |
| HK18 | Ausnahme: `git rm` wird vor der rm-Prüfung maskiert (GITRM-Muster) und bleibt erlaubt | guard-destructive.sh:41-43,78-82 | je Tool-Aufruf | Hook | 44 |
| HK19 | Blockiert Agent/Task-Aufruf ohne `subagent_type` oder mit `general-purpose`/`claude`; abschaltbar per `CLAUDE_HOOK_AGENT_GATE=off` | agent-gate.sh:7,23-30 | je Tool-Aufruf | Hook | 82 |
| HK20 | Meldet geänderte Zeilenenden (Index≠Arbeitskopie, abweichend vom Git-Checkout-Ergebnis); strikter Modus per `CLAUDE_HOOK_EOL_STRICT=1` | check-eol.sh:6-11,76-79 | je Tool-Aufruf | Hook | 59 |
| HK21 | post-edit.sh ruft für Edit/Write zusätzlich dieselbe Zeilenenden-Prüfung auf (=HK20, anderer Matcher) | post-edit.sh:15-19 | je Tool-Aufruf | Hook | 35 |
| HK22 | post-edit.sh lässt `eslint --fix` nur für .js/.jsx/.mjs/.cjs unter `konfigurator/src` laufen, blockiert bei Restfehlern | post-edit.sh:32-55 | je Tool-Aufruf | Hook | 42 |
| HK23 | Blockiert Volltext-Read in Junk-Ordnern (node_modules, .git, dist, build, out, coverage, __pycache__, .venv, venv, .next, .nuxt, .cache, .turbo, target, vendor) | read-gate.sh:52-62 | je Tool-Aufruf | Hook | 45 |
| HK24 | Blockiert Volltext-Read von Lockfiles (package-lock.json, yarn.lock, pnpm-lock.yaml, Cargo.lock, poetry.lock, uv.lock, composer.lock, Gemfile.lock) | read-gate.sh:64-71 | je Tool-Aufruf | Hook | 42 |
| HK25 | Blockiert Volltext-Read über 100 KB (Default, änderbar per `CLAUDE_HOOK_READ_MAX_BYTES`) | read-gate.sh:73-90 | je Tool-Aufruf | Hook | 30 |
| HK26 | Ausnahmen: offset/limit>0 immer erlaubt, Bild/PDF/ipynb immer erlaubt, abschaltbar per `CLAUDE_HOOK_READ_GATE=off` | read-gate.sh:8,27-38,46-50 | je Tool-Aufruf | Hook | 36 |

### 1.7 settings.json (`~/.claude/settings.json`, 3714 Bytes, Stand 2026-09-13 11:42)

| ID | Regel | Fundort | Ladezeitpunkt | Durchsetzung | Tokens |
|---|---|---|---|---|---|
| S-ALLOW-01…14 | 14 einzelne Permission-Allow-Einträge (Gmail-Suche/Thread/Message/Drafts, claude-in-chrome/Claude_Browser find/get_page_text/read_page/tabs_context, Context7 resolve/query, obsidian read-note, scheduled-tasks list) | settings.json:4-17 | je Tool-Aufruf | Permission | 7–15 je Eintrag |
| S-DENY-01 | Deny `mcp__claude_ai_Microsoft_365` | settings.json:20 | je Tool-Aufruf | Permission | 7 |
| S-DENY-02 | Deny `mcp__claude_ai_Microsoft_365__authenticate` | settings.json:21 | je Tool-Aufruf | Permission | 11 |
| S-DENY-03 | Deny `mcp__claude_ai_Microsoft_365__complete_authentication` | settings.json:22 | je Tool-Aufruf | Permission | 14 |
| S-DENY-04 | Deny `DesignSync` | settings.json:23 | je Tool-Aufruf | Permission | 3 |
| S-DENY-05 | Deny `CronCreate` | settings.json:24 | je Tool-Aufruf | Permission | 3 |
| S-DENY-06 | Deny `CronDelete` | settings.json:25 | je Tool-Aufruf | Permission | 3 |
| S-DENY-07 | Deny `CronList` | settings.json:26 | je Tool-Aufruf | Permission | 2 |
| S-DENY-08 | Deny `Bash(git push *)` | settings.json:27 | je Tool-Aufruf | Permission | 6 |
| S-DENY-09 | Deny `Bash(gh *)` | settings.json:28 | je Tool-Aufruf | Permission | 4 |
| S-DENY-10 | Deny `mcp__github` (ganzer MCP-Server) | settings.json:29 | je Tool-Aufruf | Permission | 3 |
| S-DENY-11 | Deny `Read(./dist/**)` | settings.json:30 | je Tool-Aufruf | Permission | 4 |
| S-DENY-12 | Deny `Read(./dist-*/**)` | settings.json:31 | je Tool-Aufruf | Permission | 4 |
| S-DENY-13 | Deny `Read(./.wrangler/**)` | settings.json:32 | je Tool-Aufruf | Permission | 5 |
| S-DENY-14 | Deny `Read(./graphify-out/**)` | settings.json:33 | je Tool-Aufruf | Permission | 6 |
| S-DENY-15 | Deny `Read(./**/*.log)` | settings.json:34 | je Tool-Aufruf | Permission | 4 |
| S-DENY-16 | Deny `Read(./**/package-lock.json)` | settings.json:35 | je Tool-Aufruf | Permission | 7 |
| S-DENY-17 | Deny `Read(./**/pnpm-lock.yaml)` | settings.json:36 | je Tool-Aufruf | Permission | 6 |
| S-DENY-18 | Deny `Read(./**/yarn.lock)` | settings.json:37 | je Tool-Aufruf | Permission | 5 |
| S-DENY-19 | Deny `Read(./**/uv.lock)` | settings.json:38 | je Tool-Aufruf | Permission | 5 |
| S-DENY-20 | Deny `Read(./**/poetry.lock)` | settings.json:39 | je Tool-Aufruf | Permission | 6 |
| S-DENY-21 | Deny `Read(./**/Cargo.lock)` | settings.json:40 | je Tool-Aufruf | Permission | 5 |
| S-SKILL-01 | skillOverride `agents-sdk: user-invocable-only` | settings.json:37 | immer (Skill-Sichtbarkeit) | Skill/Harness | 8 |
| S-SKILL-02 | skillOverride `cloudflare: user-invocable-only` | settings.json:38 | immer | Skill/Harness | 8 |
| S-SKILL-03 | skillOverride `cloudflare-email-service: user-invocable-only` | settings.json:39 | immer | Skill/Harness | 12 |
| S-SKILL-04 | skillOverride `cloudflare-one: user-invocable-only` | settings.json:40 | immer | Skill/Harness | 9 |
| S-SKILL-05 | skillOverride `cloudflare-one-migrations: user-invocable-only` | settings.json:41 | immer | Skill/Harness | 12 |
| S-SKILL-06 | skillOverride `durable-objects: user-invocable-only` | settings.json:42 | immer | Skill/Harness | 9 |
| S-SKILL-07 | skillOverride `sandbox-sdk: user-invocable-only` | settings.json:43 | immer | Skill/Harness | 8 |
| S-SKILL-08 | skillOverride `turnstile-spin: user-invocable-only` | settings.json:44 | immer | Skill/Harness | 9 |
| S-SKILL-09 | skillOverride `workers-best-practices: user-invocable-only` | settings.json:45 | immer | Skill/Harness | 11 |
| S-SKILL-10 | skillOverride `wrangler: user-invocable-only` | settings.json:46 | immer | Skill/Harness | 8 |
| S-SKILL-11 | skillOverride `web-perf: user-invocable-only` | settings.json:47 | immer | Skill/Harness | 8 |
| S-FLAG-01 | `disableRemoteControl: true` | settings.json:49 | immer | Harness | 7 |
| S-FLAG-02 | `disableWorkflows: true` | settings.json:50 | immer | Harness | 6 |
| S-FLAG-03 | `disableArtifact: true` | settings.json:51 | immer | Harness | 6 |
| S-OTHER-01 | `model: "fable[1m]"` — Hauptmodell-Zuweisung, Harness-Ebene | settings.json:35 | immer | Harness | 4 |
| S-OTHER-02 | `effortLevel: "xhigh"` | settings.json:76 | immer | Harness | 5 |
| S-OTHER-03 | `autoMemoryEnabled: false` | settings.json:77 | immer | Harness | 6 |
| S-OTHER-04 | `skipWorkflowUsageWarning: true` | settings.json:78 | immer | Harness | 8 |
| S-OTHER-05 | `crossSessionInbound: "refuse"` | settings.json:81 | immer | Harness | 7 |
| S-OTHER-06 | `enabledPlugins`: obsidian@obsidian-skills, diagram-design@diagram-design | settings.json:52-55 | immer (Skill-Sichtbarkeit) | Harness | 20 |
| S-OTHER-07 | `additionalDirectories: C:\GitHub\Projekte` | settings.json:31-33 | je Tool-Aufruf | Permission | 12 |
| S-OTHER-08 | `extraKnownMarketplaces`: claude-plugins-official, obsidian-skills, diagram-design | settings.json:56-75 | immer | Harness | 20 |

---

## 2. Dopplungs-Gruppen

### (a) git-push-Deny — bestätigt, Permission+Hook
- `S-DENY-08` (settings.json:27, `"Bash(git push *)"`) und `HK01` (guard-destructive.sh:56-57, `matchi "${GIT}push\b" && block "git push" "Schreibt in das Remote-Repository."`).
- Unterschied: Permission ist ein reiner String-Match auf `Bash(git push *)` (greift z. B. nicht, wenn `git push` über `bash -c "..."`, `powershell -Command "..."` oder Verkettung `; git push` aufgerufen wird); der Hook erkennt das über `CMDSTART`-Klasse inkl. Quotes/Backticks/Verkettung und ist damit der robustere der beiden Wächter. Doppelte Durchsetzung bestätigt.

### (b) Zeilenende-Regel — bestätigt, Text+Hook
- `E026` (executor.md:26, „`sed -i` in Git Bash wandelt CRLF in LF um. Bei CRLF-Dateien nutzt du das Edit-Tool oder Python mit `newline=\"\"` … nicht mit sed -i.“) und `HK20`/`HK21` (check-eol.sh, Meldungstext: „Bitte auf den Index-Zustand zurücksetzen (z. B. Python mit newline='' oder unix2dos/dos2unix), nicht mit sed -i.“).
- Unterschied: executor.md gibt die Regel als Vorab-Anweisung (Text, vor dem Editieren); der Hook prüft nachträglich (PostToolUse) das tatsächliche Ergebnis und meldet nur bei echter Abweichung. Wortlaut fast identisch („nicht mit sed -i“ wortgleich). Doppelte Durchsetzung bestätigt, aber komplementär (prospektiv vs. retrospektiv).

### (c) general-purpose-Agent — bestätigt, Text+Hook
- `R009` (CLAUDE.md:6, „den eingebauten general-purpose-Agenten nutzt du für Arbeitspakete nicht mehr“) und `HK19` (agent-gate.sh, blockiert `subagent_type` ∈ {leer, general-purpose, claude} mit Exit 2).
- Unterschied: CLAUDE.md richtet sich nur ans Hauptmodell (Empfehlung/Anweisung, keine technische Sperre); der Hook blockiert jeden Aufrufer (auch Subagents) hart auf Tool-Ebene, inklusive dreier Fälle, die CLAUDE.md nicht nennt: leerer `subagent_type` und `claude`. Doppelte Durchsetzung bestätigt, Hook ist strenger/umfassender als der Text.

### (d) Context7 — bestätigt, fünffache Text-Durchsetzung plus MCP-Server-Instruktion
Fundstellen: `R043` (CLAUDE.md:44), `C001`–`C018` (rules/context7.md, ganze Datei), `E019`–`E021` (executor.md:16), `V018`–`V019` (verifier.md:30), Skill `context7-mcp` (Beschreibung: „This skill should be used when the user asks about libraries, frameworks, API references, or needs code examples…“, 265 Bytes Beschreibung + 2420 Bytes Body), und die vom Context7-MCP-Server selbst injizierte Instruktion (~900 Bytes, s. Systemprompt-Abschnitt „MCP Server Instructions“: „Use even when you think you know the answer — your training data may not reflect recent changes. Prefer this over web search for library docs.“).
- Unterschied: `C002` erklärt ausdrücklich, dass rules/context7.md die MCP-Instruktion **overridet** („This rule overrides the server's own … instruction“) — die einzige der sechs Quellen, die den Konflikt benennt. CLAUDE.md/executor.md/verifier.md verweisen nur per Pointer auf rules/context7.md, ohne den Override-Satz zu wiederholen. Der Skill `context7-mcp` dupliziert stattdessen eigenständig ein „Wann-nutzen“-Kriterium („Activates for setup questions, code generation involving libraries…“), das inhaltlich mit C003–C007 überlappt, aber nicht auf rules/context7.md verweist und eigene, leicht andere Trigger nennt. Durchsetzung doppelt: Text (4 Loci) + Skill + MCP-Server-Instruktion, mit einer einzigen expliziten Override-Klausel.

### (e) Parallele Tool-Calls — bestätigt, wortgleiche Textduplikation (dokumentiert/beabsichtigt)
- `E024` (executor.md:24) und `V022` (verifier.md:38): identischer Satz „Parallele Tool-Calls: Liste privat auf, was du als Nächstes brauchst, und fordere alles, was nicht vom Ergebnis eines anderen Calls abhängt, in einer Antwort an.“ — Zeichen für Zeichen gleich in beiden Dateien.
- Unterschied: keiner im Wortlaut. `CTX002` (CONTEXT.md:57) erklärt den Grund: der eingebaute Parallel-Tool-Call-Hinweis geht beim Ersetzen des Subagent-Systemprompts verloren, „den beide Definitionen deshalb selbst führen“ — die Duplikation ist laut CONTEXT.md bewusst, nicht versehentlich. Zusatzfund: auch der komplette „Grenzen“-Absatz ist wortgleich dupliziert (`E022`+`E023` = `V020`+`V021`, exakt derselbe Satz „Deine Sicherheitsregeln verlangen für manche Schritte eine ausdrückliche Zustimmung im Chat…“ in beiden Agent-Definitionen).

### (f) Skill `git-guardrails-claude-code` vs. `guard-destructive.sh` — bestätigt als latentes Risiko, aktuell nicht materialisiert
- Der Skill (SKILL.md, 3757 Bytes) setzt bei Ausführung einen **eigenen** Hook `~/.claude/hooks/block-dangerous-git.sh` auf, der laut Skill-Text dieselben Muster abdeckt wie `guard-destructive.sh`: „git push (all variants including --force)“, „git reset --hard“, „git clean -f / -fd“, „git branch -D“, „git checkout . / git restore .“ (SKILL.md:12-16) — deckungsgleich mit HK01–HK06.
- Unterschied: der Skill würde bei erneuter Ausführung eine **zweite**, unabhängige Skript-Datei plus einen zweiten `PreToolUse`-Eintrag mit `matcher: "Bash"` in settings.json anlegen (SKILL.md:59-97), zusätzlich zu `guard-destructive.sh`, das bereits unter demselben Matcher `Bash|PowerShell` registriert ist. Aktuell existiert `~/.claude/hooks/block-dangerous-git.sh` nicht (Verzeichnislisting zeigt nur die 5 bekannten Skripte) — die Doppelung ist also derzeit **nicht aktiv**, sondern würde erst bei einem erneuten Lauf dieses Skills entstehen (Skill+Hook-Kollision, bestätigt als Risiko, nicht als Ist-Zustand).

### (g) „Ein Verifier pro Gegenstand“ und weitere Mehrfachnennungen in CLAUDE.md — teilweise bestätigt
- Wortlaut „Ein Verifier pro Gegenstand“ selbst kommt in CLAUDE.md nur **einmal** vor (R029, Zeile 23) — als Einzelsatz nicht dupliziert.
- Aber: die Parenthese „(Pläne, Architektur-Entscheidungen, Specs, lange Läufe)“ erscheint **wortgleich zweimal** in CLAUDE.md — einmal in R028 (Zeile 23, Subagent-Disziplin) und einmal in R034 (Zeile 32, Modellwahl-Tabelle „Subagent Fable“).
- Die Opus-scheitert-an-Kernlogik-Eskalation an Fable ist **zweimal** formuliert: R014 (Zeile 6: „scheitert eine Opus-Runde an kritischer Kernlogik, geht die Eskalation an einen Fable-Subagent“) und R034 (Zeile 32: „kritische Kernlogik, an der eine Opus-Runde gescheitert ist“) — inhaltlich identische Routing-Regel, einmal als Fließtext in der Orchestrierungs-Einleitung, einmal als Tabellenzeile.
- Zusatzfund über CLAUDE.md hinaus: „Das finale Urteil bleibt bei dir/beim Hauptmodell“ erscheint dreifach sinngleich — R030 (CLAUDE.md:23), R052 (CLAUDE.md:48, „bei kritischen Paketen tust du es“ als Variante) und CONTEXT.md-Glossareintrag „Verifier“ (Zeile 20: „Das finale Urteil bleibt beim Hauptmodell.“) — Text+Text-Dopplung über zwei Dateien.

### Weitere eigene Funde
- **Traceability-Regel dreifach**: CLAUDE.md R047 (Zeile 46), executor.md E018 (Zeile 12) und CONTEXT.md CTX004 (Zeile 36) fordern alle drei die Pflege der `TRACEABILITY.md`, in drei unterschiedlichen Wortlauten, keiner verweist auf den anderen.
- **„Grenzen“-Absatz** in executor.md (E022/E023) und verifier.md (V020/V021) ist wortgleich (siehe (e)) — bislang nicht in den sieben Kandidaten benannt, aber dieselbe Struktur wie (e).
- **Skill-Override-Liste vs. Skill-Beschreibungstext**: alle 11 skillOverride-Skills (Cloudflare-Familie, web-perf) tragen in ihrer eigenen SKILL.md-Beschreibung bereits einen klaren fachlichen Anwendungsbereich; die `user-invocable-only`-Sperre in settings.json dupliziert keine Regel, sondern schaltet die automatische Modell-Triggerung ab — kein Regel-Duplikat, aber eine Permission+Skill-Interaktion, die den Sinn der ausführlichen Beschreibungstexte (Cloudflare-Skills bis 22 293 Bytes Body, s. Abschnitt 4) für die automatische Triggerung neutralisiert, während die Bytes weiterhin auf Platte liegen (kein Token-Effekt zur Laufzeit, da nicht geladen).

---

## 3. Widersprüche

**(1) Toter Pointer: CLAUDE.md → Skill `to-spec`**
- CLAUDE.md:11 (R019): „Größeres Feature → Skill `to-spec` vor der Delegation; die Spec wird das Briefing.“
- `to-spec/SKILL.md:3`: `disable-model-invocation: true`. Der Skill ist damit für das Modell nicht aufrufbar (bestätigt: `to-spec` fehlt in der Ist-Liste der im Systemprompt sichtbaren Skills, siehe Abschnitt 4). Das Hauptmodell kann die in CLAUDE.md:11 verlangte Aktion nicht selbst ausführen — der Pointer zeigt ins Leere, sofern nicht der Nutzer manuell `/to-spec` aufruft.

**(2) Agent-Typ `claude-code-guide` nur im Hook dokumentiert, nicht in CLAUDE.md**
- `agent-gate.sh:27` nennt als gültiges Ziel „Fragen zu Claude Code an `claude-code-guide`“ (dieser Typ ist von der Sperre ausgenommen).
- CLAUDE.md kennt in seiner DELEGIEREN-Regel (R008/R009) nur `executor`, `verifier`, `Explore`. `claude-code-guide` wird in CLAUDE.md nirgends erwähnt — das Hauptmodell erfährt von diesem vierten zulässigen Agenten-Typ nur, wenn der Hook ihn im Blockade-Fall meldet, nicht aus der eigentlichen Steuerungsdatei.

**(3) rules/context7.md als „immer geladen“ vs. als Pointer-Ziel**
- Abschnitt 6a dieses Inventars zählt `rules/*.md` explizit zur „immer pro Turn geladen“-Summe (Auftrags-Vorgabe).
- Gleichzeitig behandeln CLAUDE.md:44, executor.md:16 und verifier.md:30 rules/context7.md ausdrücklich als Nachschlagewerk-Pointer („Ablauf des Lookups: `C:\Users\szieg\.claude\rules\context7.md`“), und CONTEXT.md definiert „Pointer“ als Gegenteil von dauerhaft geladenem Material. Die Datei kann nicht beides zugleich effizient sein: entweder sie ist Teil des Systemprompts jeder Runde (dann ist ihr Pointer-Charakter irreführend und sie verdoppelt sich mit der MCP-Server-Instruktion aus Gruppe (d) bei jeder Runde), oder sie wird nur bei Bedarf gelesen (dann ist die 6a-Rechnung dieses Inventars zu hoch angesetzt). Welche der beiden Lesarten tatsächlich zutrifft, war aus den gelesenen Quellen nicht abschließend zu klären.

**(4) `autoMemoryEnabled: false` vs. vorhandene, gefüllte Memory-Ordner**
- settings.json:77: `"autoMemoryEnabled": false`.
- Unter `~/.claude/projects/*/memory/` liegen fünf Projekt-Memory-Ordner mit insgesamt 24 Markdown-Dateien (u. a. 136 KB unter `G--Meine-Ablage-Projekte-WlH-Preiskalkulation/memory/`, Details Abschnitt 6d). Ob diese Ordner vor dem Deaktivieren des Flags entstanden sind oder über einen anderen Mechanismus (z. B. Skill `second-brain`, 82 Aufrufe seit 2026-08-14) befüllt werden, war aus den Quellen nicht zu klären — die Koexistenz von „Memory aus“ und aktiv genutzten Memory-Dateien ist als Beobachtung, nicht als geklärter Widerspruch, festgehalten.

**(5) Marketplace-Referenz ohne aktiviertes Plugin**
- settings.json:56-62 registriert die Marketplace `claude-plugins-official` unter `extraKnownMarketplaces`, aber `enabledPlugins` (settings.json:52-55) aktiviert daraus kein einziges Plugin (nur `obsidian@obsidian-skills` und `diagram-design@diagram-design` sind aktiv, beide aus anderen Marketplaces). Die Marketplace-Registrierung liegt vor, ohne dass ein zugehöriges Plugin genutzt wird.

---

## 4. Skill-Tabelle

Legende Herkunft: eigen = `~/.claude/skills/*`; Plugin X = Plugin-Skill aus `~/.claude/plugins/marketplaces/X`; eingebaut = im Systemprompt der Hauptsession gelistet, keine Datei unter `~/.claude` gefunden.

### 4.1 Eigene Skills (45 Ordner unter `~/.claude/skills/`)

| Name | Beschreibung-Bytes | Body-Bytes | Frontmatter-Flags | skillOverrides | Sichtbar? | Aufrufe seit 2026-08-14 (letztes Datum) |
|---|---|---|---|---|---|---|
| agents-sdk | 431 | 11724 | — | user-invocable-only | nein (skillOverride) | 0 |
| ask-matt | 83 | 11365 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| cloudflare | 368 | 8902 | references: [workers, pages, d1, durable-objects, workers-ai] | user-invocable-only | nein (skillOverride) | 0 |
| cloudflare-email-service | 512 | 7390 | — | user-invocable-only | nein (skillOverride) | 0 |
| cloudflare-one | 325 | 21924 | — | user-invocable-only | nein (skillOverride) | 0 |
| cloudflare-one-migrations | 187 | 12121 | — | user-invocable-only | nein (skillOverride) | 0 |
| codebase-design | 265 | 6250 | — | — | ja | 7 (2026-09-09) |
| context7-mcp | 265 | 2420 | — | — | ja | 0 |
| diagnosing-bugs | 156 | 8466 | — | — | ja | 0 |
| domain-modeling | 150 | 3718 | — | — | ja | 11 (2026-09-13) |
| durable-objects | 382 | 5440 | — | user-invocable-only | nein (skillOverride) | 0 |
| git-guardrails-claude-code | 243 | 3458 | — | — | ja | 0 |
| graphify | 357 | 39941 | — | — | ja | 13 (2026-09-12) |
| grill-me | 51 | 44 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| grill-with-docs | 106 | 96 | disable-model-invocation: true | — | nein (Frontmatter) | 2 (2026-09-07) |
| grilling | 152 | 3394 | — | — | ja | 34 (2026-09-13) |
| handoff | 86 | 3909 | disable-model-invocation: true; argument-hint | — | nein (Frontmatter) | 2 (2026-09-12) |
| humanizer | 300 | 30025 | license: MIT; metadata.version | — | ja | 13 (2026-09-13) |
| implement | 62 | 321 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| improve-codebase-architecture | 125 | 5849 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| matt-code-review | 421 | 6214 | — | — | ja | 3 (2026-09-12) |
| migrate-to-shoehorn | 168 | 2696 | — | — | ja | 0 |
| prototype | 179 | 2739 | — | — | ja | 0 |
| research | 226 | 694 | — | — | ja | 10 (2026-09-11) |
| resolving-merge-conflicts | 72 | 805 | — | — | ja | 0 |
| sandbox-sdk | 343 | 5387 | — | user-invocable-only | nein (skillOverride) | 0 |
| scaffold-exercises | 204 | 3443 | — | — | ja | 0 |
| second-brain | 275 | 3722 (2026-09-20) | argument-hint | — | ja | 80 (2026-09-13) |
| setup-matt-pocock-skills | 182 | 6690 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| setup-pre-commit | 238 | 2065 | — | — | ja | 0 |
| skill-inspector | 228 | 9656 | — | — | ja | 5 (2026-09-08) |
| tdd | 149 | 3410 | — | — | ja | 3 (2026-09-12) |
| teach | 61 | 9466 | disable-model-invocation: true; argument-hint | — | nein (Frontmatter) | 0 |
| to-questionnaire | 88 | 2793 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| to-spec | 151 | 2899 | disable-model-invocation: true | — | nein (Frontmatter) | 0 (aber Pointer-Ziel in CLAUDE.md:11, s. Abschnitt 3) |
| to-tickets | 247 | 5458 | disable-model-invocation: true | — | nein (Frontmatter) | 1 (2026-09-07) |
| triage | 136 | 6466 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| turnstile-spin | 418 | 17946 | references: [vanilla-html, nextjs-app, nextjs-pages, astro, sveltekit, hugo] | user-invocable-only | nein (skillOverride) | 0 |
| wait-what | 52 | 279 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| wayfinder | 197 | 11769 | disable-model-invocation: true | — | nein (Frontmatter) | 0 |
| web-perf | 453 | 7707 | — | user-invocable-only | nein (skillOverride) | 0 |
| wizard | 313 | 3984 | — | — | ja | 0 |
| workers-best-practices | 359 | 7039 | — | user-invocable-only | nein (skillOverride) | 0 |
| wrangler | 336 | 20667 | — | user-invocable-only | nein (skillOverride) | 0 |
| writing-for-agents | 103 | 10816 | — | — | ja | 26 (2026-09-13) |

**Summe:** 20 sichtbar, 25 unsichtbar (11 via skillOverride, 14 via `disable-model-invocation: true`) — deckt sich exakt mit der Ist-Liste (20 eigene Skills genannt).

### 4.2 Plugin-Skills

| Name | Herkunft | Beschreibung-Bytes | Body-Bytes | Frontmatter/Command-Flags | Sichtbar? | Aufrufe seit 2026-08-14 |
|---|---|---|---|---|---|---|
| diagram-design | Plugin diagram-design | 748 | ~39 700 (SKILL.md gesamt 40 580 Bytes) | license: MIT; metadata.version 2.6 | ja | 0 |
| doctor | Plugin diagram-design (Command, kein SKILL.md) | 66 | 1094 (prompts/doctor.md) | argument-hint, allowed-tools: Read/Bash/Glob | ja | 0 |
| export-diagram | Plugin diagram-design (Command) | 70 | 1485 (prompts/export-diagram.md) | argument-hint, allowed-tools | ja | 0 |
| import-drawio | Plugin diagram-design (Command) | 89 | — (kein prompts/import-drawio.md gefunden) | argument-hint, allowed-tools | ja | 0 |
| import-mermaid | Plugin diagram-design (Command) | 82 | 1394 (prompts/import-mermaid.md) | argument-hint, allowed-tools | ja | 9 (2026-09-06) |
| profile | Plugin diagram-design (Command) | 77 | 1856 (prompts/profile.md) | argument-hint, allowed-tools | ja | 0 |
| defuddle | Plugin obsidian (obsidian-skills) | 350 | 1164 gesamt | — | ja | 3 (2026-09-05) |
| json-canvas | Plugin obsidian | 226 | 7868 gesamt | — | ja | 0 |
| obsidian-bases | Plugin obsidian | 257 | 13526 gesamt | — | ja | 0 |
| obsidian-cli | Plugin obsidian | 468 | 3289 gesamt | — | ja | 0 |
| obsidian-markdown | Plugin obsidian | 263 | 5563 gesamt | — | ja | 0 |

Installierte Version diagram-design: 2.6.12 (`~/.claude/plugins/installed_plugins.json`), Marketplace-Commit `4451ead…`. obsidian: 1.0.1, Commit `a1dc48e…`.

### 4.3 anthropic-skills (Plugin nicht unter `~/.claude/plugins/` auffindbar)

Rechercheergebnis zur Frage „wo ist anthropic-skills aktiviert“: **nicht ermittelbar aus Dateien unter `~/.claude`.** Geprüft und ohne Treffer: `settings.json` (`enabledPlugins`), `settings.local.json` (Datei existiert nicht), `~/.claude/plugins/installed_plugins.json`, `~/.claude/plugins/known_marketplaces.json`, `~/.claude/plugins/marketplaces/*/.claude-plugin/marketplace.json` (Volltextsuche nach „anthropic-skills“ und nach den elf Skill-Namen ergab keinen Treffer), `~/.claude/plugins/cache/*`. Auch eine Systemsuche nach dem Ordnernamen „anthropic-skills“ über gängige Windows-Installationspfade (AppData/Local, AppData/Roaming, npm-global) blieb ergebnislos. Die elf Skills sind ausschließlich über die Skill-Liste im Systemprompt der aktuellen Hauptsession belegt; ihre Beschreibungstexte wurden aus dieser Systemprompt-Zeile entnommen (keine lokale SKILL.md verfügbar) — Bytes sind daher aus dem Prompt-Text geschätzt, nicht aus einer Datei gemessen.

| Name | Beschreibung-Bytes (aus Systemprompt) | Sichtbar? | Aufrufe seit 2026-08-14 |
|---|---|---|---|
| consolidate-memory | 95 | ja | 0 |
| docx | 1004 | ja | 1 (2026-09-07) |
| explain-usage | 195 | ja | 0 |
| import-memory | 142 | ja | 0 |
| morning | 340 | ja | 0 |
| pdf | 438 | ja | 5 (2026-09-07) |
| pptx | 963 | ja | 1 (2026-09-05) |
| schedule | 208 | ja | 0 |
| setup-claude | 80 | ja | 0 |
| skill-creator | 320 | ja | 0 |
| xlsx | 953 | ja | 1 (2026-09-05) |

### 4.4 Eingebaute Skills (kein Ordner unter `~/.claude`, nur Systemprompt-Listing)

| Name | Beschreibung-Bytes (aus Systemprompt) | Sichtbar? | Aufrufe seit 2026-08-14 |
|---|---|---|---|
| dataviz | 1449 | ja | 0 |
| update-config | 691 | ja | 3 (2026-09-05) |
| keybindings-help | 229 | ja | 0 |
| code-review | 794 | ja | 6 (2026-09-13) |
| simplify | 179 | ja | 0 |
| fewer-permission-prompts | 164 | ja | 1 (2026-09-13) |
| loop | 337 | ja | 0 |
| schedule | 370 | ja | 0 (Namenskollision mit anthropic-skills:schedule — Aufrufzähler in Abschnitt 5 unterscheidet Skill-Aufrufe nicht nach Herkunft, wenn der Name identisch geloggt wird; hier keine Treffer für „schedule“ ohne Präfix gefunden) |
| claude-api | 1079 | ja | 4 (2026-09-05) |
| run | 362 | ja | 0 |
| init | 60 | ja | 0 |
| security-review | 72 | ja | 5 (2026-09-12) |

**Abgleich Sichtbarkeits-Spalte ./. Ist-Liste:** Alle 20 eigenen + 6 diagram-design + 5 obsidian + 11 anthropic-skills + 12 eingebaute = 54 sichtbare Skills stimmen mit der im Auftrag genannten Ist-Liste überein. Keine Abweichung festgestellt.

---

## 5. Hook-Rauschen

Datenbasis: Transkripte unter `~/.claude/projects/**/*.jsonl`, durchsucht mit dem Grep-Tool (nie vollständig gelesen). **Die Datenbasis ist erst zwei Tage alt**: `settings.json.bak-2026-09-12` (Sicherung von 20:15 Uhr) enthält noch **gar keinen** `hooks`-Abschnitt; alle fünf Hooks wurden erst zwischen 2026-09-12 20:15 Uhr und 2026-09-13 11:42 Uhr (aktuelles `settings.json`) scharf geschaltet. Drei Skript-Dateien (`guard-destructive.sh`, `check-eol.sh`, `post-edit.sh`) stammen vom 2026-09-12 Abend, zwei (`agent-gate.sh`, `read-gate.sh`) vom 2026-09-13 Vormittag. Praktisch alle gefundenen Treffer liegen in einer einzigen Entwicklungs-/Testsitzung („…worktrees-hooks-claude-code-67c0b8…“) plus dieser Audit-Sitzung selbst.

| Hook | Meldungsmuster (Grep) | Treffer gesamt (alle Sessions) | Träger-Dateien | Erkennbare Fehlalarme |
|---|---|---|---|---|
| guard-destructive.sh | `Guardrail: Befehl blockiert` | 22 | 7 Dateien, alle 2026-09-12/13 | Ja, siehe unten |
| agent-gate.sh | `Agenten-Schranke:` | 19 | 4 Dateien, alle 2026-09-12/13 | Keine eindeutigen, s. u. |
| check-eol.sh | `Zeilenenden geändert:` | 25 | 8 Dateien, alle 2026-09-12/13 | Keine, ausschließlich Testfixtures (`crlf.txt`, `App.css`, `ordner mit leerzeichen/zwei.txt`) |
| post-edit.sh (ESLint-Teil) | `ESLint meldet Probleme` \| `ESLint-Hook:` | 14 | 6 Dateien, alle 2026-09-12/13 | Keine, ausschließlich Testdateien (`__hooktest__.jsx`, `__verify__.jsx`) |
| read-gate.sh | `Lese-Schranke:` | 23 | 8 Dateien, alle 2026-09-12/13 | Ja, siehe unten |

**Methodische Einschränkung:** Ein erheblicher Teil dieser Rohtreffer ist **kein** Live-Block, sondern eine Text-Erwähnung: der Hauptteil der Treffer in der Entwicklungssitzung stammt daher, dass das Modell dort den eigenen Hook-Quellcode zitiert/liest (Treffer enthält `printf '...Agenten-Schranke:...'` als Codezeile) oder einen Test-/Statusbericht schreibt, der die Meldungstexte wörtlich wiederholt (Beispiel, Datei `d7e98e03…jsonl:177`: „Guardrail: Befehl blockiert - Muster 'git push'\", Befehl lief nicht. Anschließendes `git status --short` lief normal … **Erfüllt.**“ — das ist ein Abschlussbericht, kein Hook-Event). Eine belastbare Trennung Live-Event vs. Text-Zitat war ohne Korrelation über `tool_use_id` (nicht Teil des Auftrags) nicht möglich; die Zahlen in der Tabelle sind Rohtreffer des jeweiligen Musters.

**Konkrete Fehlalarm-Belege:**
- **guard-destructive.sh, `git rm` trotz Ausnahme blockiert:** `d7e98e03-2824-4b3c-aafa-f5eb3925bfdb.jsonl:153`: „Guardrail: Befehl blockiert - Muster \"rm -r\".\nGrun[d]… git rm -r build/ … Guardrail: Befehl blockiert - Muster \"rm -r\".“ — der Befehl `git rm -r build/` ist ein Git-Unterkommando (Dateien bleiben in der Historie, s. HK18-Ausnahme), wurde hier aber laut Transkript trotzdem als „rm -r“ blockiert. Nach heutigem Skriptstand (guard-destructive.sh:41-43,78-82) müsste die GITRM-Maskierung das verhindern; ob dieser Treffer aus einem älteren Skriptstand während der iterativen Testsitzung stammt oder der aktuelle Stand denselben Fall noch reproduziert, ließ sich aus den Transkripten allein nicht klären — es ist der vom Auftrag genannte Beispieltyp „Literal in einem Test-/Statusbefehl“, hier sogar als tatsächlicher Blockierungs-Beleg, nicht nur als Grep-Literal.
- **read-gate.sh, „Junk-Ordner build“ auf echten Projektdateien:** `da46efaa-8c20-4d99-9da4-8ec3e40e8805.jsonl:26` und `4f6b2607-e57b-4cbc-b0f3-56e97c300ee0.jsonl:43` (je 2×): „Lese-Schranke: C:\GitHub\Projekte\wlh-preiskalkulation-app\build\handoff\wlh-handoff-ticket-02-vorbereitet-2026-09-12.md … Grund: Junk-Ordner \"build\"“ bzw. „…\build\spec-ticket-02.md … Grund: Junk-Ordner \"build\"“. Beide Dateien sind Markdown-Handoff-/Spec-Dokumente in einem Projektverzeichnis, das zufällig ein Segment „build“ im Pfad trägt (nicht der klassische generierte Build-Output); der Hook blockiert nach Pfadsegment, nicht nach Dateiinhalt oder -endung, und trifft hier ein legitimes Dokument.
- **read-gate.sh, korrekt ausgelöste Größe-Sperre (kein Fehlalarm):** `…hooks-claude-code-67c0b8\d7e98e03…jsonl:375/378`: „Lese-Schranke: C:\GitHub\Projekte\WlH Preiskalkulation\catalog_raw.json … Grund: Größe 369 KB über 100 KB“ — Größenschwelle greift wie im Skript vorgesehen (HK25); als Gegenbeispiel zur Einordnung mit aufgeführt.
- **agent-gate.sh:** keine Treffer außerhalb der Testsitzung gefunden; alle 19 Treffer sind entweder Quellcode-Zitate (`printf 'Agenten-Schranke:…`) oder gezielte Testaufrufe mit Werten `leer`, `general-purpose`, `claude`, `<wert oder leer>` — dem erwarteten Testmuster der Entwicklungssitzung, keine Fehlalarme gegen reguläre Arbeit erkennbar.
- **check-eol.sh / post-edit.sh:** alle Treffer beziehen sich auf Dateien, deren Namen selbst als Testfixtures erkennbar sind (`crlf.txt`, `App.css` in `%LOCALAPPDATA%\Temp\eoltest`, `__hooktest__.jsx`, `__verify__.jsx` unter `konfigurator/src`) — keine Fehlalarme auf Produktionscode gefunden, aber auch kein Beleg für Live-Einsatz außerhalb der Testsitzung.

---

## 6. Token-Bilanz und Sediment

### 6a. Immer geladen pro Turn (Hauptsession)

| Posten | Bytes | Tokens (÷4) |
|---|---|---|
| CLAUDE.md | 7 241 | 1 810 |
| rules/context7.md | 2 397 | 599 |
| Sichtbare Skill-Beschreibungen — eigene (20) | 4 464 | 1 116 |
| Sichtbare Skill-Beschreibungen — Plugin diagram-design (6) | 1 132 | 283 |
| Sichtbare Skill-Beschreibungen — Plugin obsidian (5) | 1 564 | 391 |
| Sichtbare Skill-Beschreibungen — anthropic-skills (11, geschätzt aus Systemprompt) | 4 738 | 1 185 |
| Sichtbare Skill-Beschreibungen — eingebaut (12, geschätzt aus Systemprompt) | 5 786 | 1 447 |
| MCP-Server-Instruktionen (Context7 ~900 + Gmail ~150 + claude-in-chrome ~900, lt. Auftragsvorgabe) | 1 950 | 488 |
| **Summe „immer geladen“** | **29 272** | **7 318** |

### 6b. Je Agent-Lauf zusätzlich

| Posten | Bytes | Tokens |
|---|---|---|
| agents/executor.md (bei Executor-Lauf) | 3 647 | 912 |
| agents/verifier.md (bei Verifier-Lauf) | 2 269 | 567 |

### 6c. Nur per Pointer (nicht in 6a/6b enthalten)

| Posten | Bytes | Tokens |
|---|---|---|
| CONTEXT.md (Pointer aus CLAUDE.md:13; „Wird nicht automatisch geladen“ laut CONTEXT.md:3) | 5 251 | 1 313 |
| Skill-Bodies, 45 eigene Skills zusammen (nur bei Invocation geladen) | 343 269 | 85 817 |
| Skill-Body diagram-design (Plugin, gesamt inkl. Frontmatter) | 40 580 | 10 145 |
| Skill-Bodies obsidian, 5 Skills zusammen (gesamt inkl. Frontmatter) | 31 410 | 7 853 |

### 6d. Sediment

| Pfad | Größe | Letztes Änderungsdatum |
|---|---|---|
| `~/.claude/CLAUDE.md.bak-2026-08-22` | 6 840 B | 2026-08-22 |
| `~/.claude/CLAUDE.md.bak-2026-09-03` | 8 580 B | 2026-09-03 08:50 |
| `~/.claude/CLAUDE.md.bak-2026-09-03-vor-ap2` | 10 090 B | 2026-09-03 11:32 |
| `~/.claude/CONTEXT.md.bak-2026-09-03` | 3 677 B | 2026-09-03 08:50 |
| `~/.claude/settings.json.bak-2026-09-12` | 2 491 B | 2026-09-12 20:15 |
| `~/.claude/settings.json.bak-2026-09-13` | 3 263 B | 2026-09-13 11:42 |
| `~/.claude/backups/.claude.json.backup.*` (5 Dateien) | je 86 373 B, zusammen 444 KB | 2026-09-13 14:38–14:48 |
| `%LOCALAPPDATA%\Temp\hooktest\` (30 Dateien: JSON-Fixtures, `run-guard.sh`, `register.js`, `*.txt`) | Ordner | 2026-09-12 20:50 |
| `%LOCALAPPDATA%\Temp\hooktest2\` (20 Einträge inkl. Unterordner `build/somefile.txt`, `register-hooks.cjs`) | Ordner | 2026-09-13 11:42 |
| `%LOCALAPPDATA%\Temp\eoltest\` (Git-Repo mit `crlf.txt`, `lf.txt`, `neu.txt`, `ordner mit leerzeichen/zwei.txt`) | Ordner + `.git` | 2026-09-12 20:16 |
| `~/.claude/projects/C--GitHub-Projekte-IIBA-CBAP/memory/` (2 Dateien) | 12 KB | s. Datei-mtimes im Ordner |
| `~/.claude/projects/C--GitHub-Projekte-Plan-Legacy-code-Migration/memory/` (2 Dateien) | 13 KB | — |
| `~/.claude/projects/C--GitHub-Projekte-Pv-Anlage-Konvo/memory/` (6 Dateien) | 36 KB | — |
| `~/.claude/projects/C--GitHub-Projekte-Repo-SA-Analyse/memory/` (2 Dateien) | 5,0 KB | — |
| `~/.claude/projects/G--Meine-Ablage-Projekte-WlH-Preiskalkulation/memory/` (11 Dateien) | 136 KB | — |
| `settings.json` → `extraKnownMarketplaces.claude-plugins-official` | Referenz ohne aktiviertes Plugin (s. Abschnitt 3, Widerspruch 5) | zuletzt aktualisiert 2026-08-19 (laut `known_marketplaces.json`) |

**Nicht als Sediment bestätigt / nicht Teil des Auftragskatalogs, aber am Rand beobachtet:** `.last-update-result.json` zeigt einen fehlgeschlagenen Auto-Update-Versuch (`"outcome":"failed"`, `"error_code":"update_apply_exe_locked"`, 2026-08-21) — nicht explizit als Sediment-Kategorie im Auftrag genannt, hier nur der Vollständigkeit halber notiert, ohne eigene Zeile in der Sediment-Tabelle.

---

## Anhang: Methodik Aufruf-/Treffer-Zählung

- Skill-Aufrufe: Grep-Muster `"name":"Skill","input":\{"skill":"[^"]+"` über `~/.claude/projects`, `-o`, ohne Zeilenlimit; 250 Rohtreffer in 172 Dateien. Datum je Treffer = mtime der Transkriptdatei (Fallback laut Auftrag, da Timestamp-Feld pro Zeile wegen Zeilenlänge nicht zuverlässig mit vertretbarem Aufwand isolierbar war — siehe Testreihe mit gebundenen Regex-Fenstern 150/400/1000 Zeichen, alle drei entweder ohne Treffer oder mit Kappung durch das Tool). Zusätzlich geprüft: Slash-Command-Aufrufe `"text":"/[a-zA-Z][a-zA-Z0-9_-]*` — einziger Treffer war `/konsistenz-radar` (kein Skill dieses Audits), sonst keine zusätzlichen Aufrufe über Nutzer-Slash-Eingaben gefunden.
- Hook-Treffer: je Hook das charakteristische Meldungsmuster aus Abschnitt 5, Grep über `~/.claude/projects`, `output_mode: count` für die Gesamtzahl, `output_mode: content -o` mit Fensterbreite 150–200 Zeichen für die Belegtexte.
- Alle Grep-Aufrufe liefen ausschließlich über das Grep-Tool; Bash wurde für Transkripte nicht verwendet. Literale wie „git push“/„rm -rf“ wurden in eigenen Bash-Schreibkommandos vermieden bzw. über das Write-Tool statt Bash geschrieben, nachdem ein Bash-Versuch mit dem Literal „git push“ in einer Heredoc-Zeile den `guard-destructive.sh`-Hook live auslöste (selbst erlebter Beleg für den in Abschnitt 5 beschriebenen Fehlalarm-Mechanismus: der Hook prüft den rohen Befehlstext, nicht die Absicht).
