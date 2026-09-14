# Umsetzung Paket D (Setup-Audit)

_Stand 2026-09-14. Freigabe durch Sebastian am 2026-09-14 für Paket D aus dem Setup-Audit, dazu die Entscheidung, die 15 Plugin-Override-Einträge in `settings.json` zu belassen._

## Paket D: Sediment archivieren

**Teil 1 — sechs `.bak`-Dateien** (`CLAUDE.md.bak-2026-08-22`, `CLAUDE.md.bak-2026-09-03`, `CLAUDE.md.bak-2026-09-03-vor-ap2`, `CONTEXT.md.bak-2026-09-03`, `settings.json.bak-2026-09-12`, `settings.json.bak-2026-09-13`) byte-exakt (md5-geprüft) nach `archiv/bak-dateien/` kopiert und committet, zusammen 34.941 Bytes.

**Teil 2 — fünf Memory-Ordner** (`C--GitHub-Projekte-IIBA-CBAP`, `C--GitHub-Projekte-Plan-Legacy-code-Migration`, `C--GitHub-Projekte-Pv-Anlage-Konvo`, `C--GitHub-Projekte-Repo-SA-Analyse`, `G--Meine-Ablage-Projekte-WlH-Preiskalkulation`; 27 Dateien, 145.515 Bytes) byte-exakt (md5-geprüft) nach `archiv/memory/<Projektordnername>/` kopiert, aber **nicht committet**: Die Sensibilitätsprüfung fand in mehreren Dateien echte Treffer (siehe unten). Nach der Vorgabe für diesen Fall geht nur Teil 1 in den Commit; Teil 2 bleibt als unversionierte Kopie im Arbeitsverzeichnis liegen, bis die gefundenen Stellen bewertet sind.

### Sensibilitätsprüfung

- **Teil 1** (6 Dateien): keine Treffer. Ein Regex-Fehlalarm (`sk-` als Substring in „Task-Beschreibung“, `CONTEXT.md.bak-2026-09-03` Zeile 21) wurde geprüft und verworfen — keine reale API-Key-Zeichenkette, keine Zeichen danach, die zu einem Key passen.
- **Teil 2** (27 Dateien): Treffer in 8 von 27 Dateien, keine davon committet:
  - E-Mail-Adressen (10 eindeutige Adressen, private Gmail-Adressen von Sebastian und Familie sowie Geschäftskontakte) in `cbap-zertifizierung.md`, `bauprojekt-gmail-organisation.md` (3 Zeilen), `hausbau-klimaanlage.md`, `hausbau-pv-angebote.md`, `MEMORY.md` (WlH-Ordner), `steuer-2025-kontext.md` (2 Zeilen), `wlh-vollkonfigurator.md`.
  - Telefonnummern in `hausbau-klimaanlage.md`, `hausbau-pv-angebote.md`.
  - Euro-Beträge mit Nachkommastellen (46 Fundstellen, darunter Kalkulations- und Preiswerte im WlH-Preiskalkulation-Ordner) in `hausbau-klimaanlage.md`, `hausbau-ordnerstruktur.md`, `hausbau-pv-angebote.md`, `catalog-two-price-classes.md`, `dependency-model-finding.md`, `steuer-2025-kontext.md`, `wlh-pitch-demo-entscheidungen.md`, `wlh-vollkonfigurator.md`.
  - IBAN und API-Keys/Tokens: keine Treffer in Teil 2.

### Löschliste für Sebastian

Sicher archiviert und committet — Original kann gelöscht werden:
- die sechs `.bak`-Dateien unter `C:\Users\szieg\.claude\` (Root).

Bereits verbessert im Repo vorhanden (`hooks/tests/`, `cases.txt` byte-identisch) — Original kann gelöscht werden:
- die drei Temp-Ordner `hooktest`, `hooktest2`, `eoltest` unter `%LOCALAPPDATA%\Temp`.

Noch NICHT löschen — Kopie liegt nur unversioniert im Arbeitsverzeichnis, Entscheidung zu den Sensibilitätsfunden steht aus:
- die fünf Memory-Ordner unter `C:\Users\szieg\.claude\projects\...\memory`.

## Plugin-Overrides

Entscheidung: belassen. Die 15 Einträge in `settings.json` kosten im Leerlauf nichts und greifen erst bei einer späteren Version; ein Abschalten würde rund 720 Tokens je Turn sparen, kostet aber Funktionalität, die `defuddle` beziehungsweise die Office-Skills bereitstellen.

## Second Brain

Der Ingest der Umsetzungssession wurde am 2026-09-14 von einem Verifier geprüft und in einer Korrekturrunde nachgebessert; Details stehen im Vault-Log.
