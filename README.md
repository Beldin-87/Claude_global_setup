# Claude_global_setup

Audit und Pflege von Sebastians persönlichem, globalem Claude-Code-Setup unter `~/.claude`:
`CLAUDE.md`, `rules/`, `CONTEXT.md`, `agents/*.md`, `hooks/`, `skills/`, `settings.json`.
Das Setup selbst bleibt unter `~/.claude`; dieses Repo hält Inventar, Empfehlungen und Änderungsvorschläge.
Änderungen an `~/.claude` erfolgen erst nach Freigabe.

## Auftrag (Stand 2026-09-13)

1. Jede Regel steht genau einmal. Je Regel eine Empfehlung, wo sie hingehört, mit Begründung.
2. Tokens sparen; alles benennen, was potenziell viel Tokens verbraucht.
3. Keine Regeln, die sich widersprechen, keine doppelte Ausführung (Text und Hook, zwei Hooks, Skill und Regel).

Handoffs zwischen Sessions liegen unter
`%LOCALAPPDATA%\Temp\handoff-claude-global-setup-*.md`.

## Struktur

- `inventar.md`, `empfehlungen.md` — Bestandsaufnahme und Entscheidungen des Audits.
- `umsetzung-<Datum>.md` — Protokoll einer Umsetzung: was geändert wurde, Prüfergebnis, Messung vorher/nachher, offene Punkte.
- `archiv/<Datum>/` — byte-exakte Sicherungen der Steuerdateien aus `~/.claude` vor einer Änderung, eine Kopie je Umsetzungsdatum (z. B. `archiv/2026-09-13/`).
- `hooks/tests/` — Regressionsmatrix für die globalen Hooks unter `~/.claude/hooks/` (siehe `hooks/tests/README.md`).

## Bewusste Dopplungen

Manche Dopplungen zwischen Regel und Hook oder zwischen zwei Regeltexten sind
kein Aufräumfall, sondern Absicht. Details und Begründung in `empfehlungen.md`
Abschnitt 6.

- **git-push-Deny neben dem Guardrail-Hook**: `guard-destructive.sh` blockiert
  `git push` bereits per Hook, der Permissions-Eintrag `Bash(git push *)`
  verbietet ihn zusätzlich. Keine doppelte Ausführung, weil der Hook vor der
  Permission-Prüfung läuft und bei einer Blockade die Deny-Regel gar nicht
  mehr erreicht wird. Die Deny-Regel greift als zweite Verteidigungslinie
  genau dann, wenn der Hook das Hook-JSON nicht lesen kann und deshalb
  bewusst fail-open durchlässt.
- **„Arbeitsweise“ und „Grenzen“ in beiden Agent-Definitionen**: Die Absätze
  zu parallelen Tool-Calls und zu den Zustimmungsgrenzen stehen wortgleich in
  `agents/executor.md` und `agents/verifier.md`. Das ist beabsichtigt, weil
  der Body jeder Agent-Definition den Standard-Subagent-Prompt ersetzt und
  nicht ergänzt — ohne die Wiederholung würde einer der beiden Leser die
  Regel gar nicht sehen.
- **Dokumentlänge in CLAUDE.md und im Executor-Baustein (R056/E014)**: Die
  Regel „Geschriebene Dokumente richten die Länge am Bedarf aus“ steht in
  CLAUDE.md für die Hauptsession und im Executor-Body noch einmal für den
  Executor-Leser. Die zweite Nennung kostet wenige Tokens, sichert aber, dass
  ein Executor die Regel auch dann kennt, wenn er CLAUDE.md aus anderen
  Gründen nicht beachtet.
