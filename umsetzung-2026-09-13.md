# Umsetzung der Pakete A und B (Setup-Audit)

_Stand 2026-09-14, Session „Umsetzung“. Freigabe durch Sebastian am 2026-09-13 für Paket A und B aus `empfehlungen.md` Abschnitt 10, mit einer Änderung: Stufe-2-Skills behalten eine minimale Beschreibung (eigene Skills: Frontmatter-Satz unter 80 Zeichen; Plugin- und eingebaute Skills: `skillOverrides`-Wert `name-only` statt `user-invocable-only`). Ausgangsstand aller geänderten Steuerdateien byte-exakt unter `archiv/2026-09-13/`._

## 1. Ergebnis in einem Absatz

Beide Pakete sind umgesetzt und je von einem Verifier mit frischem Kontext abgenommen (Paket A: 5 von 5 Prüfpunkten, Paket B: 7 von 7), Korrekturrunden: 0 je Paket. Die Ebene-1-Dateien (`CLAUDE.md`, `rules/context7.md`) sind um 2.204 Bytes kürzer, die Agent-Definitionen um 1.054 Bytes; alle 123 Regel-IDs sind am Zielort oder begründet gestrichen. Die Regressionsmatrix läuft aus dem Repo (128 Guardrail-Fälle, 12 Lese-Schranken-Fälle, alle grün). Ein Executor-Subagent startet jetzt mit 39.390 statt 42.564 Tokens Fixkontext. Ein Befund schränkt Paket B ein: `skillOverrides` wirken in der aktuellen Claude-Code-Version nicht auf Plugin-Skills (Abschnitt 4).

## 2. Was geändert wurde

**Paket A, Textdateien unter `~/.claude`** (genau nach Zieltabelle Abschnitt 5 der Empfehlungen):

| Datei | Vorher | Nachher | Änderung |
|---|---|---|---|
| `CLAUDE.md` | 7.241 | 6.039 | R003, R009, R014, R024, R043 gestrichen; R004–R006, R010, R022/R023, R028, R033–R037, R048/R049 gekürzt; R008 (nimmt R050/R051 und `claude-code-guide` auf) und R019 (`/to-spec` dem Nutzer vorschlagen) umformuliert |
| `rules/context7.md` | 2.397 | 1.395 | Abschnitt „How to look up“ (C012–C018) auf zwei Sätze gekürzt, Auslöser C001–C011 unverändert |
| `agents/executor.md` | 3.647 | 3.033 | Context7-Abschnitt (E019–E021) gestrichen, E004 und E026 gekürzt |
| `agents/verifier.md` | 2.269 | 1.829 | Context7-Abschnitt (V018–V019) gestrichen, V004 gekürzt |
| `CONTEXT.md` | 5.251 | 5.441 | Einträge Executor, Verifier, Traceability-Datei gekürzt; Agent-Definition und Pointer ergänzt (nur per Pointer geladen, kein Token-Druck) |

Zeilenenden erhalten: `CLAUDE.md` CRLF (52 Zeilen, 52 CR), die vier anderen LF.

**Paket B:**

- `hooks/read-gate.sh`: Junk-Ordner-Regel überspringt `.md` und `.txt`; Lockfile- und Größenregel greifen weiter (auch für `.md`).
- `settings.json`: Matcher `Agent|Task` → `Agent`; `skillOverrides` von 11 auf 33 Einträge (18 `name-only`, 4 `off`, siehe Abschnitt 4). Kopfkommentar in `hooks/agent-gate.sh` angepasst.
- `skills/` (Git-Repo `Beldin-87/claude-skills`): `git-guardrails-claude-code`, `context7-mcp`, `grill-me` per `git rm` entfernt, staged, nicht committet. `description` von `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`, `wizard` auf 67–70 Zeichen gekürzt.
- Repo: `hooks/tests/` mit `run-guard.sh` (128 Fälle aus `cases.txt`) und `run-read-gate.sh` (12 selbst erzeugte Fixtures), `.gitattributes` mit LF-Zwang für `*.sh` und `hooks/tests/*.txt`, README-Abschnitte „Struktur“ und „Bewusste Dopplungen“.

## 3. Messung vorher/nachher

| Posten | Vorher | Nachher | Differenz |
|---|---|---|---|
| Ebene 1 (`CLAUDE.md` + `rules/context7.md`), Bytes | 9.638 | 7.434 | −2.204 (rund 550 Tokens je Turn, beide Leser) |
| Agent-Definitionen, Bytes | 5.916 | 4.862 | −1.054 (nur im Agentenlauf) |
| Skill-Beschreibungen im Payload, Bytes (wirksamer Teil) | 17.700 | rund 12.550 | −5.147 (rund 1.290 Tokens je Turn): 7 eingebaute Skills auf `name-only` (3.990), 2 sichtbare Skills gelöscht (508), 4 Beschreibungen gekürzt (649) |
| Skill-Liste, Einträge | 54 | 52 | −2 |
| Executor-Startkontext ohne Tool-Aufruf, Tokens (Probe) | 42.564 | 39.390 | −3.174 (−7,5 %) |

