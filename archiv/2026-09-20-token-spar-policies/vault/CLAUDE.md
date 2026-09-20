# CLAUDE.md - Mein Second Brain (Obsidian Vault)
Claude Code verwaltet dieses Vault vollständig nach dem Karpathy-Prinzip.

## Struktur
- raw/      Quellmaterial, immutable. Du liest nur, änderst nie.
- wiki/     Deine Seiten. Hier schreibst, aktualisierst und verlinkst du.
- index.md  Katalog aller Seiten. Lies ihn IMMER zuerst, um die richtige Seite zu finden.
- log.md    Append-only, chronologisch.

## Drei Operationen
- Ingest: neue Quelle lesen, Wiki-Seite(n) bauen, index.md + log.md aktualisieren.
- Query: index.md lesen, passende Seite finden, Antwort mit Quellenbezug geben.
- Lint: Widersprüche, veraltete Infos und tote Links finden.

## Regeln
- Deutsch schreiben, Tech-Begriffe englisch lassen.
- Lieber viele kleine Seiten als wenige große.
- Wiki-Seiten haben YAML-Frontmatter (title, tags, sources, created, updated) und [[links]].
- Jede Behauptung muss auf eine Quelle in raw/ zurückführbar sein. Bei Unsicherheit: fragen statt raten.
- Projekt-Namespacing: pro Projekt `raw/<projekt>/`-Unterordner, Wiki-Präfix `<projekt>-`, Tag `#projekt/<name>`. Querverweise zwischen Projekten nur als Klartext, nie als [[Link]] — so bleiben die Projekt-Cluster im Graphen getrennt.
