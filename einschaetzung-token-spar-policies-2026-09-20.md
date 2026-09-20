# Einschätzung: Token-Spar-Policies für das Claude-Code-Setup

_Stand 2026-09-20, korrigiert nach Verifier-Prüfung (Fable, frischer Kontext, 21 Funde eingearbeitet). Grundlage: lokale Transkripte der letzten 60 Tage (897 Subagent- und 214 Hauptsession-Läufe, Sessions ab 10.07.2026), Projektinventar (`inventar-projekte-2026-09-20.md`), Doku-Recherche zu Claude Code 2.1.27x. Messskript `%LOCALAPPDATA%\Temp\context_fill_analysis.py`, Report `context_fill_analysis_output.txt` (Lauf 20.09. 11:58, Abschnitte A bis G), beide nicht im Repo. Dieses Dokument ist eine Einschätzung; umgesetzt wird nichts ohne Freigabe._

## 1. Kurzfassung

Die Policy-Liste aus Anhang A des Handoffs setzt am falschen Ende an. Ihre Grundannahme stimmt: Der Verbrauch hängt davon ab, wie viel Kontext ein Agent liest. Aber in diesem Setup ist das per Read-Tool Gelesene zu 80 Prozent Markdown, nicht Code. Code-Dateien machen 6,5 Prozent des Subagent-Kontextinhalts über das Read-Tool aus, dazu kommt ein nicht nach Dateityp erfasster Teil der 10,8 Prozent, die per `cat` und `sed` über Bash gelesen werden; zusammen höchstens rund 12 Prozent. Code-Dateien über 400 Zeilen: 2,4 Prozent beim Read-Tool, bei Bash nicht messbar, als Obergrenze grob das Doppelte. Eine `max-lines`-Regel könnte also im besten Fall unter fünf Prozent des Kontexts berühren, und das nur, wenn kleinere Dateien tatsächlich seltener gelesen würden. Alle sieben Code-Policies der Quelle sind als Token-Maßnahme abzulehnen; ob sie als Wartbarkeitsmaßnahme taugen, steht in Abschnitt 4.

Von den drei „Was mehr spart“-Punkten der Quelle ist einer erledigt (knappe CLAUDE.md), einer durch den bestehenden Hook abgedeckt und als Deny-Regel sogar schädlich (Lesezugriffe sperren), und einer messbar klein (Hook-Ausgaben: 0,2 Prozent des Kontextinhalts; die Hooks laufen aber erst seit dem 12. bis 14.09., auf 60 Tage hochgerechnet wären es rund 1,5 Prozent, mit einem einzelnen ESLint-Ausreißer von 40.000 Zeichen).

Die Messung zeigt stattdessen vier Posten, nach Bestand geordnet. Die Zahlen sind Bestandsanteile, nicht Einsparungen; was eine Maßnahme davon tatsächlich abträgt, zeigt erst die Nachmessung:

1. **Lange Läufe.** 6 Prozent der Subagent-Läufe (Endkontext über 300K Tokens) verursachen 33 Prozent des gesamten Input-Verbrauchs; die 21 Prozent über 200K verursachen 59 Prozent. Paketgröße ist der größte steuerbare Faktor.
2. **Markdown-Dokumente, ganz gelesen.** 37 Prozent des Kontextinhalts sind Read-Ergebnisse von `.md`-Dateien, vor allem Testpläne und Prompt-Dokumente in „Plan Legacy code Migration“ (96 Prozent der Reads dieses Projekts) und die Vault-Dateien `index.md` und `log.md`.
3. **Dateien-Lesen per Bash.** 11 Prozent des Kontextinhalts sind Ausgaben von `cat`, `head`, `sed -n`. Diese Lesezugriffe laufen am `read-gate` vorbei, der nur das Read-Tool prüft; bis zu 865 davon trafen laut Kommandotext Junk-Pfade oder Logdateien.
4. **Wiederholte Reads derselben Datei im selben Lauf.** 14 Prozent der Read-Zeichen, rund 6 Prozent des Kontextinhalts, darin auch nötige Re-Reads nach Edits. `konfigurator.jsx` (heute 406 Zeilen) wurde in 60 Tagen 79 Mal gelesen.

