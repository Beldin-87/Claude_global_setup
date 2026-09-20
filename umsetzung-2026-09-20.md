# Umsetzung 2026-09-20: SendMessage-Regel korrigiert

_Stand 2026-09-20. Ausgangsstand von `CLAUDE.md` und `CONTEXT.md` byte-exakt unter `archiv/2026-09-20/`._

## Anlass

Ein Reddit-Post zur Einstellung `subagentPromptCacheTtl` warf die Frage auf, ob
die bisherige CLAUDE.md-Regel „Folgearbeit im selben Bereich per SendMessage an
den bestehenden Agent, statt neu zu spawnen — erhaltener Kontext ist schneller
und spart Tokens“ (Schritt 2, DELEGIEREN) tatsächlich Tokens spart. Eigene
Messung über 60 Tage lokaler Subagent-Transkripte, Skripte unter
`%LOCALAPPDATA%\Temp\cache_ttl_analysis.py` und `cache_ttl_analysis_2.py`
(nicht im Repo).

## Befund

- 220 SendMessage-Resumes an bereits fertige Subagents.
- Median 101K Tokens Cache-Write je Resume, gegenüber 27K Startkosten eines
  frischen Agents.
- Rund zwei Drittel der Resumes schreiben den gesamten Kontext neu in den
  Prompt-Cache — auch bei Abständen unter fünf Minuten zwischen den Aufträgen,
  also nicht durch die Cache-TTL erklärbar.
- Folgeaufträge dauern im Median 7 Turns.
- TTL-bedingte Re-Writes (Abstand über der Cache-Gültigkeit) machen nur 8,9 %
  aller Subagent-Cache-Writes aus. Je nach Gewichtung des Abo-Meters läge der
  Effekt von `subagentPromptCacheTtl: "1h"` zwischen 9 % Ersparnis und 46 %
  Mehrkosten auf Subagent-Writes. Global deshalb nicht gesetzt; als Experiment
  am 2026-09-20 projektweise in `wlh-preiskalkulation-app/.claude/settings.json`
  gesetzt.

Fazit: Weiterführen ist bei kurzen Folgeaufträgen schneller (kein 27K-Neustart,
kein erneutes Briefing), aber nicht billiger als ein frischer Agent — die
bisherige Formulierung „spart Tokens“ war falsch.

## Änderung

**`CLAUDE.md`, Zeile 6 (Schritt 2, DELEGIEREN):**

Alt:
> Arbeite weiter, während Subagents laufen, statt blockierend zu warten; für Folgearbeit im selben Bereich führ den bestehenden Agent per SendMessage weiter, statt neu zu spawnen — erhaltener Kontext ist schneller und spart Tokens.

Neu:
> Arbeite weiter, während Subagents laufen, statt blockierend zu warten. Folgearbeit, die auf den Funden eines Agents aufbaut, etwa Debugging, Review-Fixes oder Refactorings, geht per SendMessage an den bestehenden Agent; lässt sie sich in einem knappen Briefing vollständig beschreiben, an einen frischen. Weiterführen ist schneller, nicht billiger.

Rest der Zeile (Satz „Du selbst schreibst keinen Code …“) unverändert. Zeile
6 bleibt Zeile 6, Zeilenzahl der Datei unverändert (52), CRLF erhalten.

**`CONTEXT.md`:** neuer Glossareintrag **Resume-Write** zwischen „Handoff“ und
„Sediment“ (Kernzahlen aus dem Befund oben, Verweis auf die korrigierte
CLAUDE.md-Regel, Hinweis auf die Claude-Code-Version 2.1.27x und Neubewertung
bei einer Korrektur durch Anthropic). LF erhalten.

**`inventar.md`:** Zeile zu R012 (Abschnitt 1.1) auf den neuen Wortlaut,
gleichen Fundort `CLAUDE.md:6`, neue Token-Zahl 70 aktualisiert. Neuer Eintrag
CTX005 (Abschnitt 1.5) für den Resume-Write-Glossareintrag (Fundort
`CONTEXT.md:68`, 155 Tokens) ergänzt, da Abschnitt 1.5 nur Einträge mit
Regelgehalt führt und dieser eine bisherige Regel begründet.

Zählmethode Tokens: wie im Kopf von `inventar.md` dokumentiert Bytes des
zitierten Original-Wortlauts ÷ 4. Für R011/R012 ließ sich die genaue
Zeichenauswahl der Bestandswerte rekonstruieren (exaktes Zitat inklusive
Satzzeichen, kaufmännisch gerundet: 40,5 → 41), für die CTX-Tokens ist die
exakte Zeichenauswahl der Altwerte nicht dokumentiert; für CTX005 wurde
deshalb die gesamte Eintragszeile (ohne Kopfzeile und `_Avoid_`-Zeile)
gezählt, analog zu CTX002–CTX004.

## Archivkopie

`archiv/2026-09-20/CLAUDE.md` und `archiv/2026-09-20/CONTEXT.md`, angelegt
vor bzw. (bei CLAUDE.md) rekonstruiert aus dem dokumentierten Alt-Wortlaut
und gegen die Größe vor der Session (6.039 Bytes) geprüft.

| Datei | Vorher (Bytes / SHA-256) | Nachher (Bytes / SHA-256) |
|---|---|---|
| `CLAUDE.md` | 6.039 / `76a4fcf6…995f5` | 6.157 / `c0bcab77…a357be` |
| `CONTEXT.md` | 5.441 / `9088a42a…def30b6` | 6.135 / `cc2f3ac2…503290` |

`archiv/2026-09-20/*` entspricht byte-exakt der „Vorher“-Zeile.

## Offen

- Experiment `wlh-preiskalkulation-app`: nach etwa zwei Wochen mit dem
  Messskript prüfen, ob die Subagent-Writes dort im `ephemeral_1h`-Bucket
  landen und der Anteil TTL-bedingter Re-Writes sinkt. Das Skript summiert
  bisher über alle Projekte und braucht dafür eine Aufschlüsselung je Projekt.
- `omitClaudeMd: true` für `executor`/`verifier` prüfen: Subagents laden laut
  Doku die gesamte CLAUDE.md-Hierarchie, obwohl deren Regeln die Hauptsession
  steuern. Dann müsste `rules/context7.md` in die Agent-Definitionen wandern.
  Eigenes Paket.
- Messskripte liegen unter `C:\Users\szieg\AppData\Local\Temp\cache_ttl_analysis.py`
  und `cache_ttl_analysis_2.py`, nicht im Repo.
