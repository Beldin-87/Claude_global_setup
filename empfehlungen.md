# Empfehlungen: Audit des globalen Claude-Code-Setups

_Stand 2026-09-13. Grundlage: `inventar.md` (Regel-IDs R…, C…, E…, V…, CTX…, HK…, S-…), eigene Lektüre aller Hooks, Doku-Recherche (Anhang A) und zwei Messungen (Anhang B). Sprache: Deutsch, technische Begriffe kurz erklärt._

## 1. Kurzfassung

Das Setup ist in guter Verfassung. Die drei Ziele des Audits lassen sich mit überschaubaren Eingriffen erreichen:

1. **Jede Regel genau einmal.** 123 Regeln im immer oder je Agent geladenen Text (56 in CLAUDE.md, 18 in der Context7-Regel, 27 im Executor, 22 im Verifier). Davon werden 10 gestrichen, weil ein Hook, eine andere geladene Datei oder das Modell selbst sie bereits abdeckt; 2 ziehen in einen anderen Satz um, 3 werden umformuliert, 23 gekürzt oder zusammengezogen, 85 bleiben unverändert. Dazu vier kleine Änderungen im Glossar. Die Zieltabelle in Abschnitt 5 nennt jede Regel mit Entscheidung und Begründung.
2. **Tokens.** Der steuerbare Fixbestand pro Turn liegt heute bei rund 7.300 Tokens, davon entfallen 60 Prozent auf Skill-Beschreibungen. Mit den Empfehlungen sinkt er auf rund 4.700 Tokens, mit den optionalen Skill-Entscheidungen auf rund 3.500. Das gilt für jeden Turn der Hauptsession und, weil Subagents dieselben Dateien laden, für jeden Subagent-Turn. Ehrliche Einordnung: Ein Executor startet mit rund 42.500 Tokens Fixkontext, davon sind nur rund 7.700 durch das Setup steuerbar. Die Ersparnis liegt bei 6 bis 9 Prozent je Turn. Der große Hebel bleibt die Sitzungshygiene, die seit August umgesetzt ist.
3. **Sauberes Setup.** Vier Widersprüche (Context7-Regel gegen Agent-Definition, toter Pointer auf `to-spec`, ein Agententyp nur im Hook dokumentiert, Pointer auf eine ohnehin geladene Datei), eine projektspezifische Logik im globalen Hook, ein Fehlalarm der Lese-Schranke und vier Sediment-Gruppen. Alles behebbar.

Nichts davon ist umgesetzt. Umsetzung erst nach Freigabe, Plan in Abschnitt 10, offene Entscheidungen in Abschnitt 11.

## 2. Vorgehen

- Inventar durch einen Sonnet-Executor (`inventar.md`): jede Regel mit Fundort, Ladezeitpunkt, Durchsetzung, Tokens; Skill-Nutzung aus den Transkripten der letzten 30 Tage; Hook-Treffer.
- Harness-Fakten durch den Doku-Agenten `claude-code-guide` (Anhang A).
- Zwei eigene Messungen: ein Executor-Subagent hat seinen Startkontext beschrieben (Anhang B), und die Hooks wurden mit synthetischen Eingaben getestet.
- Bewertung im Hauptmodell nach dem Drei-Ebenen-Zielbild und den Prinzipien aus `writing-for-agents`. Ein Fable-Verifier mit frischem Kontext hat die erste Fassung gegen `inventar.md` und die Originaldateien geprüft; seine 31 Funde (7 mittel, 24 niedrig) sind in dieser Fassung eingearbeitet.

## 3. Leitprinzipien

**Drei Ebenen nach Ladeart** (beschlossen 2026-09-03):

| Ebene | Datei | Wann geladen | Was gehört hinein |
|---|---|---|---|
| 1 | `CLAUDE.md`, `rules/*.md` | jeder Turn, Hauptsession und Subagents | Rollen, PLAN/DELEGIEREN/PRÜFEN, Modellstufen, Briefing-Regeln, Session-Regeln, Pointer |
| 2 | `agents/executor.md`, `agents/verifier.md` | nur beim Lauf des Agenten | Rolle, Briefing-Baustein, Meldepflicht, Arbeitsweise |
| 3 | `CONTEXT.md` | nur per Pointer | Glossar und Begründungen |

**Vokabular aus `writing-for-agents`**, das die Entscheidungen unten trägt:

- **Context Load**: Jede immer geladene Zeile kostet in jedem Turn Tokens und Aufmerksamkeit, ob sie greift oder nicht.
- **No-op**: Eine Anweisung, die das Modell ohnehin befolgt oder die ein Hook technisch erzwingt. Sie zahlt Load, ohne Verhalten zu ändern. Wird ganz gestrichen, nicht gekürzt.
- **Pointer**: Einzeiler, der Material benennt und den Auslöser, wann es zu holen ist. Ein Pointer auf eine Datei, die ohnehin geladen ist, ist ein No-op.
- **Cache**: Text, der wiederholt, was die Umgebung selbst verrät (Tool-Beschreibung, Konfiguration). Nur behalten, wenn die Nachfrage teuer ist.
- **Sediment**: Alte Schichten, die liegen bleiben, weil Löschen riskant wirkt.
- **Positivform**: Das Zielverhalten benennen statt das verbotene. Ein Verbot nur als harte Schranke, gepaart mit dem Ziel.

**Technische Begriffe**, die in den Empfehlungen Entscheidungen tragen:

- **Turn**: Ein Austausch zwischen Modell und Umgebung, also eine Antwort des Modells samt allem, was es dafür geladen bekommt. Jeder Tool-Aufruf startet einen neuen Turn, deshalb zählt alles „immer Geladene“ vielfach.
- **Harness**: Die Claude-Code-Software um das Modell herum. Sie lädt Dateien, führt Hooks aus und setzt Permissions durch.
- **Payload**: Das, was pro Turn an das Modell geschickt wird: Systemprompt, Tool-Beschreibungen, Skill-Liste, Steuerdateien, Gesprächsverlauf.
- **fail-open / fail-closed**: Verhalten eines Hooks, wenn er selbst nicht prüfen kann. Fail-open lässt den Befehl durch, fail-closed blockiert ihn sicherheitshalber.
- **Matcher**: Der Filter in der Hook-Registrierung, der festlegt, bei welchen Tools ein Hook läuft.
- **CRLF / LF**: Zwei Arten, ein Zeilenende zu speichern (Windows-Stil mit zwei Zeichen, Unix-Stil mit einem). Ein Wechsel erzeugt in Git scheinbare Änderungen an jeder Zeile.
- **Regressionsmatrix**: Eine feste Liste von Testfällen mit erwartetem Ergebnis, die nach jeder Änderung erneut gefahren wird.

Ein Grundsatz aus dem Vault gilt weiter: Vor dem Streichen einer Dopplung prüfen, für welchen Leser sie doppelt ist. Die Messungen in Anhang B zeigen, dass Executor und Verifier `CLAUDE.md`, `rules/context7.md` und die komplette Skill-Liste geladen bekommen. Auch die MCP-Server-Anweisungen erreichen sie, allerdings erst mit dem ersten Tool-Ergebnis. Damit ist der Leserkreis für alle Entscheidungen unten klar: Was in Ebene 1 steht, lesen beide.

## 4. Token-Bilanz: Ist und Soll

Alle Zahlen als Bytes geteilt durch 4, also Schätzungen. Quelle Ist: `inventar.md` Abschnitt 6.

| Posten (pro Turn) | Ist Tokens | Soll Tokens | Ersparnis |
|---|---|---|---|
| Skill-Beschreibungen, sichtbar (54 Skills) | 4.420 | 2.340 | 2.080 |
| CLAUDE.md | 1.810 | 1.510 | 300 |
| rules/context7.md | 600 | 400 | 200 |
| MCP-Server-Anweisungen (beide Leser, nicht steuerbar) | 490 | 490 | 0 |
| **Summe je Turn** | **7.320** | **4.740** | **2.580** |
| zusätzlich je Executor-Turn: executor.md | 910 | 780 | 130 |
| zusätzlich je Verifier-Turn: verifier.md | 570 | 480 | 90 |
| optional (Abschnitt 8, Stufe 3): Office-Skills, update-config, simplify, diagram-design | | | bis 1.240 |

Die Ersparnis bei CLAUDE.md ist aus den Inventar-Tokens der gestrichenen und gekürzten Regeln gerechnet (Streichungen 135 Tokens, Kürzungen rund 165 Tokens) und konservativ gerundet.

Zwei Zahlen zur Einordnung. Erstens: Die Messung vom 22.08. (Vault-Seite `claude-code-steering-plan`) ergab 30.000 bis 35.000 Tokens Fixbestand der Hauptsession, die Ersparnis oben sind davon 7 bis 9 Prozent. Zweitens: Der Executor-Probelauf heute kostete 42.564 Tokens ohne einen einzigen Tool-Aufruf. Der Inventar-Executor brauchte 85 Tool-Aufrufe und 307.000 Tokens (Laufstatistik des Agenten). Jede gesparte Zeile zahlt also 85-fach. Deshalb wiegen Skill-Beschreibungen schwerer als ihre Bytes vermuten lassen.

Was keine Tokens spart, obwohl es naheliegt: `@`-Imports in CLAUDE.md laden in jedem Turn wie Inline-Text (Anhang A, Frage 9). `rules/*.md` ohne `paths`-Frontmatter ebenso. Die Aufteilung zwischen CLAUDE.md und `rules/` ist reine Ordnung, kein Token-Hebel.

## 5. Zieltabelle je Regel

Entscheidungen: **bleibt**, **kürzen**, **streichen**, **umzug**, **umformulieren**. Regel-IDs aus `inventar.md`.

### 5.1 CLAUDE.md (Ebene 1)