Empfehlung: keine Lint-Policy, sondern drei Textregeln (Paketgröße in CLAUDE.md, Lesedisziplin in den Agent-Definitionen, grep statt Lesen im Second-Brain-Skill) und eine gezielte Deny-Liste für Build-, Cache- und Logpfade, die laut Doku auch Bash-Lesekommandos erfasst. Vorher-nachher-Vergleich per Skript, nicht per `/cost`. Details in Abschnitt 5, Reihenfolge in Abschnitt 7.

## 2. Annahmen zum Auftrag

Der Handoff nannte zwei offene Fragen. Beide Lesarten sind in dieser Einschätzung abgedeckt, deshalb habe ich nicht nachgefragt:

- **Projekte:** alle Projekte mit Subagent-Läufen im Messzeitraum. Code-Policies betreffen nur die drei Code-Projekte `wlh-preiskalkulation-app` (React, Vite, Cloudflare Worker, JavaScript ohne TypeScript), `WlH Preiskalkulation/konfigurator` (React, Vite, JavaScript) und `fantasy-draft-helper` (Python). `kinetic-app` ist Kotlin und außerhalb der Policy-Liste.
- **„Sinnvoll“:** primär Token-Verbrauch, weil die Quelle so argumentiert und der Branch so heißt. Wartbarkeit steht in Abschnitt 4 als eigene Spalte.

Passt eine Annahme nicht, ändert das die Bewertung der Code-Policies (dann zählt die Wartbarkeitsspalte), nicht die Messbefunde.

## 3. Was die Subagent-Kontexte füllt

Alle Anteile beziehen sich auf den Textinhalt der Transkripte (Zeichen ÷ 4 als Token-Näherung, Bilder ausgenommen). Der feste Startkontext (Systemprompt, Tool-Definitionen, CLAUDE.md, Agent-Definition; rund 39K Tokens laut Audit-Messung vom 14.09., Median 27K beim ersten Cache-Write laut Transkripten, die Differenz sind bereits gecachte Anteile) steht nicht in den Transkripten und ist hier nicht enthalten. Hauptsessions haben ein anderes Profil (Tool-Use-Inputs 22 Prozent, User-Text 20 Prozent); der Verbrauch liegt aber bei den Subagents, deshalb der Schwerpunkt.

### 3.1 Kategorien

| Kategorie | Anteil am Inhalt | Davon |
|---|---|---|
| Read-Ergebnisse | 46,2 % | `.md` 37,2 %, Code 6,5 %, sonstige 2,6 % |
| Tool-Use-Inputs (was der Agent schreibt) | 17,7 % | Write 7,8 %, Edit 4,1 %, Bash-Kommandotext 4,1 % |
| Bash/PowerShell-Ausgaben | 17,0 % | Dateien lesen 10,8 %, Suche 2,0 %, git 1,4 %, Tests 0,5 % |
| Assistant-Text und Thinking | 9,9 % | |
| Übrige Tool-Ergebnisse (Grep, Glob, Web, MCP, Edit, Write, Agent) | 5,6 % | Grep, Glob, Web und MCP allein 4,8 % |
| User-Text (Briefings, Folgeaufträge) | 3,6 % | |
| darin: Hook-Rückmeldungen | 0,2 % | Teilmenge der Tool-Ergebnisse; Hooks laufen erst seit 12. bis 14.09., siehe 3.5 |

Zusammen sind 57 Prozent des Kontextinhalts gelesene Dateien (Read plus Bash-Lesen). Code-Dateien über 400 Zeilen: 2,4 Prozent beim Read-Tool. Über 800 Zeilen: 0,9 Prozent. Die per Bash gelesenen Dateien sind nicht nach Typ erfasst; in den drei Code-Projekten sind das 8,4 Millionen Zeichen, plausibel überwiegend Code, im wlh-Projekt mehr als die Code-Reads per Read-Tool (4,2 gegen 3,1 Millionen).

### 3.2 Was gelesen wird

Top-Dateien nach gelesenen Zeichen: sieben der ersten zehn Plätze sind Markdown aus „Plan Legacy code Migration“ (Testpläne von 92 bis 113 KB, Fachmodul-Prompts; 14 bis 41K Zeichen je Read, 15 bis 76 Reads je Datei). Platz 3 ist `konfigurator.jsx` (79 Reads, 980K Zeichen). Platz 5 und 7 sind Vault-`index.md` (55 Reads, 941K Zeichen, also im Schnitt 17K Zeichen je Read; heute 49 KB) und `log.md` (54 Read-Aufrufe, überwiegend mit offset/limit, dazu `cat`-Aufrufe per Bash; heute 209 KB und damit über der Read-Gate-Schwelle).

