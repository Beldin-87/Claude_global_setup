# Regressionsmatrix für die Hooks

Testet zwei der globalen PreToolUse-Hooks unter `~/.claude/hooks/` gegen feste
Fallsammlungen. Beide Runner brauchen keine Umgebungsvariablen und keine
Vorbereitung; sie legen ihre Fixtures selbst in einem Temp-Ordner an und
räumen danach auf. Nach jeder Änderung an einem der beiden Hooks werden sie
erneut gefahren.

## Aufruf

```bash
bash hooks/tests/run-guard.sh
bash hooks/tests/run-read-gate.sh
```

Beide geben je Fall eine Zeile mit erwartetem und tatsächlichem Ergebnis aus
und enden mit `bestanden: N   fehlgeschlagen: M`.

## Dateien

- `cases.txt` — 128 Fälle für `guard-destructive.sh` (Befehl, erwartet BLOCK
  oder ALLOW), eine Zeile je Fall. Wird von `run-guard.sh` gelesen.
- `run-guard.sh` — spielt jeden Fall aus `cases.txt` als synthetisches
  PreToolUse-Payload gegen `~/.claude/hooks/guard-destructive.sh`.
- `run-read-gate.sh` — prüft `~/.claude/hooks/read-gate.sh` gegen selbst
  angelegte Fixtures: Dateien in Junk-Ordnern (`build`, `node_modules`, `dist`),
  ein Lockfile, eine übergroße `.md`-Datei, eine leere Datei, ein Verzeichnis
  und ein nicht existierender Pfad. Deckt insbesondere die Ausnahme ab, dass
  `.md`/`.txt`-Dateien von der Junk-Ordner-Regel nicht mehr blockiert werden,
  während die Lockfile- und Größenregel weiterhin auch für `.md`/`.txt`
  greifen.

Exit-Code je Fall: 0 = Zugriff frei, 2 = Zugriff blockiert.
