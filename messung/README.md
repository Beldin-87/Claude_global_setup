# Messskripte: Token-Verbrauch der lokalen Claude-Code-Transkripte

## Zweck

Zwei Skriptfamilien, beide reine Analyse-Werkzeuge ohne Schreibzugriff auf die Transkripte:

- **`context_fill_analysis.py`** — Womit wird der Kontext eines Laufs gefüllt (Tool-Ergebnisse nach Tool-Typ, Assistant-Text, Tool-Use-Inputs, User-Text; Read-Tiefe; Kommandoausgaben; Hook-Rückmeldungen; je Projekt; große Kontexte; siehe Modul-Docstring und Abschnitte A–G im Report). Das ist der Vorher-Nachher-Maßstab für die am 20.09. umgesetzten Token-Spar-Policies.
- **`cache_ttl_analysis.py`** und **`cache_ttl_analysis_2.py`** — Prompt-Cache-Verhalten von Subagents: Re-Writes nach einer Cache-TTL-Lücke (`cache_ttl_analysis.py`) sowie vier Kennzahlen rund um Resume-Writes, Startkosten und Endgröße des Kontexts (`cache_ttl_analysis_2.py`, baut auf demselben Parsing/Dateifilter auf). Laufen unverändert, gehören zum TTL-Experiment im wlh-Projekt (siehe „Offener Punkt“ unten).

## Voraussetzungen

- Python 3, keine externen Abhängigkeiten (nur Standardbibliothek).
- Lesen ausschließlich `C:\Users\szieg\.claude\projects\**\*.jsonl` (read-only, keine Schreibzugriffe auf Transkripte).
- Streamen zeilenweise, laden keine ganze Datei in den Speicher.
- Der Report enthält keine Transkriptinhalte — nur Pfade, Kommando-Präfixe (`context_fill_analysis.py`: ≤80 Zeichen) und Zahlen.

## Aufruf (`context_fill_analysis.py`)

```powershell
# Standard: letzte 60 Tage (Datei-mtime), Report ohne --out nach
# <Skriptordner>\context_fill_analysis_output_<YYYY-MM-DD>.txt (Datum des Laufs)
python context_fill_analysis.py

# Festes Datumsfenster (mtime >= since, < until; reines Datum bei --until
# schliesst den Vortag komplett ein)
python context_fill_analysis.py --since 2026-09-21 --until 2026-10-15

# Report in eine Datei schreiben (UTF-8), z. B. für einen Vergleichslauf
python context_fill_analysis.py --since 2026-09-21 --out nachmessung-2026-10.txt
```

`--since`/`--until` akzeptieren `YYYY-MM-DD` oder `YYYY-MM-DDTHH:MM`. Ohne beide Angaben bleibt das Fenster wie bisher (letzte `CUTOFF_DAYS` = 60 Tage, kein Enddatum); ohne `--out` landet der Report seit der Korrekturrunde im Skriptordner (`messung/`) statt in Temp. `cache_ttl_analysis.py`/`cache_ttl_analysis_2.py` haben keine Kommandozeilenargumente, öffnen Dateien nur lesend und schreiben ihr Ergebnis ausschließlich nach stdout (`python cache_ttl_analysis.py > ergebnis.json`, `python cache_ttl_analysis_2.py > ergebnis.txt`); sie bleiben unverändert.

## Zwei Basislinien in diesem Ordner

- **`context_fill_analysis_output_2026-09-20.txt`** — historischer Report des *Original*-Skripts aus `%LOCALAPPDATA%\Temp`, Lauf 20.09. 11:58, 897 Subagent- / 214 Hauptsession-Transkripte. Das ist der Report, auf den `einschaetzung-token-spar-policies-2026-09-20.md` verweist; er bleibt unverändert als historisches Dokument.
- **`context_fill_analysis_basislinie_2026-09-20.txt`** — Lauf des *Repo*-Skripts (mit Datumsfenster, den breiteren Code-Endungen und der überarbeiteten Junk-Erkennung) über dasselbe Fenster (`--since 2026-07-22 --until 2026-09-20T11:58`). Nur 880/203 Transkripte, weil einzelne Dateien zwischen 11:58 und diesem späteren Lauf durch fortgesetzte Sessions über die feste Fenstergrenze hinausgewachsen sind (mtime-Drift, siehe Lesart) — das ist unabhängig von den Definitionsänderungen. Diese Datei ist die Referenz für die Nachmessung, weil nur Läufe mit denselben Endungs-/Junk-Definitionen vergleichbar sind.

## Kennzahlen für die Nachmessung