Wiederholte Reads derselben Datei im selben Lauf: 13,9 Prozent der Read-Zeichen. 74 Prozent aller Reads sind Voll-Reads ohne offset/limit.

Je Projekt:

| Projekt | Läufe | Median Endkontext | Read-Anteil `.md` | Read-Anteil Code | Code aus Dateien über 800 Zeilen | Bash-Anteil „Dateien lesen“ |
|---|---|---|---|---|---|---|
| Plan Legacy code Migration | 310 | 145K | 96 % | 1 % | nicht ausgewiesen | 60 % |
| Pv-Anlage-Konvo | 206 | 139K | nicht ausgewiesen | nicht ausgewiesen | nicht ausgewiesen | nicht ausgewiesen |
| wlh-preiskalkulation-app | 61 | 174K | 27 % | 62 % | 2,9 % | 77 % |
| WlH Preiskalkulation | 77 | 111K | 11 % | 65 % | nicht ausgewiesen | 45 % |
| fantasy-draft-helper | 76 | 132K | 41 % | 51 % | 27,5 % | 72 % |

Pv-Anlage-Konvo ist schreiblastig (Assistant-Text 20 Prozent) und stellt 5 der 55 Läufe über 300K; für die Code-Policy-Frage ohne Belang (ein einzelnes Skript), für die Paketgröße relevant. Im wlh-Projekt ist die größte Code-Datei 1.026 Zeilen lang (`orchestrierung.js`), die meistgelesene 406 (`konfigurator.jsx`). Alle `.md`-Reads des wlh-Projekts zusammen sind 0,8 Prozent des Inhalts; `tickets.md` (95 KB) und `CONTEXT.md` sind keine Treiber. Im Python-Projekt stammen 27,5 Prozent der Code-Read-Zeichen aus Dateien über 800 Zeilen; das sind vor allem Testdateien (`test_empfehlung.py` 2.463 Zeilen) und `empfehlung.py` (1.598).

### 3.3 Bash-Ausgaben

13.485 Aufrufe, Median 688 Zeichen, Maximum 29.393 (das Harness kappt offenbar bei 30.000; die 20 größten Ausgaben liegen alle zwischen 26K und 29K, wie oft die Kappung greift, misst der Report nicht). Nach Klasse: Dateien lesen 63,5 Prozent der Ausgabezeichen (5.322 Aufrufe), Suche 12 Prozent, git 8 Prozent, Tests 2,8 Prozent. Im Bypass-Modus enthält der Systemprompt der Hauptsession die Anweisung, Dateien mit `cat`, `head` oder `sed -n` zu lesen statt mit dem Read-Tool („Do your work through the Bash tool wherever it can accomplish the job: read files with cat, head, or sed -n“); der Verifier-Subagent dieser Session fand die Anweisung in seinem eigenen Prompt nicht, ob Subagents sie erhalten, bleibt also offen. Die 5.322 Aufrufe zeigen das Verhalten unabhängig davon. Bis zu 865 der Lese-Aufrufe per Bash enthielten laut Kommandotext ein Junk-Segment (`node_modules`, `dist`, `build`, `.git`, `graphify-out`, `.wrangler`, `coverage`, `__pycache__`) oder `.log`; das ist ein Substring-Treffer und eine Obergrenze (siehe 3.6). Der `read-gate` prüft nur das Read-Tool und existiert erst seit dem 14.09.; in diesen Tagen sah er 64 solcher Aufrufe.

### 3.4 Lange Läufe

Input-Verbrauch je Lauf ist Kontextgröße mal Turns. Deshalb tragen wenige lange Läufe den Großteil:

| Endkontext | Läufe | Anteil Läufe | Anteil Input-Verbrauch | Anteil Cache-Writes |
|---|---|---|---|---|
| über 150K | 383 | 43 % | 79 % | 69 % |
| über 200K | 192 | 21 % | 59 % | 46 % |
| über 300K | 55 | 6 % | 33 % | 22 % |