| ID | Regel (Kurzform) | Entscheidung | Begründung |
|---|---|---|---|
| R001 | Hauptmodell ist Planer und Prüfer | bleibt | Kernregel, beide Leser |
| R002 | Rollenverteilung gilt für die Hauptsession | bleibt | Einzige Stelle, die beide Leser sehen; E004/V004 werden dafür gekürzt |
| R003 | Als Subagent ist das Briefing der Auftrag | streichen | Steht als E003/V003 wortgleich im Body der beiden Agents. Der einzige weitere zulässige Subagent, `claude-code-guide`, hat laut Agentenliste kein Agent-Tool; ob er CLAUDE.md lädt, ist nicht dokumentiert, in beiden Fällen ist R003 dort wirkungslos |
| R004, R005, R006 | Fable ist Hauptmodell; bei Limit Opus; Fable-Pakete an Opus | kürzen auf einen Satz | „Hauptmodell ist Fable; am Fable-Limit übernimmt Opus dieselbe Rolle nach denselben Regeln, bis Fable wieder verfügbar ist, und Fable-Subagent-Pakete gehen dann an Opus.“ Nur der Halbsatz „kritisches Coding läuft dann über Opus-Subagents“ entfällt, R013 gilt ohnehin |
| R007 | PLAN mit Akzeptanzkriterien | bleibt | |
| R008 | DELEGIEREN an executor/verifier/Explore | umformulieren | Nimmt R050/R051 und den vierten Agententyp auf: „Umsetzung an `executor`; Prüfung mit Fundliste (Review, Audit, Abgleich gegen eine Spezifikation) an `verifier`, soll Gefundenes auch behoben werden, an `executor`; reine Suche an `Explore`; Fragen zu Claude Code an `claude-code-guide`.“ Behebt Widerspruch 2 |
| R009 | general-purpose nicht mehr nutzen | streichen | `agent-gate.sh` (HK19) erzwingt es und nennt im Blockadefall die richtigen Ziele. Negation, No-op |
| R010 | `model`-Parameter bei Opus/Fable setzen | kürzen | „Für Opus- und Fable-Pakete setzt du `model` beim Aufruf; ohne Angabe gilt der Sonnet-Default der Definition.“ 49 auf rund 25 Tokens |
| R011 | Weiterarbeiten, während Subagents laufen | bleibt | Harness-Default ist Hintergrundlauf, aber die Regel steuert, was das Hauptmodell währenddessen tut |
| R012 | Folgearbeit per SendMessage | bleibt | Echte Präferenz, kein Default |
| R013 | Hauptmodell schreibt keinen Code | bleibt | Kernregel |
| R014 | Opus scheitert, Eskalation an Fable | streichen | Steht inhaltsgleich in der Tabellenzeile R034 („kritische Kernlogik, an der eine Opus-Runde gescheitert ist“) |
| R015–R017 | PRÜFEN | bleibt | |
| R018 | Mehrdeutig, Skill `grilling` | bleibt | Pointer mit Auslöser, Skill ist modell-aufrufbar |
| R019 | Feature, Skill `to-spec` | umformulieren | Der Skill trägt `disable-model-invocation: true` und setzt einen Issue-Tracker voraus (SKILL.md: „publish it to the project issue tracker“). Neu: „Größeres Feature: dem Nutzer `/to-spec` vorschlagen; die Spec wird das Briefing.“ Behebt Widerspruch 1 |
| R020 | PRÜFEN, `matt-code-review` | bleibt | |
| R021 | Pointer auf CONTEXT.md | bleibt | |
| R022, R023 | Nur Winziges selbst; Rest an Executor | kürzen auf einen Satz | „Nur wirklich winzige Aufgaben erledigst du selbst.“ Die Begründung „teures Modell fürs Denken“ steht im CONTEXT.md-Eintrag Hauptmodell |
| R024 | „Delegieren bleibt Standard, aber diszipliniert“ | streichen | Einleitungssatz ohne Regelgehalt, die Überschrift trägt ihn |
| R025–R027 | Agentenzahl, Beobachten, Verbindlichkeit | bleibt | |
| R028 | Kritische eigene Arbeit an Fable-Verifier | kürzen | Klammerliste „(Pläne, Architektur-Entscheidungen, Specs, lange Läufe)“ entfällt, sie steht in R034 |
| R029, R030 | Ein Verifier pro Gegenstand; finales Urteil | bleibt | |
| R031, R032 | Grundregel Modellwahl | bleibt | |
| R033–R036 | Modelltabelle | kürzen | Tabellenkopf ohne „(Fable; bei Fable-Limit Opus)“ (steht in R005). Zeile Fable ohne „teilt das Kontingent mit der Hauptsession“; dieser Begründungssatz wandert in den CONTEXT.md-Eintrag „Verifier“ (Abschnitt 5.5); „sparsam“ bleibt |
| R037 | Gilt für alle Agent-Aufgaben, außer Nutzer sagt anderes | kürzen | „Gilt für jeden Agent-Aufruf.“ Die zweite Hälfte ist ein No-op: Nutzeranweisungen überstimmen immer |
| R038 | Haiku wird derzeit nicht eingesetzt | bleibt | 9 Tokens, benennt eine revidierbare Entscheidung, die aus der Tabelle allein nicht hervorgeht |
| R039–R042 | Briefing-Regeln: vollständig, Geltungsbereich, Positiv-Beispiele | bleibt | |
| R043 | API-Entscheidungen vorab per Context7 | streichen | Steht als Auslöser C007 in `rules/context7.md`, die in jedem Turn geladen ist |
| R044, R045 | Frontend: Richtung vorgeben, AI-Ästhetik ausschließen | bleibt | R045 ist ein Verbot, aber als Briefing-Inhalt gepaart mit dem Positivziel R044 |
| R046, R047 | Ticket-ID im Briefing; Traceability-Abgleich | bleibt | R047 ist der Auslöser, den nur das Hauptmodell hat |
| R048, R049 | Scope-Wissen in Agent-Definitionen; Briefing beschränkt sich auf vier Teile | kürzen | R040 ist die Untergrenze (alle vier Teile nennen), R049 die Obergrenze (nur diese vier). Beide bleiben, ohne die Liste zweimal zu schreiben: „Das Briefing beschränkt sich auf diese vier Teile; Scope, Länge und Akzeptanz stehen in den Agent-Definitionen.“ |
| R050, R051 | Fundliste an verifier, Beheben an executor | umzug in R008 | Siehe R008 |
| R052 | Zusätzlicher Verifier je Paket entscheiden | bleibt | |
| R053–R056 | Ein Thema je Session; Handoff; Phasen-Meldung; Dokumentlänge | bleibt | R056 gilt der Hauptsession, die Berichte schreibt. E014 im Executor-Body bleibt ebenfalls (Abschnitt 5.3), die Dopplung für den Executor-Leser kostet 24 Tokens und ist bewusst |

Ergebnis: rund 1,1 KB weniger, geschätzt 300 Tokens je Turn, kein Regelverlust.

### 5.2 rules/context7.md (Ebene 1)

| ID | Regel | Entscheidung | Begründung |
|---|---|---|---|
| C001–C011 | Wann nachschlagen, wann nicht, Override der Server-Anweisung | bleibt | Einzige Quelle für die Auslöser. Gilt für beide Leser, Messung Anhang B. C002 ist der einzige Satz im Setup, der den Konflikt mit der Server-Anweisung benennt |
| C012–C018 | Ablauf resolve → query, Auswahlkriterien, ein Konzept je Aufruf | kürzen auf zwei Sätze | Cache: Die Tool-Beschreibungen von `resolve-library-id` und `query-docs` enthalten Reihenfolge, Ausnahme bei expliziter `/org/project`-ID, Auswahlkriterien, Versions-IDs, die Ein-Konzept-Regel und sogar das Schreibweisen-Beispiel „Next.js statt nextjs“ (Anhang B). Sie liegen im Kontext, sobald das Tool per ToolSearch geladen ist, also vor jedem Aufruf. Nicht gedeckt ist nur der Rat, bei unpassenden Treffern umzuformulieren. Bleibt: „Ablauf: `resolve-library-id`, dann `query-docs`; die Tool-Beschreibungen tragen die Auswahlkriterien. Passt kein Treffer, die Frage umformulieren oder einen anderen Namen probieren.“ |

