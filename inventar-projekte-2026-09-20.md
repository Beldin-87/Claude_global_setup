# Projektinventar 2026-09-20 (Ergebnis eines Explore-Agents, Sonnet)

_Read-only-Inventar über `C:\GitHub\Projekte`, Vault ausgeschlossen. Quelldateien = `*.js *.jsx *.mjs *.cjs *.ts *.tsx *.py *.html *.css` ohne `node_modules`, `dist*`, `build`, `out`, `coverage`, `.venv`, `venv`, `__pycache__`, `graphify-out`, `.git`, `public*`, `.claude/worktrees`, `.wrangler`. Grundlage für `einschaetzung-token-spar-policies-2026-09-20.md`._

## Code-Projekte

| Projekt | Stack | Tooling | Claude-Konfig | Dateien | Median Zeilen | >300 | >400 | >800 |
|---|---|---|---|---|---|---|---|---|
| wlh-preiskalkulation-app | React 19, Vite, Cloudflare Worker, Vitest; JS/JSX, kein TS | kein ESLint, kein Prettier, kein tsconfig, Vitest ja | CLAUDE.md 10.240 B, AGENTS.md 2.223 B (Codex), CONTEXT.md 22.677 B, `.claude/settings.json` 37 B | 180 | 134 | 44 | 31 | 4 |
| WlH Preiskalkulation/konfigurator | React 19, Vite; JS/JSX | ESLint Flat Config, nur `js.configs.recommended` + react-hooks/react-refresh, keine `max-lines`/`complexity` | keine | 13 | 112 | 6 | 4 | 1 |
| fantasy-draft-helper | Python, `requirements.txt`, pytest-Konvention | kein Ruff/Pylint/mypy/vulture, kein pyproject | keine (nur launch.json) | 42 | 375,5 | 23 | 21 | 11 |
| kinetic-app | Kotlin/Android | außerhalb der Policy-Liste | CLAUDE.md 2.116 B | 0 im Scope | | | | |

Größte handgeschriebene Dateien:

- wlh-preiskalkulation-app: `src/konfigurator/orchestrierung.js` 1.026, `tools/inventar-excel-anmerkungen.mjs` 945, `src/konfigurator/konfigurator.css` 802, `tools/inventar-excel.mjs` 793, `src/kundenansicht/kundenansicht.test.jsx` 781, `src/vergleich/vergleich.test.js` 759, `src/konfigurator/orchestrierung.test.js` 747, `worker/api.test.js` 722. (`design/.../support.js` 1.768 ist generiert.) `src/konfigurator/konfigurator.jsx` heute 406 Zeilen.
- fantasy-draft-helper: `tests/test_empfehlung.py` 2.463, `tests/test_cockpit.py` 1.965, `empfehlung.py` 1.598, `cockpit.py` 1.481, `tests/test_draft_feed_espn.py` 1.295, `cheatsheet.py` 1.151, `nebenbedingungen.py` 992.
- WlH Preiskalkulation: `konfigurator/src/KatalogView.jsx` 416, `App.jsx` 371; Root-HTML-Blueprint 1.172 (kein Quellcode).

## Übrige Ordner

- Kein Code: Claude_global_setup (Skripte/Markdown), Hausbau, Investements, research, Repo SA-Analyse, selbstauskunft-analyse.
- Plan Legacy code Migration: Analyse-/Spezifikations-Repo mit über 5.000 Markdown-Dateien; Code nur inzidentell (13 handgeschriebene Skripte, `generator/poster.py` 1.417 Zeilen); 11 generierte Archify-HTML-Diagramme mit rund 15.000 Zeilen. CLAUDE.md 637 B, AGENTS.md 5.556 B.
- Pv-Anlage-Konvo: ein Node-Skript (`proxy.mjs`, 308 Zeilen), `.claude/settings.local.json` 3.602 B.
- BA-Criff-claude_skills: vendorter Drittanbieter-Code (Anthropic-Skills), 52 Dateien, drei identische `validators/base.py`-Kopien mit 875 Zeilen.
- IIBA CBAP, corneliabraun-redesign, wlh-klimaanlage-planung, yoga-prototype: statische HTML/kleine Skripte, kein Tooling.
- wlh-preiskalkulation-app-wt-graphify: Worktree von wlh-preiskalkulation-app, kein eigenes Repo.

## Gesamtzeile

18 Ordner, 6 ohne Code, 1 Kotlin, 3 JS-Projekte (zwei davon dasselbe Repo), 1 Python-Projekt. ESLint in genau einem Projekt (Konfigurator, nur recommended). Zeilen- oder Komplexitätsregel: in keinem. Prettier, tsconfig, jscpd, knip, dependency-cruiser, Ruff, mypy, vulture, pre-commit, Husky, lint-staged: nirgends.