Gesamter Input-Verbrauch der Subagents in 60 Tagen: 3,53 Milliarden Tokens, exakt aus den `usage`-Feldern. Von den 55 Läufen über 300K sind 30 Read-dominiert (Markdown, teils mit nur 17 bis 37 Turns); 28 der 55 stammen aus „Plan Legacy code Migration“. Fünf der sieben wlh-Läufe darunter sind Bash-dominiert (47 bis 62 Prozent) mit 84 bis 162 Turns, dazu zwei Läufe des Konfigurator-Projekts (45 und 71 Prozent); der längste dieser 55 Läufe hatte 223 Turns (`fantasy-draft-helper`).

### 3.5 Hooks

Die fünf Hooks existieren erst seit dem 12. bis 14.09. (Vault-Seite `claude-code-hooks`), das Messfenster ist also rund acht Tage, nicht 60. In diesen Tagen: rund 335.000 Zeichen, 0,2 Prozent des Inhalts der 60 Tage; auf 60 Tage hochgerechnet rund 1,5 Prozent. ESLint: 29 Meldungen, Median 921 Zeichen, ein Ausreißer mit 40.036 Zeichen. `post-edit.sh` lintet nur die geänderte Datei; endet ESLint mit Fehlern, geht die volle Ausgabe inklusive Warnungen ungekürzt an Claude. Der Hook prüft den Dateipfad fest gegen `WlH Preiskalkulation/konfigurator/src` und beendet sich sonst; für `wlh-preiskalkulation-app` läuft deshalb kein Lint, unabhängig davon, dass das Projekt auch keine ESLint-Konfiguration hat.

### 3.6 Grenzen der Messung

- Zeichen ÷ 4 ist eine Näherung; deutscher Regeltext lag in der Audit-Messung vom 14.09. bei 2,3 bis 2,8 Zeichen je Token (Vault-Seite `claude-code-setup-audit`), Code liegt darüber.
- Die Kategorienanteile sind Bestandsanteile; die Ersparnis einer Maßnahme ist der Teil davon, der ohne Ersatzlesen entfällt, und wird erst in der Nachmessung sichtbar.
- Die Hook-Zahlen decken nur die Tage seit Einführung der Hooks ab (3.5).
- Inhaltsanteil ist nicht Abrechnungsanteil: Was früh im Lauf in den Kontext kommt, wird in jedem Folge-Turn erneut gelesen. Die Zahlen in 3.4 sind exakt, die Kategorienanteile in 3.1 sind Inhaltsanteile.
- Die Gewichtung des Abo-Meters zwischen Cache-Read und Cache-Write ist undokumentiert (Vault-Seite `claude-code-prompt-cache-messung`).
- Die Junk-Erkennung bei Bash ist ein Substring-Treffer auf dem Kommandotext (`.git` trifft auch `.gitignore`, `.log` auch `console.log`), kein Abgleich des aufgelösten Pfads; die 865 sind eine Obergrenze, die tatsächliche Zahl ist unbekannt. Die 64 Read-Tool-Aufrufe sind dagegen exakte Segmenttreffer; beide Zahlen sind nicht gleichartig.

## 4. Bewertung der zitierten Policies

