# Umsetzung 2026-09-20: Token-Spar-Policies umgesetzt

_Stand 2026-09-20. Ausgangsstand der geänderten Dateien byte-exakt unter `archiv/2026-09-20-token-spar-policies/`._

## Anlass

Handoff vom 20.09. (`%LOCALAPPDATA%\Temp\handoff-claude-global-setup-2026-09-20-token-spar-policies-umsetzung.md`)
legte die Umsetzung der in `einschaetzung-token-spar-policies-2026-09-20.md` (Abschnitte 5 und 7)
vorgeschlagenen vier Token-Spar-Maßnahmen vor. Sebastian gab alle vier frei: „Alle vier freigegeben,
setz um.“ Messgrundlage der Einschätzung: 60 Tage Subagent-Transkripte (897 Läufe), Skript
`%LOCALAPPDATA%\Temp\context_fill_analysis.py` (nicht im Repo). Reihenfolge nach Abschnitt 7 der
Einschätzung: Skill- und Agent-Definitionen zuerst, dann `CLAUDE.md`, dann die Deny-Liste mit
Abnahmetest.

## Befund

Vier Maßnahmen aus der Einschätzung wurden umgesetzt, dazu eine Ergänzung außerhalb der vier Punkte
an einer Datei, die der Second-Brain-Skill als Autorität nennt (Vault-`CLAUDE.md`). Die Messwerte,
die die jeweilige Maßnahme begründen, stammen aus derselben 60-Tage-Auswertung und stehen bei der
jeweiligen Änderung.

## Änderung 1 — Skill `second-brain` (SKILL.md)

`~/.claude/skills/second-brain/SKILL.md` (LF). Geänderte Zeilen 14, 22, 25, 31; Frontmatter
unverändert.

Alt (Zeile 14):
> Struktur: `raw/` immutable Quellen (nur lesen) · `wiki/` kuratierte Seiten · `index.md` Katalog (immer zuerst lesen) · `log.md` append-only.

Neu (Zeile 14):
> Struktur: `raw/` immutable Quellen (nur lesen) · `wiki/` kuratierte Seiten · `index.md` Katalog (per grep nach dem Projektpräfix befragen, nie ganz laden) · `log.md` append-only (Format per `tail -3`, Eintrag anhängen, nie ganz laden).

Alt (Zeile 22):
> 1. Zielpfade: Nennt das Briefing raw- und Wiki-Pfad, gelten sie wörtlich — `index.md` liest du dann nur, um den Katalog-Eintrag richtig einzuordnen. Ohne vorgegebene Pfade: `index.md` lesen, bei passender Seite aktualisieren statt neu anlegen (`updated:` setzen).

Neu (Zeile 22):
> 1. Zielpfade: Unabhängig vom Auslöser (Handoff oder Direktauftrag) wird `index.md` nur per grep nach dem Projektpräfix befragt (Beispiel: `grep -i "^wlh-" index.md`), um den Zielabschnitt zu finden. Nennt das Briefing raw- und Wiki-Pfad, gelten sie wörtlich. Ohne vorgegebene Pfade: bei passender Seite aktualisieren statt neu anlegen (`updated:` setzen).

Alt (Zeile 25):
> 4. `index.md` (Eintrag im Projekt-Abschnitt) + `log.md` (neuer append-only Eintrag mit Datum und Operation) nachziehen.

Neu (Zeile 25):
> 4. `index.md`: Ankerzeile des Projektabschnitts per `grep -n` finden, nur diesen Bereich mit offset/limit lesen, Katalogeintrag per Edit-Tool anfügen. `log.md`: nie ganz laden — Eintragsformat aus `tail -3 log.md` übernehmen, neuen Eintrag anhängen (Append, z. B. `>>` oder Edit am Dateiende).

Alt (Zeile 31):
> 1. `index.md` lesen — bei bekanntem Projekt nur den Projektabschnitt, z. B. per grep nach dem Präfix (Beispiel: `grep -i "^wlh-" index.md` für das Projekt `wlh`).

Neu (Zeile 31):
> 1. `index.md` Katalog: per grep nach dem Projektpräfix befragen, nie ganz laden (Beispiel: `grep -i "^wlh-" index.md` für das Projekt `wlh`).

Gemessen: 55 Reads von `index.md` mit zusammen 941K Zeichen in 60 Tagen; die Datei ist heute
49 KB groß, ein Voll-Read kostet damit rund 12K Tokens.

Verifier (Sonnet): erste Fassung mit vier Funden — Widerspruch zwischen „nie lesen“ (Grundwissen)
und der `tail -3`-Anweisung an anderer Stelle; die Edit-Tool-Voraussetzung für den grep-Weg fehlte,
sodass ein Executor ohne Edit-Tool doch ganz gelesen hätte; „In beiden Fällen“ ohne klaren Bezug;
uneinheitliche Artikelverwendung. Alle vier Funde in einer Korrekturrunde behoben.