Ergebnis: rund 0,8 KB weniger, geschätzt 200 Tokens je Turn.

### 5.3 agents/executor.md (Ebene 2)

| ID | Regel | Entscheidung | Begründung |
|---|---|---|---|
| E001, E002 | Frontmatter: Sonnet-Default, kein Agent-Tool | bleibt | |
| E003 | Briefing ist Auftrag | bleibt | Einzige Stelle nach Streichung von R003 |
| E004 | Rollenverteilung aus CLAUDE.md gilt für Hauptsession | kürzen | R002 ist im Executor geladen. Bleibt mit eigenem Bezug: „Du bist der Arbeiter der Rollenverteilung aus `~/.claude/CLAUDE.md`.“ |
| E005–E013 | Briefing-Baustein | bleibt | Kern der Ebene 2 |
| E014 | Dokumentlänge am Bedarf | bleibt | Teil des Bausteins „Scope, Länge, Akzeptanz“, auf den E027 und der CONTEXT.md-Eintrag „Briefing-Baustein“ verweisen, und Antwort auf das Leitkriterium „zu lange Executor-Ergebnisse“. Die Dopplung mit R056 für den Executor-Leser (24 Tokens) ist bewusst |
| E015–E018 | Fertig-Meldung, Autonomie, Testbericht, Ticket-ID | bleibt | |
| E019, E020 | Bei Library-Bezug immer Context7; Ausnahmen | streichen | Widerspricht C001/C008 („kein Reflex; stabile, bekannte APIs ohne Lookup“), und beide Texte liegen gleichzeitig im Executor-Kontext. `rules/context7.md` ist die Quelle |
| E021 | Pointer auf rules/context7.md | streichen | Pointer auf eine ohnehin geladene Datei, No-op |
| E022, E023 | Grenzen: keine Chat-Zustimmung möglich | bleibt | Wortgleich in verifier.md, bewusst: Der Body ersetzt den Standard-Subagent-Prompt, und genau dieser Satz fehlte im Probelauf vom 03.09. Dokumentation in CTX002 erweitern |
| E024 | Parallele Tool-Calls | bleibt | Dokumentierte Ausnahme (CTX002) |
| E025 | Gezielt editieren | bleibt | |
| E026 | `sed -i` wandelt CRLF; Edit-Tool oder Python; danach prüfen | umformulieren | Positivform, nur der Begründungssatz entfällt: „CRLF-Dateien änderst du mit dem Edit-Tool oder Python mit `newline=''` und prüfst die Zeilenenden danach.“ Die Selbstprüfung bleibt ungekürzt, weil `check-eol.sh` nur in Git-Repos und dort nur für bereits getrackte Dateien meldet; neue Dateien und alles unter `~/.claude` deckt der Hook nicht |
| E027 | Bericht auf Deutsch, kriterienweise | bleibt | |

Ergebnis: rund 0,5 KB weniger je Executor-Turn.

### 5.4 agents/verifier.md (Ebene 2)

| ID | Regel | Entscheidung | Begründung |
|---|---|---|---|
| V001–V003 | Frontmatter, Briefing ist Auftrag | bleibt | |
| V004 | Rollenverteilung gilt für Hauptsession | kürzen | Wie E004: „Du bist der Prüfer der Rollenverteilung aus `~/.claude/CLAUDE.md`.“ |
| V005–V017 | Verifikation, Meldepflicht, Berichtsformat | bleibt | Kern der Rolle. V009 („finales Urteil beim Hauptmodell“) bleibt trotz R030, weil es hier die Begründung der Meldepflicht ist |
| V018, V019 | Context7 bei Library-Bezug; Pointer | streichen | Wie E019–E021 |
| V020–V022 | Grenzen, parallele Tool-Calls | bleibt | Dokumentierte Ausnahme |

### 5.5 CONTEXT.md (Ebene 3, nur per Pointer)

Kein Token-Druck, aber das Prinzip „eine Quelle je Regel“ gilt auch hier. Vier kleine Änderungen, zwei Einträge bleiben:

| ID / Eintrag | Entscheidung | Begründung |
|---|---|---|
| CTX001 „Pruning“ | bleibt | Einzige Quelle des Grundsatzes „jede Regel hat genau eine Quelle“ |
| CTX002 „Agent-Definition“ | erweitern | Zwei Ergänzungen: Neben den parallelen Tool-Calls auch den Grenzen-Absatz als bewusste Dopplung in beiden Bodies nennen, damit ein späteres Pruning ihn nicht streicht. Und den Satz „die CLAUDE.md-Hierarchie bleibt erhalten“ präzisieren: einschließlich `rules/*.md` und der Skill-Liste, gemessen 2026-09-13. Das ist Umgebungswissen, das keine Datei verrät |
| CTX003 „CODING_STANDARDS-Datei“ | bleibt | Einzige Quelle für den Vorrang der Repo-Standards vor der Baseline von `matt-code-review` |
| CTX004 „Traceability-Datei“ | kürzen | Der Halbsatz „wird als Teil jedes Ticket-Arbeitspakets aktualisiert“ ist die Regel E018. Der Glossareintrag definiert nur |
| Einträge „Executor“, „Verifier“ | kürzen und ergänzen | Die Modellzuordnung in Klammern wiederholt die Tabelle R033–R036; Definition bleibt, Routing steht in CLAUDE.md. In „Verifier“ kommt der Begründungssatz aus R034 hinzu: Fable-Subagents teilen das Kontingent mit der Hauptsession, deshalb sparsam |