Die Token-Probe ist eine Einzelmessung mit demselben Auftrag wie am 13.09. („beschreibe deinen Kontext ohne Tool-Aufruf“); die Größenordnung passt zur Bytes-Schätzung (rund 2.000 Tokens Ersparnis je Executor-Turn). `/context` in einer frischen Hauptsession (Sebastian, 2026-09-14): 42,9k Tokens belegt, davon über dieses Setup steuerbar rund 7,9k: Memory-Dateien (`CLAUDE.md` + `rules/context7.md`) 3,3k, Skill-Liste 4,5k, Agent-Liste 0,1k. Der Rest ist Harness: MCP-Tools 11,3k (dazu 72,8k deferred, die nichts kosten), System-Tools 7,8k, Systemprompt 4,4k, Nachrichten 11,5k. Einen Vorher-Wert aus einer Hauptsession gibt es nicht; die Byte-Schätzung des Audits (7.320 → 4.740 Tokens) rechnete mit rund 4 Bytes je Token, gemessen sind es 2,3 (deutscher Regeltext) bis 2,8 (Skill-Beschreibungen). Verlässliches Vorher/Nachher-Paar bleibt die Executor-Probe.

## 4. Befund: `skillOverrides` und Plugin-Skills

Der `name-only`-Test lief in zwei Stufen. Erst mit `keybindings-help` als Einzelfall und zwei Kontrollen (`loop`, `wizard` auf `user-invocable-only`): Der Probe-Subagent sah `keybindings-help` nur noch als Namen, die Kontrollen gar nicht mehr, und konnte den Skill trotzdem per Skill-Tool laden. Damit war `name-only` für die Freigabe-Fassung nutzbar. Die Nachher-Probe nach Paket B zeigte dann: Bei eingebauten Skills (`dataviz`, `claude-api`, `loop`, `run`, `schedule`, `fewer-permission-prompts`, `keybindings-help`) wirkt `name-only`, bei allen 15 Plugin-Einträgen (`anthropic-skills:*`, `diagram-design:*`, `obsidian:*`, darunter die vier `off`-Einträge) nicht: Beschreibungen und Einträge sind unverändert im Payload.

Ursache im Code der CLI (Zeichenketten in `claude.exe`, npm-Version 2.1.238 und Desktop-Version 2.1.266 wortgleich): Die Funktion, die den Override für die Skill-Liste bestimmt, liefert für Skills mit Quelle „plugin“ immer „on“, und die `/skills`-Oberfläche zeigt Plugin-Skills als gesperrt „on“ mit Quelle „plugin“. Die Doku-Aussage aus Anhang A der Empfehlungen (Frage 2, „gilt für Plugin-Skills“) trifft für diese Versionen nicht zu. Die 15 Einträge bleiben vorerst in `settings.json` als dokumentierte Absicht; sie kosten nichts und greifen, sobald eine Version Plugin-Skills berücksichtigt. Alternative, falls die rund 720 Tokens je Turn wichtiger sind: das Plugin `obsidian@obsidian-skills` ganz abschalten (kostet `defuddle`, 3 Aufrufe in 30 Tagen) oder `anthropic-skills` ganz abschalten (kostet die Office-Skills). Entscheidung Sebastian.

Nebenbefunde derselben Tests: Subagenten einer laufenden Session sehen den aktuellen Dateistand der `settings.json` (die Doku lässt das offen). Die Terminal-CLI (`claude -p`) ist nicht angemeldet („OAuth session expired“); ein Test in einem frischen Prozess war deshalb nicht möglich.

## 5. Offene Punkte

Für Sebastian:
- Branch `claude/global-setup-umsetzung-2026-459da7` nach `main` mergen und pushen; im Skills-Repo `~/.claude/skills` die sechs staged Löschungen und vier Beschreibungsänderungen committen (dort liegen weitere, ältere uncommittete Änderungen).
- Entscheidung zu den Plugin-Overrides (Abschnitt 4).
- Worktree-Hülle `.claude/worktrees/global-setup-audit-fed341` ist weiter gesperrt („Device or resource busy“); nach Neustart der Desktop-App `rmdir`.
- GitHub: Standard-Branch auf `main` umstellen, Remote-Branch `claude/global-setup-audit-fed341` löschen.
- Paket C (ESLint-Hook ins WlH-Repo, eigene Session) und Paket D (Sediment: `.bak`-Dateien im `~/.claude`-Root, drei Temp-Testordner, fünf Memory-Ordner) wie in `empfehlungen.md` Abschnitt 9 und 10.

Für das Second Brain (Nachtrag auf `wiki/claude-code-setup-audit.md`): Zahlen aus Abschnitt 3, Befund aus Abschnitt 4, Lesson: Doku-Aussagen zu Harness-Verhalten mit einer Probe verifizieren, bevor sie eine Freigabe tragen.