## Vault-Ergänzung — `Bastis Schatz/CLAUDE.md`

Der Skill nennt diese Datei als Autorität; ihre Zeilen 7 und 12 verlangten trotz Änderung 1 weiter
„index.md lesen“. Datei: `C:\GitHub\Projekte\Bastis Obsidian Vault\Bastis Schatz\CLAUDE.md` (LF,
kein Git-Repo — die Archivkopie ist die einzige Sicherung).

Alt:
> - index.md  Katalog aller Seiten. Lies ihn IMMER zuerst, um die richtige Seite zu finden.
> - Query: index.md lesen, passende Seite finden, Antwort mit Quellenbezug geben.

Neu:
> - index.md  Katalog aller Seiten. Befrag ihn IMMER zuerst, per grep nach dem Projektpräfix; nie ganz laden.
> - Query: index.md per grep nach dem Projektpräfix befragen, passende Seite finden, Antwort mit Quellenbezug geben.

Archivkopie: `archiv/2026-09-20-token-spar-policies/vault/CLAUDE.md`.

Sebastian hat die Ergänzung am 20.09. bestätigt.

## Änderung 2 — Agent-Definitionen (`executor.md`, `verifier.md`)

`~/.claude/agents/executor.md` (LF). Neue Zeile 23 (vierter Spiegelstrich in „## Arbeitsweise“):
> Eine Datei liest du je Lauf einmal; nach einem Edit liest du sie nicht erneut, sondern bei Bedarf nur den geänderten Bereich mit offset und limit. Dateien über etwa 400 Zeilen liest du mit offset und limit in dem Ausschnitt, den die Aufgabe braucht.

`~/.claude/agents/verifier.md` (LF). Neue Zeile 35 leer, Zeile 36 (Absatz in „## Arbeitsweise“):
> Eine Datei liest du je Lauf einmal. Dateien über etwa 400 Zeilen liest du mit offset und limit in dem Ausschnitt, den die Aufgabe braucht.

Der Edit-Halbsatz fehlt im Verifier bewusst — der Verifier hat keine Edit-Tools.

Gemessen: wiederholte Reads derselben Datei im selben Lauf sind 13,9 Prozent der Read-Zeichen, der
Voll-Read-Anteil liegt bei 74 Prozent.

Verifier: alle Kriterien erfüllt. Zwei niedrige Anmerkungen ohne Änderungsbedarf: „einmal“ ließe
sich als Obergrenze statt als Verbot lesen; die Zeilenenden-Prüfung läuft in der Praxis per Bash,
nicht per Read-Tool.

## Änderung 3 — `CLAUDE.md`

`~/.claude/CLAUDE.md` (CRLF). Nur Zeile 40 geändert, 203 Bytes angehängt.

Alt:
> - Vollständig im ersten Anlauf: Auftrag, Wozu (wofür das Ergebnis gebraucht wird), Constraints und Akzeptanzkriterien — Nachreichen kostet Effizienz und Qualität.

Neu:
> - Vollständig im ersten Anlauf: Auftrag, Wozu (wofür das Ergebnis gebraucht wird), Constraints und Akzeptanzkriterien — Nachreichen kostet Effizienz und Qualität. Ein Paket hat einen Gegenstand; Implementierung, Protokoll und Ingest sind drei Pakete. Braucht ein Paket ein Dokument, nennt das Briefing Abschnitt oder Zeilen, statt das Dokument ganz lesen zu lassen.

Gemessen: Läufe über 200K Endkontext sind 21 Prozent der Läufe und 59 Prozent des Input-Verbrauchs;
Median-Endkontext 137K. Ziel: den Anteil über 200K halbieren.

Verifier: alle Kriterien erfüllt. Fund niedrig/mittel: der Satz zur Paketgröße stünde als eigener
Spiegelstrich klarer. Entscheidung des Hauptmodells: Platzierung bleibt, weil der Handoff die
Zeilenzahl 52 als Constraint gesetzt hat; als offener Punkt festgehalten (siehe Offen, Punkt 5).

## Änderung 4 — `settings.json` (Deny-Liste)

`~/.claude/settings.json` (LF). Zeile 29 bekam ein Komma, Zeilen 30 bis 40 neu in
`permissions.deny`:

> `Read(./dist/**)`, `Read(./dist-*/**)`, `Read(./.wrangler/**)`, `Read(./graphify-out/**)`, `Read(./**/*.log)`, `Read(./**/package-lock.json)`, `Read(./**/pnpm-lock.yaml)`, `Read(./**/yarn.lock)`, `Read(./**/uv.lock)`, `Read(./**/poetry.lock)`, `Read(./**/Cargo.lock)`

Bewusst nicht aufgenommen: `node_modules` (Deny wirkt auch auf Grep; Kollision mit
`rules/context7.md`, die Typdefinitionen dort lesen lässt), `build` (dort liegt Doku).

Gemessen: 5.322 Bash-Lesezugriffe in 60 Tagen laufen am `read-gate` vorbei, bis zu 865 davon auf
Junk- oder Logpfade. Nach Umstellung der Junk-Erkennung auf Pfadsegmente (`messung/context_fill_analysis.py`, Lauf vom 20.09. mit Fenster bis 11:58) sind es 297; die 865 waren Substring-Treffer und damit eine Obergrenze.

Doku-Recherche (Agent `claude-code-guide`, `code.claude.com/docs/en/permissions`,
`permission-modes`): Deny-Regeln greifen in jedem Modus einschließlich `bypassPermissions`
(wörtlich „Deny rules block in every mode, including bypassPermissions“); Änderungen wirken ab dem
nächsten Tool-Call; Pfadtabelle: `//` absolut, `~/` Home, `/path` relativ zur Settings-Datei, `path`
oder `./path` relativ zum aktuellen Verzeichnis. Der Agent leitete daraus ab, `./` löse in
User-Settings zu `~/.claude` auf — der Abnahmetest widerlegte das (siehe unten).

## Abnahmetest (Deny-Liste)

Fixtures im Worktree, Session im Bypass-Modus: erst durch einen Sonnet-Executor als Subagent
geprüft, danach drei Kernfälle aus der Hauptsession wiederholt.

- Read auf `graphify-out/fixture.json`: abgelehnt („File is in a directory that is denied by your permission settings.“).
- Read auf `dist/fixture.js`, mit und ohne offset/limit: abgelehnt, mit derselben Deny-Meldung statt der Hook-Meldung des `read-gate` — Deny greift vor dem Hook.
- `dist-test/`, `.wrangler/`: abgelehnt.
- Bash `cat fixture.log`, `head -1 sub/nested.log`, `sed -n 1p sub/package-lock.json`, `tail -1 dist/fixture.js`: abgelehnt („Permission to use Bash with command … has been denied.“).
- `cat` mit absolutem Pfad im Worktree: abgelehnt.
- `cat` auf `C:/GitHub/Projekte/wlh-preiskalkulation-app/build/vitest-full.log` (anderes Projekt, per `additionalDirectories` erreichbar): erlaubt.
- Grep in `node_modules`: erlaubt. Read mit offset/limit in `node_modules`: erlaubt.
- Grep-Tool in `dist`: abgelehnt.
- Bash `grep -r fixture .`: erlaubt, mit Treffern aus allen Fixtures.

Fazit: `./`-Muster gelten relativ zum Arbeitsverzeichnis der Session, auch aus der User-Datei —
nicht relativ zu `~/.claude`, wie der Doku-Agent vermutet hatte. Subagents erben die Regeln; kein
Neustart nötig. Fixtures danach entfernt.

## Prüfung (Verifier-Ergebnisse und Entscheidungen)

Zusammenfassung je Änderung:

- **Änderung 1 (Skill):** Verifier fand vier Widersprüche/Unklarheiten in der ersten Fassung, alle in einer Korrekturrunde behoben.
- **Änderung 2 (Agent-Definitionen):** Verifier: alle Kriterien erfüllt, zwei niedrige Anmerkungen ohne Änderungsbedarf.
- **Änderung 3 (CLAUDE.md):** Verifier: alle Kriterien erfüllt, ein Fund niedrig/mittel zur Platzierung — Entscheidung des Hauptmodells: Platzierung bleibt (Zeilenzahl-Constraint aus dem Handoff), als offener Punkt vermerkt.
- **Änderung 4 (Deny-Liste):** kein klassisches Verifier-Review, stattdessen Doku-Recherche plus praktischer Abnahmetest mit Fixtures (siehe oben). Der Abnahmetest widerlegte eine Doku-Ableitung des Rechercheagenten (`./` löse zu `~/.claude` auf); die übrigen Doku-Fakten (Geltung in jedem Modus, Wirkzeitpunkt, Pfadtabelle, `bypassPermissions`) wurden dadurch nicht widerlegt.

## Archivkopie

Archivordner: `archiv/2026-09-20-token-spar-policies/`.

| Datei | Vorher (Bytes / SHA-256) | Nachher (Bytes / SHA-256) | Archivpfad |
|---|---|---|---|
| `skills/second-brain/SKILL.md` | 3.772 / `6a5d1d8b…9cc78f` | 4.118 / `c0332af8…9b1f12` | `archiv/2026-09-20-token-spar-policies/skills/second-brain/SKILL.md` |
| `Bastis Schatz/CLAUDE.md` (Vault) | 1.202 / `ecd80be0…bc534f` | 1.257 / `11cac337…3167e4` | `archiv/2026-09-20-token-spar-policies/vault/CLAUDE.md` |
| `agents/executor.md` | 3.033 / `515103ae…599706` | 3.287 / `dceda539…9aa9ad` | `archiv/2026-09-20-token-spar-policies/agents/executor.md` |
| `agents/verifier.md` | 1.829 / `837cec89…603553` | 1.970 / `f47aafe5…21dfe1` | `archiv/2026-09-20-token-spar-policies/agents/verifier.md` |
| `CLAUDE.md` | 6.157 / `c0bcab77…a357be` | 6.360 / `adde5a90…0931ed` | `archiv/2026-09-20-token-spar-policies/CLAUDE.md` |
| `settings.json` | 4.612 / `9717193d…dbd996a` | 4.947 / `d28f181e…9ea839` | `archiv/2026-09-20-token-spar-policies/settings.json` |

Alle Bytes- und SHA-256-Werte gegen die Archivkopien (Vorher) bzw. die Live-Dateien (Nachher)
nachgerechnet (`wc -c`, `sha256sum`); keine Abweichung zu den im Auftrag genannten Werten.

## Offen

1. Nachmessung in zwei bis drei Wochen mit `context_fill_analysis.py`: Anteil der Läufe über 200K (Basis 21 Prozent, 59 Prozent des Input-Verbrauchs), Anteil wiederholter Reads (13,9 Prozent), Voll-Read-Anteil (74 Prozent), Reads von `index.md` (55 in 60 Tagen). Dazu das TTL-Experiment im wlh-Projekt ab 04.10. Aufruf und Kennzahlen: `messung/README.md`.
2. Messskripte ins Repo (Einschätzung 5.8): erledigt. Ordnername `messung/` von Sebastian freigegeben; die Skripte liegen jetzt unter `messung/` mit README und der Basislinie `context_fill_analysis_output_2026-09-20.txt`. Das Hauptskript hat ein Datumsfenster (`--since`, `--until`, `--out`); die drei Skript-Folgepunkte (Code-Endungen in Abschnitt B, Hook-Quoten erst ab 12.09., Junk-Erkennung auf Pfadsegmente) sind darin umgesetzt. `messung/` hält zwei Basislinien: `context_fill_analysis_output_2026-09-20.txt` (Originalskript, 11:58, in der Einschätzung zitiert) und `context_fill_analysis_basislinie_2026-09-20.txt` (Repo-Skript mit erweiterten Endungs- und Junk-Definitionen über dasselbe Fenster); die Nachmessung vergleicht gegen die zweite.
3. Deny-Liste, Reichweite: `./`-Muster decken Dateien außerhalb des Arbeitsverzeichnisses nicht ab (Fall `vitest-full.log` im wlh-Projekt aus einer anderen Session); nicht abgedeckt ist auch `Plan Legacy code Migration/_test-workspace/graphify-out` (verschachtelt). Absolute `//`-Muster wären die Erweiterung, nicht freigegeben.
4. Beobachtung: Beim Read-Tool in `dist/` kam die Deny-Meldung, nicht die Hook-Meldung des `read-gate`; die README-Aussage „der Hook läuft vor der Permission-Prüfung“ (Abschnitt Bewusste Dopplungen, git-push-Deny) gilt damit zumindest für Read-Deny-Regeln nicht oder nicht in dieser Reihenfolge. Prüfen, ob sie für Bash-Deny weiter stimmt.
5. Platzierung der Paketgrößen-Regel in CLAUDE.md Zeile 40 (Verifier-Fund): entschieden. Sebastian hat am 20.09. entschieden, dass die Regel in Zeile 40 bleibt.
6. `inventar.md`: Fundort-Zeilennummern der Bestandseinträge und Tabellenköpfe (Bytes, Stand) seit Paket A veraltet; Abgleich als eigenes Paket.
7. Paket C (ESLint-Logik aus `post-edit.sh` ins Konfigurator-Repo) bleibt offen.
8. Doku-Umbau „Plan Legacy code Migration“ erst nach der Nachmessung.
9. Der Punkt `omitClaudeMd` aus `umsetzung-2026-09-20.md` ist durch Einschätzung 5.6 entschieden (nicht setzen) und damit geschlossen.
10. Worktree `zealous-napier-a3bed1` enthält die Einschätzung und das Projektinventar weiterhin als nicht committete Kopien; in diesem Branch sind sie committet (`4a31fb4`). Dort löschen oder Worktree aufräumen.