## 6. Dopplungen und Widersprüche: Entscheidungen

| Gruppe | Befund | Entscheidung |
|---|---|---|
| (a) git-push-Deny vs. Hook | Hook läuft vor der Permission-Prüfung (Anhang A, Frage 1) und ist bei ungültigem Hook-JSON bewusst fail-open, lässt den Befehl also durch, wenn er ihn nicht lesen kann. Der Deny-Eintrag fängt dann die einfache Form ab | **Behalten als zweite Verteidigungslinie.** Keine doppelte Ausführung: Greift der Hook, wird die Deny-Regel nicht mehr erreicht. Begründung in diesem Repo dokumentieren (README-Abschnitt „Bewusste Dopplungen“, Paket B) |
| (b) Zeilenende-Regel vs. check-eol.sh | Komplementär: Regel wirkt vorher, Hook meldet nachher, und nur innerhalb von Git-Repos | **Regel bleibt, gekürzt (E026).** Anwendungsfall außerhalb von Repos bleibt ungedeckt vom Hook |
| (c) general-purpose-Satz vs. agent-gate.sh | Hook ist strenger und erklärt im Blockadefall die Alternativen | **R009 streichen** |
| (d) Context7 an sechs Stellen | Eine Quelle (`rules/context7.md`) plus fünf Wiederholungen, davon vier mit abweichendem Auslöser „immer bei Library-Bezug“ (executor.md, verifier.md, Skill-Beschreibung, MCP-Server-Anweisung) | **R043, E019–E021, V018–V019 streichen; Skill `context7-mcp` löschen.** Die MCP-Server-Anweisung bleibt technisch und erreicht auch Subagents; C002 überstimmt sie für beide Leser |
| (e) Parallele Tool-Calls und Grenzen in beiden Bodies | Bewusst, weil der Body den Standardprompt ersetzt | **Behalten, in CTX002 vollständig dokumentieren** |
| (f) Skill `git-guardrails-claude-code` | Würde bei Aufruf einen zweiten Hook mit denselben Mustern anlegen; 0 Aufrufe | **Löschen** |
| (g) Mehrfachnennungen in CLAUDE.md | Klammerliste, Eskalationsregel und Vier-Teile-Liste je zweimal | **R014 streichen; R028-Klammer und die Liste in R049 kürzen**, die Obergrenze „nur diese vier Teile“ bleibt (Abschnitt 5.1) |
| Traceability dreifach | R047 (Auslöser für den Abgleich), E018 (Pflege durch den Executor), CTX004 (Definition) | **R047 und E018 sind verschiedene Regeln für verschiedene Leser, bleiben. CTX004 kürzen** |
| Widerspruch 1: Pointer auf `to-spec` | Skill für das Modell nicht aufrufbar | **R019 umformulieren** |
| Widerspruch 2: `claude-code-guide` nur im Hook | CLAUDE.md kennt den Typ nicht | **In R008 aufnehmen** |
| Widerspruch 3: rules als Pointer oder Dauerlast | Gemessen: Dauerlast in beiden Lesern | **Pointer-Sätze streichen (E021, V019), CONTEXT.md-Eintrag „Pointer“ ergänzen** |
| Widerspruch 4: Memory-Ordner trotz Auto-Memory aus | Inertes Archiv aus der Zeit vor dem 12.08., laut Vault so gewollt | **Kein Widerspruch. Sediment, Abschnitt 9** |
| Widerspruch 5: Marketplace ohne Plugin | Kein Token-Effekt | **Belassen**, bis geklärt ist, ob `anthropic-skills` daraus stammt |
| Neu: Skill `context7-mcp` vs. `rules/context7.md` | Skill-Beschreibung sagt „bei jeder Library-Frage“, Regel sagt „kein Reflex“; 0 Aufrufe | **Löschen** (siehe d) |
| Neu: zwei Skills namens `schedule` | Eingebaut und im Plugin `anthropic-skills`, beide 0 Aufrufe | **Plugin-Variante `off`**, eingebaute `user-invocable-only` (Abschnitt 8). Der Sonntags-Task läuft über die Desktop-App und ist nicht betroffen |

## 7. Hooks und settings.json

| Nr. | Fund | Empfehlung |
|---|---|---|
| H1 | `post-edit.sh` ist global registriert, enthält aber ESLint-Logik mit festem Pfad auf `C:/GitHub/Projekte/WlH Preiskalkulation/konfigurator`. Projektlogik auf der globalen Ebene | ESLint-Teil in das WlH-Repo verschieben: `.claude/hooks/eslint-fix.sh` plus Registrierung in der Projekt-`settings.json`. Global `check-eol.sh` direkt unter `Edit\|Write` registrieren und `post-edit.sh` danach löschen. Die Sequenzierung (erst Zeilenenden, dann ESLint) entfällt; mit der heutigen ESLint-Konfiguration des Konfigurators (keine `linebreak-style`-Regel, kein Prettier) ändert ESLint keine Zeilenenden. Kommt Prettier hinzu, muss der Projekt-Hook die Zeilenenden selbst prüfen. Braucht eine eigene Session im WlH-Repo (Themenwechsel), Paket C |
| H2 | `read-gate.sh` blockiert Markdown-Dokumente, wenn ein Pfadsegment `build` heißt (zwei Belege im Inventar, heute reproduziert) | Junk-Ordner-Regel überspringt Dateien mit Endung `.md` und `.txt`. Die Größenregel bleibt und schützt weiter |
| H3 | Matcher `Agent\|Task` in der Registrierung und im Kopfkommentar von `agent-gate.sh` | `Task` ist der alte Toolname (Anhang A, Frage 6). An beiden Stellen auf `Agent` kürzen. Kosmetisch |
| H4 | jq-Auflösungsblock wortgleich in fünf Skripten, nur der Meldungspräfix unterscheidet sich | Optional: gemeinsame `hooks/lib.sh`, die jedes Skript per `source` lädt und den Präfix als Parameter bekommt. Kein Token-Thema, nur Pflegeaufwand |
| H5 | Transkript-Beleg, dass `git rm -r build/` blockiert wurde | Mit dem heutigen Skript nicht reproduzierbar (Test mit zwei Varianten, Exit 0). Stammt aus einer älteren Fassung der Testsitzung. Keine Änderung |
| H6 | Hook-Meldungen als Token-Quelle | Außerhalb der Testsitzung nur der H2-Fall gefunden. Der Literal-Kompromiss des Guardrails (Blockade, sobald `git push` als bloßer Text im Befehl steht, etwa in einem grep-Suchmuster oder in einem mehrzeiligen Textblock) hat den Inventar-Executor einmal getroffen, drei Zeilen. Akzeptabel, bleibt |
| S1 | `Bash(git push *)` und `Bash(gh *)` unter deny | Beide behalten, siehe Gruppe (a). `gh` ist nur hier abgedeckt |
| S2 | `skillOverrides` | Erweitern nach Abschnitt 8 |
| S3 | `extraKnownMarketplaces.claude-plugins-official` ohne aktiviertes Plugin | Belassen, kein Token-Effekt. Erst prüfen, ob `anthropic-skills` daraus stammt (`claude plugin list`) |
| S4 | Hook-Registrierung | Nach H1 und H3 anpassen: vier Skripte statt fünf; `check-eol.sh` bleibt zweimal registriert (Edit\|Write und Bash\|PowerShell), also weiterhin fünf Registrierungen |