| Policy (Quelle) | Token-Hebel gemessen | Wartbarkeit | Urteil |
|---|---|---|---|
| Dateigröße begrenzen (`max-lines` 300 bis 400) | Code über 400 Zeilen: 2,4 % des Inhalts beim Read-Tool, bei Bash-Lesen nicht messbar; Obergrenze grob 5 %, realistisch unter 2 % | mittel; die großen Dateien sind Tests und ein Orchestrierungsmodul | **Nein** als Token-Regel. Als Wartbarkeitsregel allenfalls `warn` ab 800 Zeilen, Tests ausgenommen |
| Funktionslänge, Komplexität | nicht messbar, wirkt nur indirekt über Dateigröße | gering bis mittel, Goodhart-Risiko real | **Nein** |
| Duplikate (jscpd) | nicht gemessen; Inventar zeigte Duplikate nur in vendortem Drittcode | einmaliger Lauf billig | **Nein** als Policy; einmaliger Lauf optional |
| Toter Code (knip, vulture) | nicht messbar | einmaliger Lauf billig | **Nein** als Policy; einmaliger Lauf optional |
| Typprüfung (tsc, mypy) | keiner messbar; beide JS-Projekte ohne TypeScript | tsc: hoch, aber eine Migration. mypy: `fantasy-draft-helper` ist bereits breit annotiert, mypy wäre ein kleiner Schritt | **Nein** als Token-Maßnahme. mypy optional aus Wartbarkeitsgründen; tsc wäre eine Projektentscheidung |
| Architekturgrenzen (dependency-cruiser, import-linter) | nicht messbar | für 180 Dateien überdimensioniert | **Nein** |
| Formatter (Prettier, Ruff format) | keiner, wie die Quelle selbst sagt | ja, billig; das wlh-Projekt hat nicht einmal ESLint | **Optional**, nur aus Wartbarkeitsgründen |
| Lesezugriffe sperren (`permissions.deny`) | Deny-Regeln gelten laut Doku auch für Grep, Glob und für die Bash-Lesekommandos `cat`, `head`, `tail`, `sed` sowie Redirects; damit erfassen sie die Bash-Lücke, die der Hook offen lässt. Für `node_modules` kollidiert die Grep-Wirkung mit der Context7-Regel „Typdefinitionen in `node_modules` lesen“ | keine | **Teilweise ja**: Deny für `dist*`, `.wrangler`, `graphify-out`, Logs und Lockfiles; nicht für `node_modules`. Details 5.4 |
| Knappe CLAUDE.md | erledigt (Audit 13.09., Pakete A, B, D) | keine | **Erledigt** |
| Hook-Ausgaben kurz halten | 0,2 % des Inhalts; ein 40K-Ausreißer | keine | **Richtig, aber kein Hebel.** Beim offenen Paket C mitnehmen (`--quiet`, `head -30`) |
| Risiken-Abschnitt der Quelle | stimmig | | Bestätigt. `/cost` und `/usage` zeigen Sitzungs- und Kontingentwerte ohne Aufschlüsselung je Aufgabe und Projekt; das Skript liefert diese |

Zur Sprache: Für JavaScript und Python fällt das Urteil gleich aus. Der einzige Unterschied ist `fantasy-draft-helper`, wo Dateien über 800 Zeilen 27,5 Prozent der Code-Reads tragen. Auch dort bleibt der Anteil am Gesamtkontext des Projekts einstellig, weil Code nur die Hälfte der Reads und Reads nur rund die Hälfte des Inhalts sind.

## 5. Vorschläge, priorisiert nach gemessenem Hebel

Die Reihenfolge in diesem Abschnitt folgt dem gemessenen Bestand. Die Ersparnis je Maßnahme ist kleiner als der Bestand und erst in der Nachmessung sichtbar; wo sie sich abschätzen lässt, steht es dabei.

### 5.1 Paketgröße als Briefing-Regel (Bestand: Läufe über 200K tragen 59 Prozent des Input-Verbrauchs)

Eine Zeile in den Briefing-Regeln der `CLAUDE.md`: Ein Paket hat einen Gegenstand; Implementierung, Protokoll und Ingest sind drei Pakete. Braucht ein Paket ein Dokument, nennt das Briefing Abschnitt oder Zeilen. Gehört in die CLAUDE.md, weil nur die Hauptsession das Paket schneidet. Messbar über den Anteil der Läufe über 200K (heute 21 Prozent) und deren Anteil am Input-Verbrauch (59 Prozent).

Was das Teilen einspart: Der Input-Verbrauch eines Laufs wächst mit Kontext mal Turns. Zwei halb so lange Läufe kosten rechnerisch die Hälfte des Verbrauchs eines langen, abzüglich eines zweiten Startkontexts und der Dokumente, die das zweite Paket erneut lädt. Die Arbeit selbst verschwindet nicht. Gelingt die Teilung bei der Hälfte der Läufe über 200K, liegt die Ersparnis grob bei einem Zehntel des Gesamtverbrauchs.

Ehrlich dazu: Der Median-Endkontext liegt bei 137K. Ein Ziel „unter 150K“ (Handoff Vorschlag 2) würde die Hälfte aller Läufe betreffen und ist als Regel nicht haltbar. Realistisch ist, den Anteil über 200K zu halbieren.

Nicht empfohlen ohne Test: `autoCompactWindow` auf 300k senken. Das Setting existiert, ob es für Subagents gilt, ist nicht dokumentiert, und eine Kompaktierung mitten im Paket kann das Briefing verlieren.

