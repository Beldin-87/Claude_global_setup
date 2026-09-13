# Sebastians Agent-Setup (globales Steering)

Vokabular für die Arbeit mit Claude-Code-Agents über alle Projekte hinweg. Wird nicht automatisch geladen; Pointer-Ziel aus CLAUDE.md. Projekt-Domänen haben eigene CONTEXT.md-Dateien (kinetic-app, wlh-preiskalkulation-app, Repo SA-Analyse).

## Rollen & Arbeitsteilung

**Hauptmodell**:
Das stärkste verfügbare Modell (Fable; bei Limit Opus) in der Rolle Planer und Prüfer. Denkt, brieft und urteilt — implementiert nicht.
_Avoid_: Orchestrator, Main-Agent

**Hauptsession**:
Die Session, in der der Nutzer arbeitet und das Hauptmodell plant, brieft und prüft. Subagents laufen in eigenen Sessions mit dem Briefing als Auftrag — unabhängig davon, auf welchem Modell.
_Avoid_: Hauptloop als Synonym für die Session, Main-Session

**Executor**:
Subagent, der ein gebrieftes Arbeitspaket umsetzt (Opus bei unklarem Weg, Sonnet als Default, Fable als Eskalation, wenn eine Opus-Runde an kritischer Kernlogik gescheitert ist); dahinter steht der Agent `executor`, dessen Modell beim Aufruf gesetzt wird.
_Avoid_: Worker, Coder-Agent

**Verifier**:
Subagent mit frischem Kontext, der ein Ergebnis gegen Spezifikation bzw. Akzeptanzkriterien prüft und alles meldet (mit Confidence und Severity). Fable prüft kritische Hauptmodell-Arbeit (Pläne, Architektur-Entscheidungen, Specs, lange Läufe), Sonnet übernimmt die mechanische Erst-Prüfung von Executor-Ergebnissen; dahinter steht der Agent `verifier`, dessen Modell beim Aufruf gesetzt wird. Das finale Urteil bleibt beim Hauptmodell.
_Avoid_: Reviewer, Checker

**Briefing**:
Vollständiger Arbeitsauftrag im ersten Anlauf: Auftrag, Wozu, Constraints, Akzeptanzkriterien.
_Avoid_: Prompt, Task-Beschreibung

**Briefing-Baustein**:
Fester, positiv formulierter Textblock (Scope-Erwartung, Umgang mit Dissens, Blockade, Mehrdeutigkeit und offenen Fragen, Folgepunkte, Test-Disziplin, Längen-Erwartung, Akzeptanzkriterien-Pflicht, Turn-Ende erst bei erfüllten Kriterien), der im Body von `agents/executor.md` steht und beim Lauf des Executors mitgeladen wird.
_Avoid_: den Baustein ins Briefing kopieren

**Akzeptanzkriterien**:
Vor der Delegation festgehaltene, messbare Merkmale, an denen fertig UND korrekt erkennbar ist.
_Avoid_: Definition of Done (informell)

**Traceability-Datei**:
Pro Coding-Projekt eine `TRACEABILITY.md` im Repo-Root, die je Ticket-ID in einer Zeile festhält, in welchen Codeteilen das Ticket umgesetzt wurde, dazu ein Halbsatz zum Was; wird als Teil jedes Ticket-Arbeitspakets aktualisiert.
_Avoid_: Ticket-Zuordnung nur über Commit-Historie

**CODING_STANDARDS-Datei**:
Pro Coding-Projekt ein Dokument im Repo-Root (`CODING_STANDARDS.md`), das festhält, wie Code geschrieben, im Code dokumentiert und getestet wird — Testformat und Testbericht-Format gehören hierhin. Die Standards-Achse von `matt-code-review` prüft gegen genau diese dokumentierten Repo-Standards; sie überstimmen die eingebaute Smell-Baseline des Skills, die ohne Dokument allein gilt. Etablierung je Repo ist der Folgeschritt aus Schritt 8 des Steering-Plans.
_Avoid_: Standards nur im Briefing oder mündlich

**Testbericht**:
Executor-Meldung nach einem Testlauf: welche Tests liefen, das Grün/Rot-Ergebnis und der Abgleich gegen die Akzeptanzkriterien des Briefings. Das konkrete Format je Repo steht in der CODING_STANDARDS-Datei.
_Avoid_: „Tests laufen“ ohne Nennung der Tests und des Kriterien-Abgleichs

## Steering & Kontext-Ökonomie

**Steering-Ebene**:
Eine der fünf Stellschrauben, über die Agent-Verhalten sessionübergreifend gelenkt wird: CLAUDE.md, Skills, Memory, Permissions, Token-Management (nach Matt Pocock).

**Pointer**:
Einzeiliger Verweis auf ausgelagertes Material (Skill, Datei), das nur bei Bedarf in den Kontext geladen wird.
_Avoid_: Inline-Runbook, einkopierter Styleguide

**Agent-Definition**:
Markdown-Datei unter `~/.claude/agents/`, deren Frontmatter den Agenten benennt (Name, Beschreibung, Default-Modell, Tool-Grenzen) und deren Body sein Systemprompt wird. Sie wird nur beim Lauf dieses Agenten geladen und ist damit der Wohnort für Regeln, die nur Ausführende brauchen. Der Body ersetzt den Claude-Code-Standardprompt des Subagenten, aber nicht vollständig: Identitätszeile, Sicherheitsteil und die CLAUDE.md-Hierarchie bleiben erhalten; verloren geht der eingebaute Hinweis auf parallele Tool-Calls, den beide Definitionen deshalb selbst führen.
_Avoid_: Regeln nur für Ausführende in der immer geladenen CLAUDE.md ablegen

**Smart Zone / Dumb Zone**:
Früher Session-Bereich mit hoher Befolgungsqualität vs. abfallende Qualität bei wachsendem Kontext — unabhängig vom Kontextfenster-Limit. Geplant wird um die Smart Zone, nicht um das Fenster.

**Handoff**:
Strukturiertes Übergabedokument, das ein Session-Thema abschließt und eine frische Session startfähig macht; enthält den Vault-Ingest dauerhafter Erkenntnisse.
_Avoid_: einfach neue Session ohne Übergabe

**Sediment**:
Veraltete Schichten in immer geladenen Dokumenten (CLAUDE.md, Memory, Skills), die sich ansammeln, weil Hinzufügen sicher wirkt und Löschen riskant.

**Pruning**:
Bewusstes, regelmäßiges Entfernen von Sediment; jede Regel hat genau eine Quelle.
_Avoid_: Anhäufen „zur Sicherheit“