Die Guardrail-Regressionsmatrix (`%LOCALAPPDATA%\Temp\hooktest\cases.txt` mit `run-guard.sh`; 128 Fälle laut Vault-Seite `claude-code-hooks`) gehört in dieses Repo unter `hooks/tests/` und wird nach jeder Hook-Änderung gefahren.

## 8. Skills: Entscheidungstabelle

Drei Stufen, gesteuert über den Abschnitt `skillOverrides` in `settings.json`. `user-invocable-only` nimmt die Beschreibung aus dem Payload, also aus dem, was pro Turn an das Modell geht; der Slash-Befehl bleibt tippbar. `off` entfernt beides. Für Plugin-Skills gilt der Schlüssel `plugin:skill`, etwa `anthropic-skills:morning` (Anhang A, Frage 2). Aufrufzahlen: Transkripte seit 2026-08-14, Quelle `inventar.md` Abschnitt 4.

**Stufe 1: Löschen** (Dopplung oder überholt)

| Skill | Beschreibung Bytes | Aufrufe | Grund |
|---|---|---|---|
| git-guardrails-claude-code | 243 | 0 | Durch `guard-destructive.sh` ersetzt, würde zweiten Hook anlegen |
| context7-mcp | 265 | 0 | Widerspricht `rules/context7.md`, Body wiederholt den Lookup-Ablauf |
| grill-me | 51 (unsichtbar) | 0 | Alias auf `grilling`; `grill-with-docs` wird genutzt und bleibt |

**Stufe 2: `user-invocable-only`** (keine oder vereinzelte Aufrufe in 30 Tagen, Beschreibung kostet in jedem Turn)

| Skill | Bytes | Aufrufe | Anmerkung |
|---|---|---|---|
| migrate-to-shoehorn, scaffold-exercises, setup-pre-commit | 610 | 0 | TypeScript-Kurs-Werkzeuge aus dem Pocock-Set |
| wizard | 313 | 0 | Für Einrichtungs-Schritte weiter per `/wizard` erreichbar |
| anthropic-skills: morning, skill-creator, explain-usage | 855 | 0 | `explain-usage` bleibt als `/explain-usage` tippbar |
| eingebaut: dataviz, loop, run, schedule, keybindings-help | 2.747 | 0 | `dataviz` ist mit 1.449 Bytes die größte Beschreibung im Setup. Das eingebaute `schedule` bleibt als Slash-Befehl, die Plugin-Variante geht auf `off` (Stufe 2b) |
| eingebaut: claude-api | 1.079 | 4 | Alle vier Aufrufe am 05.09. in der Session zur CLAUDE.md-Anpassung. Die Beschreibung löst bei jeder Erwähnung von „Claude“ aus, also auch in Sessions wie dieser, ohne dass die API gemeint ist |
| eingebaut: fewer-permission-prompts | 164 | 1 | Ein Aufruf am 13.09. in der Hook-Testsitzung. Einmal-Werkzeug, bleibt als Slash-Befehl |
| diagram-design: doctor, export-diagram, import-drawio, profile | 302 | 0 | `import-mermaid` (9 Aufrufe) und der Hauptskill bleiben sichtbar |
| obsidian: json-canvas, obsidian-bases, obsidian-cli, obsidian-markdown | 1.214 | 0 | Vault-Arbeit läuft über `second-brain` (80 Aufrufe); `defuddle` (3 Aufrufe) bleibt |

Summe Stufe 2: 7.284 Bytes, rund 1.820 Tokens je Turn.

**Stufe 2b: `off`** (Funktion ohne Wirkung im Setup oder doppelt)

| Skill | Bytes | Grund |
|---|---|---|
| anthropic-skills: consolidate-memory, import-memory | 237 | Auto-Memory ist seit 12.08. aus |
| anthropic-skills: setup-claude | 80 | Einmalige Einrichtung, erledigt |
| anthropic-skills: schedule | 208 | Namensgleich mit dem eingebauten Skill, 0 Aufrufe. Der Sonntags-Task läuft über die Desktop-App und ist nicht betroffen |

Summe Stufe 2b: 525 Bytes. Stufe 1, 2 und 2b zusammen: 8.317 Bytes, rund 2.080 Tokens je Turn.

**Stufe 3: Sebastians Entscheidung** (genutzt oder fachlich naheliegend, aber teuer)