### 5.2 Dokumente nicht ganz lesen (Bestand: 37 Prozent des Inhalts sind `.md`-Reads)

Die Ersparnis ist der Teil, der durch Abschnitts- statt Volltext-Reads entfällt; in „Plan Legacy code Migration“ kostet ein Read heute 14 bis 41K Zeichen, ein Abschnitt wäre ein Bruchteil davon. Drei Stellen:

- **Second-Brain-Skill:** Das Grundwissen und Operation 1 verlangen, `index.md` zu lesen; die grep-Einschränkung steht nur in Operation 2. Gemessen: 55 Reads mit zusammen 941K Zeichen, im Schnitt 17K je Read; welcher Anteil davon auf Ingest-Läufe entfällt, weist der Report nicht aus. Bei heute 49 KB kostet ein Voll-Read rund 12K Tokens. Ändern zu: Projektabschnitt per grep, Katalogeintrag per Edit anfügen. `log.md` nie lesen: Format aus `tail -3`, Eintrag per Append. Gilt für den Handoff-Ingest-Executor ebenso.
- **Briefings:** Wenn ein Paket ein Dokument braucht, nennt das Briefing Abschnitt oder Zeilen oder zitiert den Ausschnitt. Ergänzung der Briefing-Regel „vollständig im ersten Anlauf“: vollständig heißt nicht, das ganze Dokument lesen zu lassen.
- **Plan Legacy code Migration:** größter Einzelverbraucher der 60 Tage (310 Läufe, 96 Prozent der Reads Markdown, 28 der 55 Läufe über 300K). Falls das Projekt weiterläuft: Testpläne je Lauf statt je Datum, Prompt-Dokumente aufteilen. Falls nicht: nichts tun.

Kein Hebel, anders als im Handoff vermutet: `tickets.md` und `CONTEXT.md` im wlh-Projekt. Alle `.md`-Reads dieses Projekts zusammen sind 0,8 Prozent des Inhalts; `tickets.md` wird in Hauptsessions mit offset/limit gelesen. Eine Datei je Ticket wäre Ordnung, keine Token-Maßnahme.

### 5.3 Lesedisziplin in den Agent-Definitionen (Bestand: wiederholte Reads sind 6,4 Prozent des Inhalts, darin nötige Re-Reads nach Edits)

Zwei Sätze in `executor.md` und `verifier.md`: Eine Datei wird je Lauf einmal gelesen; nach einem Edit wird nicht erneut gelesen, bei Bedarf nur der geänderte Bereich mit offset/limit. Dateien über etwa 400 Zeilen werden mit offset/limit in dem Ausschnitt gelesen, den die Aufgabe braucht. Ersparnis grob die Hälfte des Bestands, weil ein Teil der Wiederholungen nach Edits nötig bleibt. Messbar über den Anteil wiederholter Reads (heute 13,9 Prozent der Read-Zeichen) und den Voll-Read-Anteil (heute 74 Prozent).

### 5.4 Deny-Liste für Build-, Cache- und Logpfade (Bestand: klein, geschätzt 1 bis 2 Prozent; die Lücke ist aber systematisch)

Der `read-gate` prüft nur das Read-Tool. 5.322 Lese-Aufrufe per Bash in 60 Tagen laufen daran vorbei, bis zu 865 davon auf Junk- oder Log-Pfade. Laut Permissions-Doku gelten Read-Deny-Regeln auch für die Bash-Kommandos `cat`, `head`, `tail`, `sed`, `tee` und für Redirects, nicht aber für Grep-Rekursion ohne Dateinamen oder für Skripte, die Dateien selbst öffnen. Eine gezielte Deny-Liste schließt die Lücke deshalb ohne neuen Hook:

- `Read(./dist/**)`, `Read(./dist-*/**)`, `Read(./.wrangler/**)`, `Read(./graphify-out/**)`, `Read(./**/*.log)`, dazu die Lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `uv.lock` und so weiter). Syntax und Ablage über den Skill `update-config`; `./`-Muster gelten relativ zum jeweiligen Projekt, auch aus der globalen `settings.json`.
- **Nicht** `node_modules`: Deny wirkt auch auf Grep und Glob, und die Context7-Regel verlangt, Typdefinitionen dort zu lesen. Für `node_modules` bleibt der Hook das richtige Werkzeug, weil er nur Voll-Reads blockiert und offset/limit sowie Grep zulässt.
- Nebenwirkung: Grep in `dist` wird ebenfalls verweigert. Das Leak-Check-Skript des wlh-Projekts läuft als Node-Prozess und ist nicht betroffen; ein Agent, der Bundle-Inhalte prüfen will, bekommt eine Ablehnung mit Hinweis.
- Abnahme: nach dem Setzen im Bypass-Modus `cat` auf eine `.log`-Datei und ein Read auf `dist/` probieren. Ob Deny-Regeln im Bypass-Modus greifen, sagt die Doku nicht ausdrücklich; das Setup verlässt sich beim `git push`-Deny bereits darauf.

Der `read-gate` selbst bleibt, wie er ist. Eine Erweiterung seiner `JUNK_DIRS` um `.wrangler` und `graphify-out` träfe nur das Read-Tool und wegen der `.md`-Ausnahme nicht einmal `graphify-out/GRAPH_REPORT.md`; gegenüber der Deny-Liste ist sie überflüssig. Ein eigener Bash-Lese-Hook ebenfalls.

Nicht empfohlen: `bashOutputMaxChars` senken. Wie oft die 30K-Kappung heute greift, misst der Report nicht; die 20 größten Ausgaben liegen alle knapp darunter. Eine niedrigere Kappung schneidet mehr ab und erzeugt Wiederholungsläufe, ohne dass die Ersparnis bekannt wäre.

### 5.5 Große Writes (7,8 Prozent des Inhalts, davon 74 Prozent aus Writes über 10K Zeichen)

Zweit-Writes derselben Datei sind selten (37 Fälle in 60 Tagen). Die großen Writes sind also meist Erstfassungen: Reports, Skripte, Dokumente. Das ist legitime Arbeit; die Regel „Länge am Bedarf“ steht bereits in CLAUDE.md und Executor-Definition. Kein neuer Vorschlag, nur die Erinnerung, dass Briefings die Zielform benennen (Tabelle statt Fließtext, Umfang).

### 5.6 `omitClaudeMd` für Executor und Verifier: nicht setzen

Das Frontmatter-Feld existiert seit 2.1.271, überspringt aber die gesamte CLAUDE.md-Hierarchie einschließlich der Projekt-CLAUDE.md. Die wlh-`CLAUDE.md` trägt die fachlichen Projektregeln (Preisdaten nie committen, Tech-Stack-Entscheidungen), die ein Executor braucht. Ersparnis wären 2 bis 5K Tokens je Subagent-Start (globale CLAUDE.md 6,2 KB, dazu im wlh-Projekt dessen CLAUDE.md mit 10,2 KB) bei einem Startkontext von rund 39K. Das Verhältnis stimmt nicht. Handoff Vorschlag 3: nein.

### 5.7 `AGENTS.md` im wlh-Projekt: lassen

Die Datei ist die Codex-Anweisungsdatei („Projektanweisungen für Codex“) und verweist auf CLAUDE.md. Claude Code ignoriert sie, weil eine CLAUDE.md existiert; das ist hier gewollt. Handoff Vorschlag 4: weder importieren noch entfernen.

### 5.8 Messskripte ins Repo

Beide Skriptfamilien (`cache_ttl_analysis*.py`, `context_fill_analysis.py`) sind der Vorher-nachher-Maßstab für jede Maßnahme oben und für das TTL-Experiment im wlh-Projekt (Nachmessung ab 04.10.). Vorschlag: Ordner `messung/` im Repo `Claude_global_setup` mit den Skripten, einer README (Aufruf, Kennzahlen, Lesart) und dem Report vom 20.09. als Basislinie. Der Ordnername ist Sebastians Entscheidung. Folgepunkt aus der Messung: Abschnitt B des Skripts bucketet `.jsx` und `.mjs` als „sonstige“; vor dem Einchecken korrigieren.

### 5.9 Offene Commits: erledigt

Der Handoff nannte den Branch `claude/prompt-cache-ttl-config-df32eb` und `wlh-preiskalkulation-app/.claude/settings.json` als nicht committet. Geprüft am 20.09.: der Branch ist sauber und in `main` enthalten, die Settings-Datei ist committet (`d154813`). Handoff Vorschlag 6 ist gegenstandslos. Offen sind nur die zwei Dateien dieser Session im Worktree `zealous-napier-a3bed1` (diese Einschätzung und das Inventar).

