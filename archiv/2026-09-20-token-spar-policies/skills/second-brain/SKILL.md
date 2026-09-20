---
name: second-brain
description: 'Pflege von Sebastians Obsidian Second Brain (Vault „Bastis Schatz“). Use when: Session-Erkenntnisse ins Vault einpflegen („ins Second Brain“, „ins Vault“, via /handoff), oder Vorwissen aus dem Vault abrufen. Kapselt Ingest und Query-first über den Katalog.'
argument-hint: "ingest | query <Frage> (ohne Argument: fragen, was gebraucht wird)"
---

# Second Brain — Ingest & Query

Sebastians Claude-verwaltetes Obsidian-Vault: `C:\GitHub\Projekte\Bastis Obsidian Vault\Bastis Schatz`.
Die **Betriebsregeln stehen in der Vault-eigenen `CLAUDE.md`** (Karpathy-Prinzip) — zuerst lesen, sie sind die Autorität. Dieser Skill beschreibt nur die Operationen darüber hinaus.

## Grundwissen (gilt für Ingest und Query)

- Struktur: `raw/` immutable Quellen (nur lesen) · `wiki/` kuratierte Seiten · `index.md` Katalog (immer zuerst lesen) · `log.md` append-only.
- Konventionen: raw-Dateien enden auf `.source.md` (eindeutige Wikilink-Basenamen); pro Projekt Unterordner `raw/<projekt>/`, wiki-Prefix `<projekt>-`, Tag `#projekt/<name>`; Wiki-Seiten haben YAML-Frontmatter (title, tags, sources, created, updated), `[[links]]` und Fußnoten-Zitate auf die raw-Quelle.
- **Sensibles bleibt draußen:** nie Rohdaten mit Geschäfts-/Preisinformationen (z. B. `price_list.json`-Inhalte) ins Vault — nur die *Erkenntnisse darüber*. Im Zweifel fragen.

## Operation 1 — Ingest (läuft im Handoff-Ritual)

`/handoff` stößt diese Mechanik am Sessionende an — als Hintergrund-`executor`, parallel zum Übergabedokument, mit den Zielpfaden aus dem Briefing —, sobald dauerhafte Erkenntnisse entstanden sind; das ist der **einzige Schreibpfad ins Vault**. Ein direkter Nutzer-Auftrag („pflege das ins Second Brain ein“) durchläuft dieselben Schritte 1–4, dann aber in der laufenden Session und mit selbst gewählten Zielpfaden.

1. Zielpfade: Nennt das Briefing raw- und Wiki-Pfad, gelten sie wörtlich — `index.md` liest du dann nur, um den Katalog-Eintrag richtig einzuordnen. Ohne vorgegebene Pfade: `index.md` lesen, bei passender Seite aktualisieren statt neu anlegen (`updated:` setzen).
2. Quellmaterial als Snapshot nach `raw/<projekt>/<thema>.source.md` (immutable; bestehende raw-Dateien nie ändern).
3. Destillierte Wiki-Seite(n) in `wiki/` bauen — lieber mehrere kleine als eine große; Frontmatter, `[[links]]` (mind. zum Projekt-Hub), Fußnoten auf die raw-Quelle.
4. `index.md` (Eintrag im Projekt-Abschnitt) + `log.md` (neuer append-only Eintrag mit Datum und Operation) nachziehen.

## Operation 2 — Query first (Session-Start / Vorwissen)

Wenn eine Session altes Projektwissen braucht: **nicht** Dateien in den Kontext laden, sondern gezielt über den Katalog gehen:

1. `index.md` lesen — bei bekanntem Projekt nur den Projektabschnitt, z. B. per grep nach dem Präfix (Beispiel: `grep -i "^wlh-" index.md` für das Projekt `wlh`).
2. Die eine passende Wiki-Seite aus dem Katalog-Eintrag öffnen.
3. Aus dieser Seite antworten, mit Pfadangabe zitieren.

Nie das ganze Vault laden, nie `raw/` durchsuchen.

## Ausgemustert: Abgleich (22.08.2026)

Der frühere Abgleich Memory ↔ Vault ist ausgemustert: Auto-Memory ist seit 12.08.2026 global aus, Projekt-Sessions erzeugen keine Memory-Notizen mehr. Der letzte Abgleich lief am 22.08.2026 (log.md-Eintrag im Vault). Die fünf alten Projekt-Memory-Ordner unter `~/.claude/projects/<projekt>/memory/` bleiben als inertes Archiv liegen, ohne weitere Rolle in diesem Skill.

## Wartung

Der Wochen-Task `second-brain-wartung` ist seit 14.09.2026 deaktiviert (Vault-Graph abgeschaltet, Protokoll `entscheidung-graphify-2026-09-14.md` im Repo Claude_global_setup). Pflege des Vaults geschieht ausschließlich über Operation 1 beim Handoff.