| Skill | Bytes | Aufrufe | Abwägung |
|---|---|---|---|
| anthropic-skills: docx, pptx, xlsx, pdf | 3.358 | 1, 1, 1, 5 | Werkzeuge eines Business Analysts. Sichtbar heißt: „mach mir ein Word-Dokument“ löst automatisch aus. `user-invocable-only` heißt: `/docx` tippen, spart 840 Tokens je Turn |
| update-config | 691 | 3 | Nützlich für Settings-Änderungen, die dieses Audit auslöst. Danach `user-invocable-only` |
| simplify | 179 | 0 | Klein, situativ. Bleiben oder `user-invocable-only` |
| diagram-design (Hauptskill) | 748 | 0 direkt | `import-mermaid` nutzt ihn vermutlich intern. Sichtbar lassen, bis das geklärt ist |

**Bleiben sichtbar** (genutzt oder situativ und klein): codebase-design, diagnosing-bugs, domain-modeling, graphify, grilling, humanizer, matt-code-review, prototype, research, resolving-merge-conflicts, second-brain, skill-inspector, tdd, writing-for-agents, defuddle, import-mermaid, code-review, security-review, init.

Alternative zu `user-invocable-only`: Der Wert `name-only` (Anhang A, Frage 2) lässt den Namen in der Liste und nimmt nur die Beschreibung. Ob das Modell den Skill dann noch selbst aufruft, ist nicht dokumentiert. Empfehlung: erst mit einem Skill testen, bevor er breit eingesetzt wird.

## 9. Sediment