| Kennzahl | Basiswert (neue Basislinie) | Report-Abschnitt |
|---|---|---|
| Anteil Subagent-Läufe über 200K Endkontext | 21 % (mit 59 % des Input-Verbrauchs) | Abschnitt G1 — unverändert durch die Korrekturen, Wert aus der historischen Basislinie (20.09., 11:58) |
| Wiederholte Reads derselben Datei im selben Lauf | 14,0 % der Read-Zeichen (historisch: 13,9 %) | Abschnitt B |
| Voll-Read-Anteil (ohne offset/limit) | 74,0 % (historisch: 74,3 %) | Abschnitt B |
| `.md`-Reads am Kontextinhalt | 37,3 % (historisch: 37,2 %) | Abschnitt B (Zeichen je Endung), bezogen auf Abschnitt A („Summe der 4 Kategorien“) |
| Dateien-Lesen per Bash (`cat`/`head`/`sed -n` u. ä.) am Kontextinhalt | 10,7 % (historisch: 10,8 %) | Abschnitt G4 (Klasse „datei-lesen“), bezogen auf Abschnitt A |
| Reads von `index.md` (Vault) | 55 Reads, 941K Zeichen, ø 17K je Read (historische Basislinie; überwiegend Teil-Reads, da ø-Größe deutlich unter der Dateigröße) | Abschnitt B, Top-20 gelesene Dateien |

Die Abweichungen zwischen historischer und neuer Basislinie in den Abschnitten B, G3–G6 sind überwiegend Nachkommastellen: Die Endungs- und Junk-Listen sind seit der Korrekturrunde bewusst breiter (`.jsx`/`.mjs`/`.cjs`/`.sh`/… zählen jetzt als Code; `dist-*`, Lockfile-Namen und `.venv`/`venv` zählen jetzt als Junk), das verschiebt Anteile innerhalb der betroffenen Abschnitte, ändert aber die hier zitierten Gesamtquoten kaum. `index.md` ist bewusst mit dem historischen Wert stehen geblieben, weil sich die Read-Zahl nur durch Zeitablauf (fortgesetzte Sessions), nicht durch die Definitionsänderungen verschiebt.

Quelle: beide Basislinien-Dateien in diesem Ordner sowie `einschaetzung-token-spar-policies-2026-09-20.md`.

## Lesart

- Token-Zahlen sind durchgängig eine Näherung: Zeichen ÷ 4. Ausnahme: „Endkontext“ in Abschnitt E/F und die Werte in Abschnitt G1 stammen exakt aus den `usage`-Feldern (`input_tokens` + `cache_read_input_tokens` + `cache_creation_input_tokens`) des letzten bzw. jedes Assistant-Turns.
- Das Datumsfenster filtert über die Datei-`mtime`, nicht über Zeitstempel innerhalb der JSONL-Zeilen. Ein Transkript, das über die Fenstergrenze hinweg weitergeschrieben wurde (fortgesetzte Session), fällt bei einer festen Obergrenze (`--until`) komplett aus dem Fenster, auch wenn ein Teil seines Inhalts vor der Grenze entstand.
- Hook-Trefferquoten (Abschnitt D, G6) beziehen sich erst ab `HOOKS_ACTIVE_SINCE` (2026-09-12) auf Transkripte mit mtime ab diesem Datum, weil die Hooks vorher nicht existierten. Absolute Trefferzahlen in der Haupttabelle laufen weiter über das gesamte Report-Fenster und sind entsprechend beschriftet.
- Die beiden mit „bezogen auf Abschnitt A“ markierten Kennzahlen in der Tabelle oben sind nicht direkt im Report ausgewiesen, sondern aus den genannten Abschnitten abgeleitet (Zeichen der Teilmenge ÷ „Summe der 4 Kategorien“ aus Abschnitt A, gleicher Lauf/gleiches Fenster).

## Offene Punkte

- Die Nachmessung läuft frühestens Mitte Oktober, mit `--since 2026-09-21` (Stichtag der Umsetzung), damit sie sauber von der Basislinie getrennt bleibt.
- Die TTL-Auswertung im wlh-Projekt (`cache_ttl_analysis*.py`, Experiment ab 20.09.) braucht noch eine Aufschlüsselung je Projekt (offener Punkt aus `umsetzung-2026-09-20.md`).
- Code-Regeln-Experiment im wlh-Projekt seit 21.09.2026: bei der Nachmessung die Zeile `wlh-preiskalkulation-app` getrennt betrachten und den Token-Zahlen die Verstoßzahlen aus `npm run pruefe:code:bericht` gegenüberstellen (Basislinie: `docs/code-regeln-basislinie-2026-09-21.md` im wlh-Repo).