## 6. Was aus dem Handoff damit beantwortet ist

| Punkt | Ergebnis |
|---|---|
| Lesezugriffe sperren | Teilweise ja: gezielte Deny-Liste ohne `node_modules`, weil Deny auch Bash-Lesekommandos erfasst (Abschnitt 4, 5.4) |
| Hook-Ausgaben | Geprüft: ungekürzt, aber klein (0,2 Prozent im Achttage-Fenster, hochgerechnet 1,5); Hygiene mit Paket C |
| Code-Policies | Nein als Token-Maßnahme; Zahlen in 3.1 und 4 |
| Vorschlag 1 (erst messen) | Erledigt, Skript liegt vor |
| Vorschlag 2 (Pakete klein) | Ja, als CLAUDE.md-Zeile; Ziel „Anteil über 200K halbieren“ (5.1) |
| Vorschlag 3 (`omitClaudeMd`) | Nein (5.6) |
| Vorschlag 4 (`AGENTS.md`) | Lassen (5.7) |
| Vorschlag 5 (Skripte ins Repo) | Ja (5.8) |
| Vorschlag 6 (Commits) | Gegenstandslos, bereits committet (5.9) |

## 7. Reihenfolge, falls freigegeben

1. Second-Brain-Skill und Agent-Definitionen (5.2 erster Punkt, 5.3): Textänderungen ohne Risiko, sofort messbar. Skill `writing-for-agents` für die Formulierung.
2. CLAUDE.md-Zeile zur Paketgröße und Briefing-Abschnitte (5.1, 5.2 zweiter Punkt).
3. Deny-Liste für Build-, Cache- und Logpfade (5.4) über `update-config`, mit Abnahmetest im Bypass-Modus.
4. Skripte ins Repo (5.8); dabei die Hook-Auswertung nach Datum filtern, damit die nächste Messung nur Tage mit aktiven Hooks zählt, und die Bash-Junk-Erkennung auf Pfadsegmente umstellen.
5. Nach zwei bis drei Wochen den Anteil der Läufe über 200K, den Anteil wiederholter Reads und den Voll-Read-Anteil nachmessen. Erst dann über den Doku-Umbau in „Plan Legacy code Migration“ entscheiden.

Was nicht kommt: Lint-Policies aus der Quelle, Deny für `node_modules`, ein eigener Bash-Lese-Hook, `omitClaudeMd`, `bashOutputMaxChars`, `autoCompactWindow`.

## Anhang: Datenquellen

- Messskript und Report: `%LOCALAPPDATA%\Temp\context_fill_analysis.py`, `context_fill_analysis_output.txt`; v1-Kopien daneben. Abschnitte A bis F Erstmessung, G Nachmessung, beide 20.09.
- Projektinventar: `inventar-projekte-2026-09-20.md` in diesem Repo.
- Doku-Fakten (Agent `claude-code-guide` und Verifier, 20.09.): Read-Deny gilt „best effort“ auch für Grep und Glob und ausdrücklich für die Bash-Kommandos `cat`, `head`, `tail`, `sed`, `tee` sowie Redirects, nicht für Grep-Rekursion ohne Dateinamen oder Skripte, die Dateien selbst öffnen (`code.claude.com/docs/en/permissions`, Abschnitt zu Read- und Edit-Regeln); `omitClaudeMd` ab 2.1.271, überspringt User-, Projekt- und Local-CLAUDE.md (`sub-agents`); für Hook-stderr nennt die Doku keine Begrenzung, der Beleg für „ungekürzt“ ist der 40.036-Zeichen-Treffer in Abschnitt G6 des Reports (`hooks-guide`); `bashOutputMaxChars` existiert, Default undokumentiert (`settings-reference`); `autoCompactWindow` existiert, Subagent-Verhalten undokumentiert (`model-config`); keine offizielle Empfehlung zu Dateigrößen-Limits.
- Hooks: `~/.claude/hooks/post-edit.sh`, `read-gate.sh` (Stand 20.09.).
- Vault: `claude-code-prompt-cache-messung`, `claude-code-setup-audit`, `claude-code-hooks`.