| Was | Empfehlung |
|---|---|
| Sechs `.bak`-Dateien im `~/.claude`-Root (CLAUDE.md dreimal, CONTEXT.md, settings.json zweimal) | In dieses Repo nach `archiv/` verschieben. Ab dann gilt: Sicherungen vor Änderungen an `~/.claude` landen im Repo, nicht daneben |
| `~/.claude/backups/.claude.json.backup.*` | Vom Harness verwaltet, nicht anfassen |
| `%LOCALAPPDATA%\Temp\hooktest\` | `cases.txt`, `run-guard.sh` und die JSON-Fixtures in dieses Repo nach `hooks/tests/`; Rest löschen |
| `%LOCALAPPDATA%\Temp\hooktest2\`, `eoltest\` | Löschen. Rekursives Löschen ist für Claude gesperrt, das bleibt bei Sebastian |
| Fünf Memory-Ordner unter `~/.claude/projects/*/memory/` (200 KB) | Werden nicht geladen. Löschen oder nach `archiv/memory/` ins Repo; Entscheidung Sebastian |
| `.last-update-result.json` mit fehlgeschlagenem Update vom 21.08. | Information, keine Aktion |

**Strukturvorschlag**, der die Backup-Frage dauerhaft löst: Dieses Repo hält die Steuerdateien als Quelle (`claude/CLAUDE.md`, `claude/CONTEXT.md`, `claude/rules/`, `claude/agents/`, `claude/hooks/`, `claude/settings.json`), ein PowerShell-Skript `deploy.ps1` kopiert sie nach `~/.claude`, analog zum vorhandenen `powershell/profile.ps1`. Git-Historie ersetzt die `.bak`-Dateien, und jede Änderung hat einen Commit mit Begründung. Entscheidung Sebastian.

## 10. Umsetzungsplan

Erst nach Freigabe. Reihenfolge so, dass jeder Schritt messbar ist.

**Paket A: Textänderungen** (Sonnet-Executor, danach Sonnet-Verifier)
- Sicherung der fünf Dateien nach `archiv/2026-09-13/` in diesem Repo.
- Änderungen an `CLAUDE.md`, `rules/context7.md`, `agents/executor.md`, `agents/verifier.md`, `CONTEXT.md` genau nach Abschnitt 5, CRLF erhalten (Python mit `newline=''`).
- Akzeptanz: Der Verifier weist je Regel-ID nach, dass sie am Zielort steht oder begründet gestrichen ist; keine Regel fehlt, keine ist dazuerfunden; Bytes von CLAUDE.md unter 6.200, von executor.md unter 3.250.

**Paket B: Settings, Hooks, Skills, Repo-Doku** (Sonnet-Executor)
- `settings.json`: `skillOverrides` nach Abschnitt 8; Matcher nach H3.
- `read-gate.sh`: Ausnahme nach H2. Regressionsmatrix nach `hooks/tests/` übernehmen und fahren.
- Skill-Ordner aus Stufe 1 löschen. Die drei Ordner enthalten je eine bis drei Dateien; sie werden Datei für Datei gelöscht, weil rekursives Löschen für Claude gesperrt ist.
- README dieses Repos: Abschnitt „Bewusste Dopplungen“ mit den Gruppen (a), (e) und E014/R056.
- Akzeptanz: 128 Guardrail-Fälle grün; Lese-Schranke lässt `build/x.md` durch und blockiert `build/x.js` weiter; `/context` in einer frischen Session zeigt die Skill-Liste ohne die Stufe-2-Einträge.

**Paket C: ESLint-Hook ins WlH-Repo** (eigene Session, Themenwechsel). Erst dort den Projekt-Hook anlegen, dann global `check-eol.sh` direkt unter `Edit|Write` registrieren und `post-edit.sh` löschen. Bis dahin bleibt `post-edit.sh` in Betrieb, damit das Linting nicht zwischenzeitlich fehlt.

**Paket D: Sediment** (Sebastian löscht, Executor verschiebt ins Repo)

**Messung vorher/nachher**
- `/context` in einer frischen Hauptsession, vorher und nachher.
- Den Probelauf aus Anhang B wiederholen: Executor ohne Tool-Aufruf, Tokenzahl vergleichen (heute 42.564).

## 11. Offene Entscheidungen für Sebastian

1. Stufe 3 der Skill-Tabelle: Office-Skills sichtbar lassen oder per Slash-Befehl?
2. Strukturvorschlag aus Abschnitt 9: Repo als Quelle mit `deploy.ps1`, oder `~/.claude` bleibt die Quelle und das Repo hält nur Archiv und Berichte?
3. Memory-Ordner löschen oder archivieren?
4. `name-only` für Skills testen oder bei `user-invocable-only` bleiben?

## 12. Review gegen das Leitkriterium (Schritt 8 in der Fassung vom 22.08.)

Das Leitkriterium lautete: weniger wiederholte Korrekturen wegen Scope-Überschreitung und zu langer Executor-Ergebnisse. Eine systematische Messung gibt es nicht. Beobachtung aus dieser Session: drei Executor- und Agent-Pakete (Inventar, Probelauf, Doku-Recherche), null Korrekturrunden, alle Akzeptanzkriterien im ersten Anlauf erfüllt; der Inventar-Bericht lang, aber weil das Briefing Vollständigkeit verlangte. Die einzige Korrekturrunde galt der Arbeit des Hauptmodells: Der Fable-Verifier fand 31 Punkte an der ersten Fassung dieses Dokuments, darunter sieben, die bei wörtlicher Umsetzung Regeln verloren oder widersprochen hätten. Die Fable-Verifier-Regel aus dem September hat sich damit zum zweiten Mal bezahlt gemacht. Vorschlag: Das Handoff-Dokument bekommt eine Zeile „Korrekturrunden je Paket“, dann liegen ab der nächsten Session Zahlen vor.

---

## Anhang A: Harness-Fakten (Doku-Agent `claude-code-guide`, 2026-09-13)

| Nr. | Frage | Antwort | Confidence |
|---|---|---|---|
| 1 | Reihenfolge Deny-Regel und PreToolUse-Hook | Hook läuft zuerst. Blockiert er (Exit 2), wird die Permission-Prüfung nicht erreicht. Ein Hook kann eine Deny-Regel nicht aufheben | mittel |
| 2 | `skillOverrides` für Plugin- und eingebaute Skills | Gilt für beide. Plugin-Schlüssel `plugin:skill`. Werte `off`, `user-invocable-only`, `name-only`. Zusätzlich `disableBundledSkills: true` für alle eingebauten auf einmal | hoch |
| 3 | Was laden Custom-Subagents | CLAUDE.md-Hierarchie ja, Git-Status ja. `rules/` laut Doku unklar, Messung Anhang B: ja. Explore und Plan laden weder CLAUDE.md noch Git-Status | hoch / gemessen |
| 4 | Skill-Frontmatter und Sichtbarkeit | `disable-model-invocation: true` nimmt die Beschreibung aus dem Kontext; `user-invocable: false` lässt sie drin. Im Systemprompt steht nur `description` (plus `when_to_use`), zusammen höchstens 1.536 Zeichen | hoch |
| 5 | `rules/*.md` | Ohne `paths`-Frontmatter beim Start vollständig geladen, mit `paths` erst beim Lesen passender Dateien. Gilt für `~/.claude/rules/` und Projekt-`rules/` | hoch |
| 6 | Hook-Matcher | `Task` ist nicht mehr dokumentiert, `Agent` ist der Matcher. `PowerShell` ist gültig. Exit 2 blockiert, Exit 0 mit JSON `permissionDecision` entscheidet, Exit 0 ohne JSON lässt durch | mittel |
| 7 | Deny mit bloßem Toolnamen entfernt Definition | Doku schweigt. Vault-Messung vom 08.08. bestätigt den Effekt; für deferred geladene MCP-Tools ohne Bedeutung | niedrig |
| 8 | Plugin `anthropic-skills` | Gebündelt mit Claude Code, nicht in `enabledPlugins`. Abschalten ganz per `enabledPlugins: {"anthropic-skills": false}`, einzeln per `skillOverrides` (Frage 2) | mittel |
| 9 | `@`-Imports in CLAUDE.md | Werden beim Start vollständig geladen, wie Inline-Text, bis vier Ebenen tief. Kein Lazy-Loading | hoch |

## Anhang B: Messungen dieser Session

**Startkontext eines Executor-Subagents** (Sonnet, Auftrag: „beschreibe deinen Kontext ohne Tool-Aufruf“): 42.564 Tokens. Enthalten: `~/.claude/CLAUDE.md` (zitiert ab „Du bist das stärkste Modell“), `~/.claude/rules/context7.md` (zitiert ab „Context7 is for version-sensitive facts“), 54 Skills mit Beschreibungen, der eigene Agent-Body ab „Du bist Executor“. Vor dem ersten Tool-Aufruf nicht enthalten: MCP-Server-Anweisungen, nur die Namen deferred geladener Tools. Der Fable-Verifier dieser Session hat ergänzt, dass der Block „MCP Server Instructions“ (Context7, claude-in-chrome) mit dem ersten Tool-Ergebnis in seinen Kontext kam. Subagents sehen die Anweisungen also doch, nur später; der Override-Satz C002 gilt damit für beide Leser.

**Hook-Tests mit synthetischer Eingabe** (heutiger Skriptstand):

| Eingabe | Hook | Ergebnis |
|---|---|---|
| `git rm -r --cached build/` | guard-destructive.sh | Exit 0, durchgelassen |
| `git rm -r build/` | guard-destructive.sh | Exit 0, durchgelassen |
| `C:/x/build/spec.md` als Volltext-Read | read-gate.sh | Exit 2, blockiert mit „Junk-Ordner build“ |

**Context7-Tool-Beschreibungen** (per ToolSearch geladen): `resolve-library-id` nennt Auswahlkriterien (Namenstreffer, Relevanz, Snippet-Zahl, Reputation, Benchmark), die Pflicht, es vor `query-docs` aufzurufen, und die Ausnahme bei expliziter `/org/project`-ID. `query-docs` nennt die Ein-Konzept-Regel mit Beispielen. Damit ist Abschnitt „How to look up“ in `rules/context7.md` bis auf das Schreibweisen-Beispiel ein Cache.
