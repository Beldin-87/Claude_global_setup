"""
Analyse von Claude-Code-Transkripten: WOMIT wird der Kontext gefuellt?
(Tool-Ergebnisse nach Tool-Typ, Assistant-Text/Thinking, Tool-Use-Inputs,
User-Text; Read-Tiefe; Kommandoausgaben; Hook-Rueckmeldungen; je Projekt;
grosse Kontexte.)

Uebernimmt Fundort/Discovery/Cutoff-Mechanik im Grundfall 1:1 aus
cache_ttl_analysis.py (gleicher Ordner, gleiches 60-Tage-Fenster als
Default, gleiche Sub-/Hauptsession-Unterscheidung ueber den Pfadanteil
"\\subagents\\"). Mit --since/--until laesst sich das Fenster ueber die
Datei-mtime frei setzen (siehe --help); das ersetzt dann den 60-Tage-Default.

Liest NUR, streamt JSONL zeilenweise. Der Report enthaelt keine
Transkriptinhalte -- nur Pfade, Kommando-Praefixe (<=80 Zeichen) und Zahlen.

Token-Schaetzung durchgaengig als Zeichen / 4 (Naeherung, nicht exakt).
"""

import argparse
import glob
import json
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

BASE = r"C:\Users\szieg\.claude\projects"
CUTOFF_DAYS = 60

# --- Abschnitt D/G6: Hooks existieren erst ab diesem Datum (Datei-mtime) ---
HOOKS_ACTIVE_SINCE = "2026-09-12"

# --- Tool-Kategorien (A) -----------------------------------------------
STANDARD_TOOLS = {
    "Read", "Grep", "Glob", "Bash", "PowerShell", "Edit", "Write",
    "Agent", "SendMessage", "WebFetch", "WebSearch",
}

# Gemeinsame Code-Endungen-Liste fuer alle Stellen, die Dateiendungen als
# "Code" einordnen (Abschnitt B: Verteilung nach Dateiendung; Abschnitt G3/G5:
# Code-Reads) -- eine Konstante, an dieser einen Stelle definiert. Markdown
# (.md) bleibt eigenstaendige Kategorie und ist absichtlich nicht enthalten.
CODE_EXTS = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".py", ".html", ".css",
    ".json", ".sh", ".ps1", ".kt", ".java", ".go", ".rs", ".c", ".h",
    ".cpp", ".sql", ".yaml", ".yml", ".toml",
}

READ_EXT_BUCKETS = CODE_EXTS | {".md", ".jsonl"}

# --- Hook-Suchmuster (D), entnommen aus C:\Users\szieg\.claude\hooks\*.sh ---
# (marker_key, marker_text, capture_cap_chars)
HOOK_MARKERS = [
    ("read_gate", "Lese-Schranke:", 1200),          # read-gate.sh (Junk-Ordner, Lockfile, Groesse)
    ("agent_gate", "Agenten-Schranke:", 1200),       # agent-gate.sh
    ("eslint", "ESLint meldet Probleme", 6000),      # post-edit.sh
    ("check_eol", "Zeilenenden ge\u00e4ndert:", 1200),  # check-eol.sh
    ("guardrail_block", "Guardrail: Befehl blockiert", 1200),  # guard-destructive.sh
    ("guardrail_no_jq", "Guardrail: jq nicht gefunden", 1200),  # guard-destructive.sh (jq fehlt)
]

# --- Abschnitt G: Kommandoklassen, Junk-Segmente ---------------------------
# (siehe Auftrag Abschnitt G3/G4/G6; die Kommando-Klassifikation ist eine
# Naeherung auf Basis erkennbarer Muster im Kommandotext, keine vollstaendige
# Shell-Syntaxanalyse. CODE_EXTS fuer G3/G5 ist oben gemeinsam mit Abschnitt B
# definiert.)

JUNK_SEGMENTS_G4 = {"node_modules", "dist", "build", ".git", "graphify-out",
                     ".wrangler", "coverage", "__pycache__", ".venv", "venv"}

# Lockfile-Namen (kleingeschrieben, fuer Endungsvergleich): ein Pfad-Token,
# das auf einen dieser Namen endet, gilt ebenfalls als Junk-Treffer (G4/G6).
LOCKFILE_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock",
                   "uv.lock", "poetry.lock", "cargo.lock"}

CMD_CLASS_PRIORITY = ["tests", "build", "datei-lesen", "git", "suche", "python-inline"]

# Gleicher ESLint-Marker wie in Abschnitt D (HOOK_MARKERS), aber mit 60.000
# statt 6.000 Zeichen Kappung -- fuer G6 (echter Umfang unter der D-Kappung).
HOOK_MARKERS_G6 = [
    ("eslint_g6", "ESLint meldet Probleme", 60_000),
]


def classify_segment(seg):
    """Ordnet ein einzelnes Kommando-Segment (nach Trennung an &&/;/|) einer
    Klasse aus Abschnitt G4 zu. Nur Praefix-/Musterabgleich."""
    s = seg.strip()
    if not s:
        return "sonstige"
    low = s.lower()
    if re.match(r'^(npx\s+)?vitest\b', low):
        return "tests"
    if re.match(r'^npm\s+test\b', low):
        return "tests"
    if re.match(r'^npm\s+run\s+test', low):
        return "tests"
    if re.match(r'^(python3?|py)\s+-m\s+pytest\b', low):
        return "tests"
    if re.match(r'^pytest\b', low):
        return "tests"
    if re.match(r'^node\s+--test\b', low):
        return "tests"
    if re.match(r'^npm\s+run\s+build', low):
        return "build"
    if re.match(r'^(npx\s+)?vite\s+build\b', low):
        return "build"
    if re.match(r'^wrangler\b', low):
        return "build"
    if re.match(r'^(npx\s+)?tsc\b', low):
        return "build"
    if re.match(r'^cat\b', low):
        return "datei-lesen"
    if re.match(r'^head\b', low):
        return "datei-lesen"
    if re.match(r'^tail\b', low):
        return "datei-lesen"
    if re.match(r'^sed\s+-n\b', low):
        return "datei-lesen"
    if re.match(r'^type\b', low):
        return "datei-lesen"
    if re.match(r'^get-content\b', low):
        return "datei-lesen"
    if re.match(r'^less\b', low):
        return "datei-lesen"
    if re.match(r'^more\b', low):
        return "datei-lesen"
    if re.match(r'^git\b', low):
        return "git"
    if re.match(r'^(grep|rg)\b', low):
        return "suche"
    if re.match(r'^find\b', low):
        return "suche"
    if re.match(r'^ls\b', low):
        return "suche"
    if re.match(r'^dir\b', low):
        return "suche"
    if re.match(r'^get-childitem\b', low):
        return "suche"
    if re.match(r'^wc\b', low):
        return "suche"
    if re.match(r'^tree\b', low):
        return "suche"
    if re.match(r'^(python3?|py)\b', low) and ("<<" in s or re.search(r'(^|\s)-c(\s|$)', s)):
        return "python-inline"
    return "sonstige"


_CD_PREFIX_RE = re.compile(r'^cd\s+(?:"[^"]*"|\'[^\']*\'|\S+)\s*&&\s*', re.IGNORECASE)
_EXPORT_PREFIX_RE = re.compile(r'^export\s+\S+\s*;\s*', re.IGNORECASE)
_CMD_SPLIT_RE = re.compile(r'&&|\|\||\||;')


def classify_command(cmd_full):
    """Klassifiziert einen vollstaendigen Bash-/PowerShell-Kommandotext
    (Abschnitt G4). Entfernt zuerst fuehrende cd "..." &&- und export ...;-
    Praefixe. Bei Ketten (&&/;/|) gewinnt die erste erkannte Klasse in der
    Prioritaet tests > build > datei-lesen > git > suche > python-inline."""
    s = (cmd_full or "").strip()
    while True:
        m = _CD_PREFIX_RE.match(s)
        if m:
            s = s[m.end():]
            continue
        m2 = _EXPORT_PREFIX_RE.match(s)
        if m2:
            s = s[m2.end():]
            continue
        break
    segments = _CMD_SPLIT_RE.split(s)
    classes_found = {classify_segment(seg) for seg in segments}
    for prio in CMD_CLASS_PRIORITY:
        if prio in classes_found:
            return prio
    return "sonstige"


_JUNK_TOKEN_SPLIT_RE = re.compile(r'[\s"\'=]+')
_JUNK_PATH_SEP_RE = re.compile(r'[\\/]+')


def segments_hit(path_str):
    """Gemeinsame Segment-Logik fuer Junk-/.log-/Lockfile-Erkennung, genutzt von
    cmd_has_junk_or_log() (je Kommando-Token) und path_has_junk_or_log() (direkt
    auf einem normalisierten Read-Dateipfad) -- Doctests liegen in
    cmd_has_junk_or_log(), da alle geforderten Beispiele dort als Kommandos
    formuliert sind; diese Funktion traegt nur die geteilte Logik.

    An '/' oder '\\' getrennte ORDNER-Segmente zaehlen nur, wenn `path_str`
    ueberhaupt einen Pfadtrenner enthaelt (sonst ist es ein blosses Wort, kein
    Pfad); sie muessen dann EXAKT einem Namen aus JUNK_SEGMENTS_G4 entsprechen
    oder mit 'dist-' beginnen. Das LETZTE Segment (der Dateiname, auch ganz
    ohne Trenner moeglich) trifft zusaetzlich IMMER, wenn es EXAKT einem Namen
    aus LOCKFILE_NAMES entspricht oder auf '.log' endet."""
    if not path_str:
        return False
    low = path_str.lower()
    segs = [s for s in _JUNK_PATH_SEP_RE.split(low) if s]
    if not segs:
        return False
    if _JUNK_PATH_SEP_RE.search(low):
        if any(seg in JUNK_SEGMENTS_G4 or seg.startswith("dist-") for seg in segs):
            return True
    last = segs[-1]
    return last in LOCKFILE_NAMES or last.endswith(".log")


def cmd_has_junk_or_log(cmd_full):
    r"""Zerlegt den Kommandotext in Pfad-Tokens (getrennt an Leerzeichen,
    Anfuehrungszeichen und '=') statt einer reinen Substring-Suche im
    Volltext und prueft jedes Token mit segments_hit() (siehe dort fuer die
    genaue Segment-Regel). Ein blosses Wort ohne Pfadtrenner ist kein Pfad:
    'ls dist' und 'cat dist-report.json' treffen NICHT, weil 'dist' bzw.
    'dist-report.json' dort blosse Argumente ohne Trenner sind; sobald ein
    Trenner dazukommt, wird daraus ein Pfad -- 'cat dist-angebot/x.js' und
    'cat ./dist/x.js' treffen. Ein Lockfile-Treffer braucht ein EXAKTES
    letztes Segment ('cat sub/package-lock.json' und ein blosses
    'package-lock.json' treffen, 'cat custom-package-lock.json' NICHT).

    >>> cmd_has_junk_or_log('cat dist/app.js')
    True
    >>> cmd_has_junk_or_log('head -5 ./build/x.txt')
    True
    >>> cmd_has_junk_or_log('sed -n 1,3p "C:\\p\\node_modules\\a\\index.d.ts"')
    True
    >>> cmd_has_junk_or_log('tail vitest-full.log')
    True
    >>> cmd_has_junk_or_log('cat distribution.md')
    False
    >>> cmd_has_junk_or_log('grep -r build .')
    False
    >>> cmd_has_junk_or_log('echo dist')
    False
    >>> cmd_has_junk_or_log('cat docs/builder.md')
    False
    >>> cmd_has_junk_or_log('ls dist')
    False
    >>> cmd_has_junk_or_log('cat dist-report.json')
    False
    >>> cmd_has_junk_or_log('cat dist-angebot/x.js')
    True
    >>> cmd_has_junk_or_log('cat ./dist/x.js')
    True
    >>> cmd_has_junk_or_log('cat custom-package-lock.json')
    False
    >>> cmd_has_junk_or_log('cat sub/package-lock.json')
    True
    """
    tokens = [t for t in _JUNK_TOKEN_SPLIT_RE.split(cmd_full or "") if t]
    return any(segments_hit(tok) for tok in tokens)


def path_has_junk_or_log(norm_file_path):
    """Wie cmd_has_junk_or_log, aber direkt ueber segments_hit() auf dem
    bereits normalisierten (lowercased, an '\\' getrennten) Dateipfad eines
    Read-Aufrufs -- dieselbe Segment-/Lockfile-/.log-/dist-*-Logik wie dort."""
    return segments_hit(norm_file_path)


def g2_bucket(name):
    """Tool-Bucket fuer Abschnitt G2 (feiner als tool_category: MultiEdit
    bleibt eigenstaendig statt in 'sonstige' zu verschwinden)."""
    if name in ("Write", "Edit", "MultiEdit", "Bash", "PowerShell", "Agent", "SendMessage"):
        return name
    return "sonstige"


def parse_ts(ts_raw):
    if not ts_raw:
        return None
    try:
        return datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    except Exception:
        return None


def hooks_active_since_ts():
    """Epoch-Sekunden (lokale Zeit, wie os.path.getmtime()) ab HOOKS_ACTIVE_SINCE 00:00."""
    return datetime.strptime(HOOKS_ACTIVE_SINCE, "%Y-%m-%d").timestamp()


def discover_files(since_dt=None, until_dt=None):
    """since_dt/until_dt (datetime oder None): filtert per Datei-mtime, until exklusiv.
    Ohne beide Angaben: Default-Verhalten wie bisher (letzte CUTOFF_DAYS Tage, kein
    Enddatum). Sobald mindestens eine der beiden Angaben gesetzt ist, ersetzt das
    Fenster [since_dt, until_dt) das CUTOFF_DAYS-Default vollstaendig."""
    sub_files = glob.glob(os.path.join(BASE, "**", "subagents", "agent-*.jsonl"), recursive=True)
    all_jsonl = glob.glob(os.path.join(BASE, "**", "*.jsonl"), recursive=True)
    sep = os.sep + "subagents" + os.sep
    main_files = [f for f in all_jsonl if sep not in f]
    if since_dt is None and until_dt is None:
        since_ts = time.time() - CUTOFF_DAYS * 86400
        until_ts = float("inf")
    else:
        since_ts = since_dt.timestamp() if since_dt is not None else 0.0
        until_ts = until_dt.timestamp() if until_dt is not None else float("inf")
    sub_recent = [f for f in sub_files if since_ts <= os.path.getmtime(f) < until_ts]
    main_recent = [f for f in main_files if since_ts <= os.path.getmtime(f) < until_ts]
    skipped_sub = len(sub_files) - len(sub_recent)
    skipped_main = len(main_files) - len(main_recent)
    return sub_recent, main_recent, skipped_sub, skipped_main


def tool_category(name):
    if not name:
        return "sonstige"
    if name in STANDARD_TOOLS:
        return name
    if name.startswith("mcp__"):
        parts = name.split("__")
        if len(parts) >= 2:
            return "mcp__" + parts[1]
        return name
    return "sonstige"


def ext_bucket(file_path):
    if not file_path:
        return "sonstige"
    ext = os.path.splitext(file_path)[1].lower()
    return ext if ext in READ_EXT_BUCKETS else "sonstige"


def norm_path(p):
    if not p:
        return p
    return p.replace("/", "\\").lower()


def tool_result_text_and_sizes(content):
    """Vereinfachte, robuste Variante: liefert (extracted_text_or_None, text_chars, raw_chars)."""
    if isinstance(content, str):
        return content, len(content), len(content)
    if isinstance(content, list):
        parts = []
        text_chars = 0
        raw_chars = 0
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text":
                t = c.get("text") or ""
                parts.append(t)
                text_chars += len(t)
                raw_chars += len(t)
            else:
                try:
                    raw_chars += len(json.dumps(c, ensure_ascii=False))
                except Exception:
                    pass
        return ("".join(parts) if parts else None), text_chars, raw_chars
    return None, 0, 0


def scan_hooks(text, message_kind, sink, markers=HOOK_MARKERS):
    """Sucht Hook-Marker in text, haengt Treffer (key, message_kind, chars) an sink an."""
    if not text:
        return
    for key, marker, cap in markers:
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx == -1:
                break
            window_end = min(len(text), idx + cap)
            nl2 = text.find("\n\n", idx, window_end)
            end = nl2 if nl2 != -1 else window_end
            msg_len = end - idx
            sink.append((key, message_kind, msg_len))
            start = idx + len(marker)


def scan_hooks_both(text, message_kind, sink, sink_g6):
    """Wie scan_hooks, scannt aber zusaetzlich mit dem 60k-Cap-Markersatz
    aus G6 in denselben Text (fuer Abschnitt G6, ohne Abschnitt D anzutasten)."""
    scan_hooks(text, message_kind, sink, HOOK_MARKERS)
    scan_hooks(text, message_kind, sink_g6, HOOK_MARKERS_G6)


def process_file(path, is_subagent):
    """Ein Durchlauf ueber die Datei. Liefert ein Ergebnis-Dict oder None bei Lesefehler.
    Jede JSONL-Zeile traegt nur EIGENE (nicht kumulative) Content-Bloecke, auch wenn
    mehrere Zeilen dieselbe assistant message.id teilen (verifiziert an Rohdaten:
    unterschiedliche tool_use-IDs je Zeile) -- daher wird jede Zeile einzeln gezaehlt,
    kein Dedup noetig fuer die Zeichen-Summen."""

    tool_result_chars = Counter()      # tool_category -> chars (Kategorie A.1)
    assistant_text_chars = 0           # Kategorie A.2 (text + thinking in assistant)
    tool_use_input_chars = Counter()   # tool_category -> chars (Kategorie A.3)
    user_text_chars = 0                # Kategorie A.4 (reiner User-Text, ohne tool_result)
    total_content_chars = 0            # Summenprobe: alle Bloecke in user/assistant Content
    nontext_by_tool = Counter()        # tool_category -> Zeichen aus Bild/Dokument-Bloecken in
                                        # tool_result (raw, zaehlt in total_content_chars, aber in
                                        # keiner der 4 A-Kategorien -- Hauptquelle der Summenprobe-Luecke)
    top_level_other_chars = 0          # Bild/Dokument direkt im Content (ausserhalb tool_result), selten

    hook_hits = []  # (key, message_kind, chars)
    hook_hits_g6 = []  # dito, mit 60k-Cap-Markersatz (nur fuer Abschnitt G6)

    read_records = []   # (ext, has_offset_or_limit(bool), chars, lines, norm_file_path)
    file_read_chars = defaultdict(int)   # norm_path -> gesamt gelesene Zeichen in dieser Datei (fuer Wiederholungs-Anteil)
    file_read_count = defaultdict(int)

    cmd_records = []   # (tool_category in {Bash,PowerShell}, cmd_prefix80, chars)
    cmd_class_records = []  # (klasse aus G4, chars, junk_or_log(bool)) -- fuer Abschnitt G4/G5/G6

    tool_id_to_call = {}   # tool_use_id -> {"name":..., "cat":..., "input":...}

    # --- Abschnitt G2: Tool-Use-Inputs nach Rohnamen + Write/Edit-Details ---
    tool_use_input_by_rawname = Counter()   # Rohname (nicht Kategorie) -> Zeichen
    write_records = []          # (norm_file_path, content_chars) in Aufruf-Reihenfolge
    write_content_lens = []     # content-Laenge je Write-Aufruf
    edit_new_string_lens = []   # new_string-Laenge je Edit-Aufruf

    # --- Abschnitt G1: Input-Verbrauch ueber ALLE Assistant-Turns ----------
    sum_usage_input_total = 0       # Summe (it+cr+cc) je EINDEUTIGEM message.id
    sum_usage_cache_creation = 0    # Summe cc je EINDEUTIGEM message.id

    assistant_msg_ids = set()
    last_end_usage = None  # (input_tokens, cache_read, cache_creation) des letzten Assistant-Turns
    project_cwd = None
    first_ts = None

    total_lines = 0
    json_errors = 0

    try:
        fh = open(path, "r", encoding="utf-8", errors="replace")
    except Exception:
        return None

    with fh:
        for raw_line in fh:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            total_lines += 1
            try:
                o = json.loads(raw_line)
            except Exception:
                json_errors += 1
                continue

            if project_cwd is None:
                cwd = o.get("cwd")
                if cwd:
                    project_cwd = cwd

            t = o.get("type")

            if t not in ("user", "assistant", "system"):
                continue

            if first_ts is None:
                ts = parse_ts(o.get("timestamp"))
                if ts is not None:
                    first_ts = ts

            if t == "system":
                # Hook-Feedback taucht in den bisher beobachteten Daten nicht in
                # system-Zeilen auf (hookAdditionalContext durchgehend leer),
                # der Pfad bleibt defensiv erhalten falls sich das aendert.
                txt = o.get("content")
                if isinstance(txt, str):
                    scan_hooks_both(txt, "system", hook_hits, hook_hits_g6)
                continue

            msg = o.get("message") or {}
            content = msg.get("content")

            if t == "assistant":
                mid = msg.get("id")
                # Verifiziert an Rohdaten: usage wiederholt sich IDENTISCH auf allen
                # JSONL-Zeilen, die dieselbe message.id teilen (mehrteilige Antworten).
                # last_end_usage ("letzte Zeile gewinnt") bleibt dadurch unveraendert,
                # aber fuer G1 (Summe ueber alle Turns) muss je message.id genau
                # einmal gezaehlt werden -- daher die Neuheit-Pruefung vor dem Add.
                is_new_mid = bool(mid) and (mid not in assistant_msg_ids)
                if mid:
                    assistant_msg_ids.add(mid)
                usage = msg.get("usage")
                if usage:
                    it = usage.get("input_tokens") or 0
                    cr = usage.get("cache_read_input_tokens") or 0
                    cc = usage.get("cache_creation_input_tokens") or 0
                    last_end_usage = (it, cr, cc)
                    if is_new_mid or not mid:
                        sum_usage_input_total += (it + cr + cc)
                        sum_usage_cache_creation += cc

            if isinstance(content, str):
                n = len(content)
                total_content_chars += n
                if t == "assistant":
                    assistant_text_chars += n
                    scan_hooks_both(content, "assistant_text", hook_hits, hook_hits_g6)
                else:
                    user_text_chars += n
                    scan_hooks_both(content, "user_text", hook_hits, hook_hits_g6)
                continue

            if not isinstance(content, list):
                continue

            for c in content:
                if not isinstance(c, dict):
                    continue
                bt = c.get("type")

                if bt == "text":
                    txt = c.get("text") or ""
                    n = len(txt)
                    total_content_chars += n
                    if t == "assistant":
                        assistant_text_chars += n
                        scan_hooks_both(txt, "assistant_text", hook_hits, hook_hits_g6)
                    else:
                        user_text_chars += n
                        scan_hooks_both(txt, "user_text", hook_hits, hook_hits_g6)

                elif bt == "thinking":
                    txt = c.get("thinking") or ""
                    n = len(txt)
                    total_content_chars += n
                    assistant_text_chars += n

                elif bt == "tool_use":
                    name = c.get("name")
                    cat = tool_category(name)
                    inp = c.get("input")
                    try:
                        n = len(json.dumps(inp, ensure_ascii=False)) if inp is not None else 0
                    except Exception:
                        n = 0
                    total_content_chars += n
                    tool_use_input_chars[cat] += n
                    tool_use_input_by_rawname[name or "?"] += n   # Abschnitt G2
                    tid = c.get("id")
                    if tid:
                        tool_id_to_call[tid] = {"name": name, "cat": cat, "input": inp}

                    if name == "Write" and isinstance(inp, dict):   # Abschnitt G2
                        wcontent = inp.get("content")
                        wclen = len(wcontent) if isinstance(wcontent, str) else 0
                        write_content_lens.append(wclen)
                        write_records.append((norm_path(inp.get("file_path")), wclen))
                    elif name == "Edit" and isinstance(inp, dict):   # Abschnitt G2
                        ns = inp.get("new_string")
                        edit_new_string_lens.append(len(ns) if isinstance(ns, str) else 0)

                elif bt == "tool_result":
                    tid = c.get("tool_use_id")
                    call = tool_id_to_call.get(tid) if tid else None
                    cat = call["cat"] if call else "sonstige"
                    text, text_chars, raw_chars = tool_result_text_and_sizes(c.get("content"))
                    total_content_chars += raw_chars
                    tool_result_chars[cat] += text_chars
                    if raw_chars > text_chars:
                        nontext_by_tool[cat] += (raw_chars - text_chars)
                    if text:
                        scan_hooks_both(text, "tool_result", hook_hits, hook_hits_g6)

                    if call and call["name"] in ("Read",):
                        inp = call["input"] or {}
                        fp = inp.get("file_path")
                        has_ol = bool(inp.get("offset")) or bool(inp.get("limit"))
                        n_lines = (text.count("\n") + 1) if text else 0
                        read_records.append((ext_bucket(fp), has_ol, text_chars, n_lines, norm_path(fp)))
                        if fp:
                            fk = norm_path(fp)
                            file_read_chars[fk] += text_chars
                            file_read_count[fk] += 1

                    elif call and call["name"] in ("Bash", "PowerShell"):
                        inp = call["input"] or {}
                        cmd = inp.get("command") or ""
                        cmd_prefix = " ".join(cmd.split())[:80]
                        cmd_records.append((call["cat"], cmd_prefix, text_chars))
                        cmd_cls = classify_command(cmd)                      # Abschnitt G4
                        cmd_junk = cmd_has_junk_or_log(cmd)                   # Abschnitt G4/G6
                        cmd_class_records.append((cmd_cls, text_chars, cmd_junk))

                else:
                    # Bild/Dokument/Tool-Referenz o.ae. direkt auf Top-Level (selten)
                    try:
                        n = len(json.dumps(c, ensure_ascii=False))
                    except Exception:
                        n = 0
                    total_content_chars += n
                    top_level_other_chars += n

    # Wiederholte Reads derselben Datei im selben Transkript: Zeichen jenseits des ersten Reads
    repeat_read_chars = 0
    for fk, cnt in file_read_count.items():
        if cnt > 1:
            sizes = sorted((r[2] for r in read_records if r[4] == fk), reverse=True)
            # Summe minus den groessten Einzel-Read gilt als "wiederholt" (der erste sinnvolle Read
            # bleibt unangetastet, alles danach zaehlt als Wiederholung -- Naeherung, da Reihenfolge
            # nicht erneut nachverfolgt wird, aber Betrag ist ordnungsunabhaengig korrekt)
            repeat_read_chars += sum(sizes[1:])

    # Zweit-Writes (Abschnitt G2): Writes auf dieselbe Datei NACH dem ersten
    # Write im selben Transkript (Reihenfolge = Aufruf-Reihenfolge in write_records).
    second_write_count = 0
    second_write_chars = 0
    writes_by_file = defaultdict(list)
    for fk, clen in write_records:
        if fk:
            writes_by_file[fk].append(clen)
    for fk, lens in writes_by_file.items():
        if len(lens) > 1:
            second_write_count += len(lens) - 1
            second_write_chars += sum(lens[1:])

    end_context = None
    if last_end_usage is not None:
        end_context = sum(last_end_usage)

    return {
        "path": path,
        "is_subagent": is_subagent,
        "project_cwd": project_cwd,
        "first_ts": first_ts,
        "total_lines": total_lines,
        "json_errors": json_errors,
        "tool_result_chars": tool_result_chars,
        "assistant_text_chars": assistant_text_chars,
        "tool_use_input_chars": tool_use_input_chars,
        "user_text_chars": user_text_chars,
        "total_content_chars": total_content_chars,
        "nontext_by_tool": nontext_by_tool,
        "top_level_other_chars": top_level_other_chars,
        "hook_hits": hook_hits,
        "hook_hits_g6": hook_hits_g6,
        "read_records": read_records,
        "repeat_read_chars": repeat_read_chars,
        "cmd_records": cmd_records,
        "cmd_class_records": cmd_class_records,
        "n_turns": len(assistant_msg_ids),
        "end_context": end_context,
        "total_input_verbrauch": sum_usage_input_total,
        "total_cache_creation": sum_usage_cache_creation,
        "tool_use_input_by_rawname": tool_use_input_by_rawname,
        "write_content_lens": write_content_lens,
        "edit_new_string_lens": edit_new_string_lens,
        "second_write_count": second_write_count,
        "second_write_chars": second_write_chars,
    }


# ---------------------------------------------------------------------------
# Projekt-Normalisierung
# ---------------------------------------------------------------------------

def project_key(cwd, raw_project_dirname):
    if cwd:
        c = cwd.replace("/", "\\")
        low = c.lower()
        marker = "\\.claude\\worktrees\\"
        idx = low.find(marker)
        base = c[:idx] if idx != -1 else c
        base = base.rstrip("\\")
        name = base.split("\\")[-1] if base else None
        if name:
            return name
    # Fallback ueber den Projektordnernamen unter BASE
    raw = raw_project_dirname
    marker2 = "--claude-worktrees-"
    idx2 = raw.find(marker2)
    if idx2 != -1:
        raw = raw[:idx2]
    return raw


def project_dirname_from_path(path):
    # .../projects/<projdir>/subagents/agent-*.jsonl  ODER  .../projects/<projdir>/<session>.jsonl
    rel = os.path.relpath(path, BASE)
    return rel.split(os.sep)[0]


# ---------------------------------------------------------------------------
# Statistik-Helfer
# ---------------------------------------------------------------------------

def pct(part, whole):
    return (100.0 * part / whole) if whole else 0.0


def median(xs):
    return statistics.median(xs) if xs else 0


def p90(xs):
    if not xs:
        return 0
    xs = sorted(xs)
    idx = min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))
    return xs[idx]


def fmt_int(n):
    return f"{int(round(n)):,}".replace(",", ".")


def fmt_tokens(chars):
    return fmt_int(chars / 4.0)


# ---------------------------------------------------------------------------
# Hauptanalyse
# ---------------------------------------------------------------------------

def run(files, is_subagent, label):
    results = []
    n = len(files)
    for i, path in enumerate(files):
        if (i + 1) % 100 == 0 or (i + 1) == n:
            print(f"[{label}] {i+1}/{n} Dateien verarbeitet...", file=sys.stderr, flush=True)
        r = process_file(path, is_subagent)
        if r is not None:
            results.append(r)
    return results


def section_a(results):
    """Kontextfueller je Kategorie, aggregiert ueber alle Transkripte."""
    CATS = ["tool_result", "assistant_text", "tool_use_input", "user_text"]

    sum_tool_result_by_tool = Counter()
    sum_assistant_text = 0
    sum_tool_use_input = 0
    sum_user_text = 0
    sum_total_content = 0
    sum_deviation_abs = 0.0
    sum_nontext_by_tool = Counter()
    sum_top_level_other = 0

    per_file_cat_pct = defaultdict(list)  # cat -> [pct-of-file, ...] fuer Median/p90 je Kategorie
    per_file_cat_chars = defaultdict(list)

    deviations = []

    for r in results:
        tr_total = sum(r["tool_result_chars"].values())
        at = r["assistant_text_chars"]
        tu = sum(r["tool_use_input_chars"].values())
        ut = r["user_text_chars"]
        file_cat_sum = tr_total + at + tu + ut
        total = r["total_content_chars"]

        sum_tool_result_by_tool.update(r["tool_result_chars"])
        sum_assistant_text += at
        sum_tool_use_input += tu
        sum_user_text += ut
        sum_total_content += total
        sum_nontext_by_tool.update(r["nontext_by_tool"])
        sum_top_level_other += r["top_level_other_chars"]

        dev_pct = pct(abs(total - file_cat_sum), total) if total else 0.0
        deviations.append(dev_pct)

        if total > 0:
            per_file_cat_pct["tool_result"].append(pct(tr_total, total))
            per_file_cat_pct["assistant_text"].append(pct(at, total))
            per_file_cat_pct["tool_use_input"].append(pct(tu, total))
            per_file_cat_pct["user_text"].append(pct(ut, total))
        per_file_cat_chars["tool_result"].append(tr_total)
        per_file_cat_chars["assistant_text"].append(at)
        per_file_cat_chars["tool_use_input"].append(tu)
        per_file_cat_chars["user_text"].append(ut)

    grand_total_cat_sum = sum(sum_tool_result_by_tool.values()) + sum_assistant_text + sum_tool_use_input + sum_user_text

    return {
        "sum_tool_result_by_tool": sum_tool_result_by_tool,
        "sum_tool_result_total": sum(sum_tool_result_by_tool.values()),
        "sum_assistant_text": sum_assistant_text,
        "sum_tool_use_input": sum_tool_use_input,
        "sum_user_text": sum_user_text,
        "sum_total_content": sum_total_content,
        "grand_total_cat_sum": grand_total_cat_sum,
        "overall_deviation_pct": pct(abs(sum_total_content - grand_total_cat_sum), sum_total_content),
        "sum_nontext_by_tool": sum_nontext_by_tool,
        "sum_top_level_other": sum_top_level_other,
        "per_file_deviation_median": median(deviations),
        "per_file_deviation_p90": p90(deviations),
        "per_file_deviation_max": max(deviations) if deviations else 0,
        "per_file_cat_pct_median": {k: median(v) for k, v in per_file_cat_pct.items()},
        "per_file_cat_pct_p90": {k: p90(v) for k, v in per_file_cat_pct.items()},
        "per_file_cat_chars_median": {k: median(v) for k, v in per_file_cat_chars.items()},
        "per_file_cat_chars_p90": {k: p90(v) for k, v in per_file_cat_chars.items()},
    }


def section_b(results):
    all_records = []
    for r in results:
        all_records.extend(r["read_records"])

    total_read_chars = sum(rec[2] for rec in all_records)

    over_300 = sum(rec[2] for rec in all_records if rec[3] > 300)
    over_400 = sum(rec[2] for rec in all_records if rec[3] > 400)
    over_800 = sum(rec[2] for rec in all_records if rec[3] > 800)

    full_reads = sum(1 for rec in all_records if not rec[1])
    partial_reads = sum(1 for rec in all_records if rec[1])
    full_reads_chars = sum(rec[2] for rec in all_records if not rec[1])
    partial_reads_chars = sum(rec[2] for rec in all_records if rec[1])

    by_ext_count = Counter()
    by_ext_chars = Counter()
    for rec in all_records:
        by_ext_count[rec[0]] += 1
        by_ext_chars[rec[0]] += rec[2]

    by_file_chars = Counter()
    by_file_count = Counter()
    for rec in all_records:
        fk = rec[4]
        if fk:
            by_file_chars[fk] += rec[2]
            by_file_count[fk] += 1

    top20_files = by_file_chars.most_common(20)

    total_repeat_read_chars = sum(r["repeat_read_chars"] for r in results)

    return {
        "n_reads": len(all_records),
        "total_read_chars": total_read_chars,
        "over_300_lines_chars": over_300,
        "over_300_lines_pct": pct(over_300, total_read_chars),
        "over_400_lines_chars": over_400,
        "over_400_lines_pct": pct(over_400, total_read_chars),
        "over_800_lines_chars": over_800,
        "over_800_lines_pct": pct(over_800, total_read_chars),
        "full_reads": full_reads,
        "partial_reads": partial_reads,
        "full_reads_pct": pct(full_reads, full_reads + partial_reads),
        "full_reads_chars": full_reads_chars,
        "partial_reads_chars": partial_reads_chars,
        "by_ext_count": by_ext_count,
        "by_ext_chars": by_ext_chars,
        "top20_files": [(fk, by_file_count[fk], chars) for fk, chars in top20_files],
        "repeat_read_chars": total_repeat_read_chars,
        "repeat_read_pct": pct(total_repeat_read_chars, total_read_chars),
    }


def section_c(results):
    all_cmds = []
    for r in results:
        for cat, prefix, chars in r["cmd_records"]:
            all_cmds.append((cat, prefix, chars, r.get("first_ts")))

    sizes = [c[2] for c in all_cmds]
    total = sum(sizes)
    over_10k = sum(s for s in sizes if s > 10_000)
    over_50k = sum(s for s in sizes if s > 50_000)

    top20 = sorted(all_cmds, key=lambda x: x[2], reverse=True)[:20]
    top20_fmt = []
    for cat, prefix, chars, ts in top20:
        date_str = ts.strftime("%Y-%m-%d") if ts else "?"
        top20_fmt.append((cat, prefix, chars, date_str))

    return {
        "n_cmds": len(all_cmds),
        "median": median(sizes),
        "p90": p90(sizes),
        "max": max(sizes) if sizes else 0,
        "total": total,
        "over_10k_chars": over_10k,
        "over_10k_pct": pct(over_10k, total),
        "over_50k_chars": over_50k,
        "over_50k_pct": pct(over_50k, total),
        "top20": top20_fmt,
    }


def section_d(results):
    """Hook-Rueckmeldungen. 'hook_agg'/'eslint_sizes' zaehlen wie bisher ueber
    ALLE uebergebenen Transkripte (Anzahl bleibt ueber das gesamte Report-
    Fenster vergleichbar). Die Hooks existieren erst seit HOOKS_ACTIVE_SINCE;
    'hook_quote_since' (Anteil der Transkripte mit >=1 Treffer je Hook) und
    'n_since_hooks_active' beziehen sich deshalb NUR auf Transkripte mit
    Datei-mtime ab diesem Datum."""
    hook_agg = defaultdict(lambda: {"count": 0, "chars": 0, "max": 0, "by_kind": Counter()})
    eslint_sizes = []
    since_ts = hooks_active_since_ts()
    hit_transcripts_since = defaultdict(set)
    n_since = 0
    for r in results:
        is_since = os.path.getmtime(r["path"]) >= since_ts
        if is_since:
            n_since += 1
        for key, kind, chars in r["hook_hits"]:
            a = hook_agg[key]
            a["count"] += 1
            a["chars"] += chars
            a["max"] = max(a["max"], chars)
            a["by_kind"][kind] += 1
            if key == "eslint":
                eslint_sizes.append(chars)
            if is_since:
                hit_transcripts_since[key].add(r["path"])
    hook_quote_since = {key: pct(len(paths), n_since) for key, paths in hit_transcripts_since.items()}
    return {
        "hook_agg": dict(hook_agg),
        "eslint_sizes": eslint_sizes,
        "n_transcripts_total": len(results),
        "n_since_hooks_active": n_since,
        "hook_quote_since": hook_quote_since,
    }


def overall_end_context_stats(results):
    ecs = [r["end_context"] for r in results if r["end_context"] is not None]
    return {
        "n": len(ecs),
        "median": median(ecs),
        "p90": p90(ecs),
        "max": max(ecs) if ecs else 0,
    }


def section_e(results, base_results_for_pct):
    by_project = defaultdict(list)
    for r in results:
        pd = project_dirname_from_path(r["path"])
        pk = project_key(r["project_cwd"], pd)
        by_project[pk].append(r)

    rows = []
    for pk, rs in by_project.items():
        end_contexts = [r["end_context"] for r in rs if r["end_context"] is not None]
        tr_total = sum(sum(r["tool_result_chars"].values()) for r in rs)
        at = sum(r["assistant_text_chars"] for r in rs)
        tu = sum(sum(r["tool_use_input_chars"].values()) for r in rs)
        ut = sum(r["user_text_chars"] for r in rs)
        cat_sum = tr_total + at + tu + ut
        rows.append({
            "project": pk,
            "n_runs": len(rs),
            "median_end_context_tokens": median(end_contexts) if end_contexts else 0,
            "pct_tool_result": pct(tr_total, cat_sum),
            "pct_assistant_text": pct(at, cat_sum),
            "pct_tool_use_input": pct(tu, cat_sum),
            "pct_user_text": pct(ut, cat_sum),
        })
    rows.sort(key=lambda x: x["n_runs"], reverse=True)
    return rows


def section_f(results, threshold_tokens=300_000):
    rows = []
    for r in results:
        if r["end_context"] is None:
            continue
        tokens = r["end_context"]
        if tokens <= threshold_tokens:
            continue
        pd = project_dirname_from_path(r["path"])
        pk = project_key(r["project_cwd"], pd)

        flat = Counter()
        for tool, chars in r["tool_result_chars"].items():
            flat[f"tool_result:{tool}"] += chars
        flat["assistant_text"] += r["assistant_text_chars"]
        flat["tool_use_input"] += sum(r["tool_use_input_chars"].values())
        flat["user_text"] += r["user_text_chars"]

        total = sum(flat.values())
        top3 = flat.most_common(3)
        top3_fmt = [(k, pct(v, total)) for k, v in top3]

        rows.append({
            "date": r["first_ts"].strftime("%Y-%m-%d") if r["first_ts"] else "?",
            "project": pk,
            "end_context_tokens": tokens,
            "n_turns": r["n_turns"],
            "top3": top3_fmt,
        })
    rows.sort(key=lambda x: x["end_context_tokens"], reverse=True)
    return rows


# ---------------------------------------------------------------------------
# Abschnitt G -- Hebel-Kennzahlen (nur Subagent-Transkripte, sofern nicht
# anders angegeben). Baut auf process_file()/section_a..d() auf, dupliziert
# deren Parsing nicht.
# ---------------------------------------------------------------------------

def _project_key_for_result(r):
    pd = project_dirname_from_path(r["path"])
    return project_key(r["project_cwd"], pd)


def _group_by_project(results):
    by_project = defaultdict(list)
    for r in results:
        by_project[_project_key_for_result(r)].append(r)
    return by_project


def section_g1(sub_results):
    thresholds = [150_000, 200_000, 300_000]
    n_total = len(sub_results)
    total_input_all = sum(r["total_input_verbrauch"] for r in sub_results)
    total_cc_all = sum(r["total_cache_creation"] for r in sub_results)
    rows = []
    for t in thresholds:
        group = [r for r in sub_results if r["end_context"] is not None and r["end_context"] > t]
        input_group = sum(r["total_input_verbrauch"] for r in group)
        cc_group = sum(r["total_cache_creation"] for r in group)
        rows.append({
            "threshold": t,
            "n": len(group),
            "pct_n": pct(len(group), n_total),
            "pct_input": pct(input_group, total_input_all),
            "pct_cc": pct(cc_group, total_cc_all),
        })
    return {"n_total": n_total, "total_input_all": total_input_all,
            "total_cc_all": total_cc_all, "rows": rows}


def section_g2(sub_results, a_sub):
    buckets = ["Write", "Edit", "MultiEdit", "Bash", "PowerShell", "Agent", "SendMessage", "sonstige"]
    bucket_chars = Counter()
    for r in sub_results:
        for rawname, chars in r["tool_use_input_by_rawname"].items():
            bucket_chars[g2_bucket(rawname)] += chars
    total_bucket_sum = sum(bucket_chars.values())

    write_lens = []
    edit_lens = []
    for r in sub_results:
        write_lens.extend(r["write_content_lens"])
        edit_lens.extend(r["edit_new_string_lens"])

    total_write_content_chars = sum(write_lens)
    over_10k_write_chars = sum(x for x in write_lens if x > 10_000)

    second_write_count = sum(r["second_write_count"] for r in sub_results)
    second_write_chars = sum(r["second_write_chars"] for r in sub_results)

    return {
        "buckets": buckets,
        "bucket_chars": bucket_chars,
        "total_bucket_sum": total_bucket_sum,
        "total_from_a": a_sub["sum_tool_use_input"],
        "write_n": len(write_lens),
        "write_median": median(write_lens),
        "write_p90": p90(write_lens),
        "write_total_content_chars": total_write_content_chars,
        "write_over_10k_chars": over_10k_write_chars,
        "write_over_10k_pct": pct(over_10k_write_chars, total_write_content_chars),
        "edit_n": len(edit_lens),
        "edit_median": median(edit_lens),
        "second_write_count": second_write_count,
        "second_write_chars": second_write_chars,
    }


def _code_read_stats(records, total_read_chars_scope):
    """records: Liste von read_records-Tupeln (ext_bucket, has_ol, chars, lines, norm_path).
    Ermittelt die Code-Endung ueber norm_path neu anhand von CODE_EXTS (dieselbe
    Liste wie Abschnitt B/READ_EXT_BUCKETS, seit der Vereinheitlichung deckungsgleich;
    eigene Ermittlung bleibt bestehen, da rec[0] bereits vor-gebuckete Werte wie
    'sonstige' enthalten kann)."""
    code_records = []
    for rec in records:
        fp = rec[4]
        if not fp:
            continue
        if os.path.splitext(fp)[1].lower() in CODE_EXTS:
            code_records.append(rec)

    chars = sum(rec[2] for rec in code_records)
    over_300 = sum(rec[2] for rec in code_records if rec[3] > 300)
    over_400 = sum(rec[2] for rec in code_records if rec[3] > 400)
    over_800 = sum(rec[2] for rec in code_records if rec[3] > 800)
    full_n = sum(1 for rec in code_records if not rec[1])
    partial_n = sum(1 for rec in code_records if rec[1])
    full_chars = sum(rec[2] for rec in code_records if not rec[1])
    partial_chars = sum(rec[2] for rec in code_records if rec[1])

    by_file_chars = Counter()
    by_file_count = Counter()
    for rec in code_records:
        by_file_chars[rec[4]] += rec[2]
        by_file_count[rec[4]] += 1
    top10 = [(fp, by_file_count[fp], c) for fp, c in by_file_chars.most_common(10)]

    return {
        "n": len(code_records),
        "chars": chars,
        "pct_of_all_reads": pct(chars, total_read_chars_scope),
        "over_300_pct": pct(over_300, chars), "over_300_chars": over_300,
        "over_400_pct": pct(over_400, chars), "over_400_chars": over_400,
        "over_800_pct": pct(over_800, chars), "over_800_chars": over_800,
        "full_n": full_n, "partial_n": partial_n,
        "full_chars": full_chars, "partial_chars": partial_chars,
        "top10": top10,
    }


def section_g3(sub_results):
    all_records = []
    for r in sub_results:
        all_records.extend(r["read_records"])
    total_read_chars_all = sum(rec[2] for rec in all_records)
    overall = _code_read_stats(all_records, total_read_chars_all)

    by_project = _group_by_project(sub_results)
    project_stats = {}
    for name in ("wlh-preiskalkulation-app", "fantasy-draft-helper"):
        matching = [r for pk, rs in by_project.items() if pk.lower() == name.lower() for r in rs]
        proj_records = []
        for r in matching:
            proj_records.extend(r["read_records"])
        proj_total_chars = sum(rec[2] for rec in proj_records)
        project_stats[name] = _code_read_stats(proj_records, proj_total_chars)

    return {"overall": overall, "projects": project_stats}


def _bash_class_stats(records):
    """records: Liste von (klasse, chars, junk_or_log_bool)-Tupeln (cmd_class_records)."""
    by_class = defaultdict(list)
    for cls, chars, _junk in records:
        by_class[cls].append(chars)
    total = sum(sum(v) for v in by_class.values())

    order = ["tests", "build", "datei-lesen", "git", "suche", "python-inline", "sonstige"]
    rows = []
    for cls in order:
        sizes = by_class.get(cls, [])
        rows.append({"class": cls, "n": len(sizes), "chars": sum(sizes),
                      "pct": pct(sum(sizes), total),
                      "median": median(sizes), "p90": p90(sizes)})

    n_datei_lesen = sum(1 for cls, _c, _j in records if cls == "datei-lesen")
    junk_datei_lesen = sum(1 for cls, _c, j in records if cls == "datei-lesen" and j)

    return {"rows": rows, "total": total,
            "n_datei_lesen": n_datei_lesen, "junk_datei_lesen_count": junk_datei_lesen}


def section_g4(sub_results, c_sub):
    all_records = []
    for r in sub_results:
        all_records.extend(r["cmd_class_records"])
    stats = _bash_class_stats(all_records)
    stats["total_from_c"] = c_sub["total"]
    return stats


def section_g5(sub_results):
    project_names = ["Plan Legacy code Migration", "wlh-preiskalkulation-app",
                      "WlH Preiskalkulation", "fantasy-draft-helper"]
    by_project = _group_by_project(sub_results)

    rows = []
    for name in project_names:
        matching = [r for pk, rs in by_project.items() if pk.lower() == name.lower() for r in rs]
        read_records = []
        cmd_class_records = []
        for r in matching:
            read_records.extend(r["read_records"])
            cmd_class_records.extend(r["cmd_class_records"])

        total_read_chars = sum(rec[2] for rec in read_records)
        md_chars = sum(rec[2] for rec in read_records
                        if rec[4] and os.path.splitext(rec[4])[1].lower() == ".md")
        code_chars = sum(rec[2] for rec in read_records
                          if rec[4] and os.path.splitext(rec[4])[1].lower() in CODE_EXTS)
        sonstige_chars = total_read_chars - md_chars - code_chars

        rows.append({
            "project": name,
            "n_runs": len(matching),
            "total_read_chars": total_read_chars,
            "md_chars": md_chars, "md_pct": pct(md_chars, total_read_chars),
            "code_chars": code_chars, "code_pct": pct(code_chars, total_read_chars),
            "sonstige_chars": sonstige_chars, "sonstige_pct": pct(sonstige_chars, total_read_chars),
            "bash_stats": _bash_class_stats(cmd_class_records),
        })
    return rows


def section_g6(sub_results, d_sub):
    es60 = []
    for r in sub_results:
        for key, _kind, chars in r["hook_hits_g6"]:
            if key == "eslint_g6":
                es60.append(chars)
    capped60 = sum(1 for x in es60 if x >= 60_000)

    read_junk_count = 0
    for r in sub_results:
        for rec in r["read_records"]:
            if path_has_junk_or_log(rec[4]):
                read_junk_count += 1

    bash_junk_datei_lesen_count = 0
    for r in sub_results:
        for cls, _chars, junk in r["cmd_class_records"]:
            if cls == "datei-lesen" and junk:
                bash_junk_datei_lesen_count += 1

    return {
        "eslint60_n": len(es60),
        "eslint60_median": median(es60),
        "eslint60_p90": p90(es60),
        "eslint60_max": max(es60) if es60 else 0,
        "eslint60_sum": sum(es60),
        "eslint60_capped_n": capped60,
        "eslint_d_n": len(d_sub["eslint_sizes"]),
        "n_since_hooks_active": d_sub["n_since_hooks_active"],
        "n_transcripts_total": d_sub["n_transcripts_total"],
        "read_junk_count": read_junk_count,
        "bash_junk_datei_lesen_count": bash_junk_datei_lesen_count,
    }


def section_g(sub_results):
    a_sub = section_a(sub_results)
    c_sub = section_c(sub_results)
    d_sub = section_d(sub_results)
    return {
        "g1": section_g1(sub_results),
        "g2": section_g2(sub_results, a_sub),
        "g3": section_g3(sub_results),
        "g4": section_g4(sub_results, c_sub),
        "g5": section_g5(sub_results),
        "g6": section_g6(sub_results, d_sub),
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(out_path, sub_files_n, main_files_n, skipped_sub, skipped_main,
                  sub_results, main_results, elapsed, since_dt=None, until_dt=None):
    lines = []

    def p(s=""):
        lines.append(s)

    window_long, window_short = describe_window(since_dt, until_dt)
    is_default_window = since_dt is None and until_dt is None
    skip_label = "aelter" if is_default_window else "ausserhalb des Fensters"

    p("=" * 78)
    p("Context-Fill-Analyse von Claude-Code-Transkripten")
    p("=" * 78)
    p(f"Zeitraum: {window_long}. Token-Zahlen sind Naeherungen (Zeichen / 4), "
      f"AUSSER 'Endkontext' in Abschnitt E und F: der stammt direkt aus den usage-Feldern "
      f"des letzten Assistant-Turns (input_tokens + cache_read_input_tokens + "
      f"cache_creation_input_tokens) und ist damit ein von Anthropic gemeldeter, exakter Wert.")
    p(f"Laufzeit des Skripts: {elapsed:.1f}s")
    p()
    p(f"Subagent-Transkripte gefunden ({window_short}): {sub_files_n} "
      f"(uebersprungen, {skip_label}: {skipped_sub}); erfolgreich verarbeitet: {len(sub_results)}")
    p(f"Hauptsession-Transkripte gefunden ({window_short}): {main_files_n} "
      f"(uebersprungen, {skip_label}: {skipped_main}); erfolgreich verarbeitet: {len(main_results)}")
    p()
    p("Plausibilitaetsprobe gegen cache_ttl_analysis.py (dort zuletzt 882 Sub- / 211 "
      "Hauptsession-Transkripte, files_ok):")
    p(f"  Hier: {len(sub_results)} Sub- / {len(main_results)} Hauptsession-Transkripte.")
    p("  Abweichung erwartungsgemaess klein positiv: Datenbestand waechst laufend "
      "(neue Sessions seit der Referenzmessung), gleiche Discovery-/Cutoff-Logik "
      "wie in cache_ttl_analysis.py.")
    p()

    for label, results in (("SUBAGENT", sub_results), ("HAUPTSESSION", main_results)):
        p("=" * 78)
        p(f"ABSCHNITT A -- Kontextfueller je Kategorie ({label})")
        p("=" * 78)
        a = section_a(results)
        p(f"Gesamtzeichen aller content-Bloecke (Summenprobe-Basis): {fmt_int(a['sum_total_content'])} "
          f"(~{fmt_tokens(a['sum_total_content'])} Tokens)")
        p(f"Summe der 4 Kategorien:                                  {fmt_int(a['grand_total_cat_sum'])} "
          f"(~{fmt_tokens(a['grand_total_cat_sum'])} Tokens)")
        p(f"Abweichung gesamt: {a['overall_deviation_pct']:.2f}% "
          f"(je Transkript: Median {a['per_file_deviation_median']:.2f}%, "
          f"p90 {a['per_file_deviation_p90']:.2f}%, Max {a['per_file_deviation_max']:.2f}%)")
        if a["overall_deviation_pct"] > 5:
            top_nontext = a["sum_nontext_by_tool"].most_common(3)
            top_nontext_str = ", ".join(f"{t} {fmt_int(c)} Zeichen" for t, c in top_nontext)
            p(f"  -> ueber 5%: Ursache sind nicht-textuelle Bloecke (v. a. Bilder, z. B. Screenshots) "
              f"in tool_result, die in die Summenprobe (raw, als JSON-Groesse inkl. Base64) aber "
              f"nicht in die 4 Kategorien (nur Text) einfliessen. Groesste Quellen hier: {top_nontext_str}. "
              f"Direkt im Content liegende Bild-/Dokument-Bloecke (ausserhalb tool_result): "
              f"{fmt_int(a['sum_top_level_other'])} Zeichen.")
        else:
            p("  -> unter 5%, keine gesonderte Erklaerung noetig.")
        p()
        p("Kategorie              Summe Zeichen      ~Tokens      Anteil   Median/Datei(%)  p90/Datei(%)")
        cats = [
            ("1. tool_result (gesamt)", a["sum_tool_result_total"]),
            ("2. Assistant-Text+Thinking", a["sum_assistant_text"]),
            ("3. Tool-Use-Inputs", a["sum_tool_use_input"]),
            ("4. User-Text", a["sum_user_text"]),
        ]
        gt = a["grand_total_cat_sum"] or 1
        keymap = {"1. tool_result (gesamt)": "tool_result", "2. Assistant-Text+Thinking": "assistant_text",
                  "3. Tool-Use-Inputs": "tool_use_input", "4. User-Text": "user_text"}
        for name, val in cats:
            k = keymap[name]
            p(f"{name:<26} {fmt_int(val):>14} {fmt_tokens(val):>12} {pct(val, gt):>9.1f}% "
              f"{a['per_file_cat_pct_median'].get(k, 0):>14.1f} {a['per_file_cat_pct_p90'].get(k, 0):>13.1f}")
        p()
        p("tool_result nach Tool (Top 15 nach Zeichen):")
        p(f"{'Tool':<28} {'Zeichen':>14} {'~Tokens':>12} {'Anteil an tool_result':>22}")
        tr_total = a["sum_tool_result_total"] or 1
        for tool, chars in a["sum_tool_result_by_tool"].most_common(15):
            p(f"{tool:<28} {fmt_int(chars):>14} {fmt_tokens(chars):>12} {pct(chars, tr_total):>21.1f}%")
        p()

        p("-" * 78)
        p(f"ABSCHNITT B -- Read-Tiefe ({label})")
        p("-" * 78)
        b = section_b(results)
        p(f"Anzahl Read-Aufrufe: {fmt_int(b['n_reads'])}, gelesene Zeichen gesamt: "
          f"{fmt_int(b['total_read_chars'])} (~{fmt_tokens(b['total_read_chars'])} Tokens)")
        p(f"Anteil aus Ergebnissen > 300 Zeilen: {b['over_300_lines_pct']:.1f}% "
          f"({fmt_int(b['over_300_lines_chars'])} Zeichen)")
        p(f"Anteil aus Ergebnissen > 400 Zeilen: {b['over_400_lines_pct']:.1f}% "
          f"({fmt_int(b['over_400_lines_chars'])} Zeichen)")
        p(f"Anteil aus Ergebnissen > 800 Zeilen: {b['over_800_lines_pct']:.1f}% "
          f"({fmt_int(b['over_800_lines_chars'])} Zeichen)")
        p(f"Voll-Reads: {fmt_int(b['full_reads'])} ({b['full_reads_pct']:.1f}%), "
          f"Teil-Reads (offset/limit): {fmt_int(b['partial_reads'])} "
          f"({100 - b['full_reads_pct']:.1f}%)")
        p(f"  Zeichen aus Voll-Reads: {fmt_int(b['full_reads_chars'])}  |  "
          f"Zeichen aus Teil-Reads: {fmt_int(b['partial_reads_chars'])}")
        p(f"Anteil Zeichen aus wiederholten Reads derselben Datei im selben Transkript: "
          f"{b['repeat_read_pct']:.1f}% ({fmt_int(b['repeat_read_chars'])} Zeichen)")
        p()
        p("Verteilung nach Dateiendung:")
        p(f"{'Endung':<10} {'Anzahl':>8} {'Zeichen':>14} {'~Tokens':>12} {'Anteil':>8}")
        tot_ext_chars = b["total_read_chars"] or 1
        for ext, chars in b["by_ext_chars"].most_common():
            cnt = b["by_ext_count"][ext]
            p(f"{ext:<10} {cnt:>8} {fmt_int(chars):>14} {fmt_tokens(chars):>12} {pct(chars, tot_ext_chars):>7.1f}%")
        p()
        p("Top-20 gelesene Dateien nach Zeichensumme:")
        p(f"{'#':>3} {'Reads':>6} {'Zeichen':>12} {'~Tokens':>10}  Pfad")
        for i, (fp, cnt, chars) in enumerate(b["top20_files"], 1):
            p(f"{i:>3} {cnt:>6} {fmt_int(chars):>12} {fmt_tokens(chars):>10}  {fp}")
        p()

        p("-" * 78)
        p(f"ABSCHNITT C -- Kommandoausgaben Bash/PowerShell ({label})")
        p("-" * 78)
        c = section_c(results)
        p(f"Anzahl Aufrufe: {fmt_int(c['n_cmds'])}")
        p(f"Ausgabegroesse: Median {fmt_int(c['median'])} Zeichen, p90 {fmt_int(c['p90'])} Zeichen, "
          f"Maximum {fmt_int(c['max'])} Zeichen")
        p(f"Anteil Ausgaben > 10.000 Zeichen an Gesamtsumme: {c['over_10k_pct']:.1f}% "
          f"({fmt_int(c['over_10k_chars'])} Zeichen)")
        p(f"Anteil Ausgaben > 50.000 Zeichen an Gesamtsumme: {c['over_50k_pct']:.1f}% "
          f"({fmt_int(c['over_50k_chars'])} Zeichen)")
        p()
        p("Top-20 Kommandos nach Ausgabegroesse:")
        p(f"{'#':>3} {'Tool':<12} {'Zeichen':>10} {'Datum':<12}  Kommando (<=80 Zeichen)")
        for i, (cat, prefix, chars, date_str) in enumerate(c["top20"], 1):
            p(f"{i:>3} {cat:<12} {fmt_int(chars):>10} {date_str:<12}  {prefix}")
        p()

        p("-" * 78)
        p(f"ABSCHNITT D -- Hook-Rueckmeldungen ({label})")
        p("-" * 78)
        d = section_d(results)
        if not d["hook_agg"]:
            p("Keine Treffer der Hook-Suchmuster in diesem Korpus.")
        else:
            p(f"{'Hook':<18} {'Anzahl':>8} {'Zeichen':>12} {'~Tokens':>10} {'Groesste':>10}  Nachrichtenart (Anzahl)")
            for key, a2 in sorted(d["hook_agg"].items(), key=lambda kv: -kv[1]["chars"]):
                kinds = ", ".join(f"{k}:{v}" for k, v in a2["by_kind"].most_common())
                p(f"{key:<18} {a2['count']:>8} {fmt_int(a2['chars']):>12} {fmt_tokens(a2['chars']):>10} "
                  f"{fmt_int(a2['max']):>10}  {kinds}")
        p()
        p(f"Hooks aktiv seit {HOOKS_ACTIVE_SINCE} (Datei-mtime). 'Anzahl' oben zaehlt weiter ueber "
          f"das gesamte Report-Fenster ({label}); die folgende Trefferquote je Transkript bezieht "
          f"sich NUR auf Transkripte mit mtime ab {HOOKS_ACTIVE_SINCE} (n={d['n_since_hooks_active']} "
          f"von {d['n_transcripts_total']} Transkripten in diesem Bereich).")
        if d["n_since_hooks_active"] > 0 and d["hook_quote_since"]:
            for key, qpct in sorted(d["hook_quote_since"].items(), key=lambda kv: -kv[1]):
                p(f"  {key:<18} {qpct:>5.1f}% der Transkripte seit {HOOKS_ACTIVE_SINCE} mit >=1 Treffer")
        elif d["n_since_hooks_active"] == 0:
            p("  Keine Transkripte mit mtime ab diesem Datum in diesem Bereich.")
        p()
        if d["eslint_sizes"]:
            es = d["eslint_sizes"]
            capped = sum(1 for x in es if x >= 6000)
            p(f"ESLint-Meldungsgroesse: n={len(es)}, Median {fmt_int(median(es))} Zeichen, "
              f"p90 {fmt_int(p90(es))} Zeichen, Max {fmt_int(max(es))} Zeichen")
            if capped:
                p(f"  Hinweis: Erfassung pro Fund ist bei 6.000 Zeichen gedeckelt (Naeherung fuer "
                  f"lange, nicht durch Leerzeile abgesetzte Ausgaben); {capped} von {len(es)} Funden "
                  f"treffen die Kappung exakt und sind in der Realitaet ggf. laenger.")
        else:
            p("ESLint: keine Treffer.")
        p()

    p("=" * 78)
    p("ABSCHNITT E -- Je Projekt (Subagent-Laeufe)")
    p("=" * 78)
    oe = overall_end_context_stats(sub_results)
    p(f"Endkontext ueber ALLE {oe['n']} Subagent-Transkripte (exakte Tokens aus usage): "
      f"Median {fmt_int(oe['median'])}, p90 {fmt_int(oe['p90'])}, Max {fmt_int(oe['max'])}.")
    p("(Referenzwerte aus dem Auftrag: Median ~131K, Spitzen 300K-700K -- deckt sich mit diesem Lauf.)")
    p()
    e_rows = section_e(sub_results, sub_results)
    top5 = e_rows[:5]
    names_top5 = {r["project"] for r in top5}
    wlh_row = next((r for r in e_rows if "wlh-preiskalkulation-app" in r["project"].lower()), None)
    p(f"{'Projekt':<45} {'Laeufe':>7} {'Median-Endktx(~Tok)':>20} {'tool_res%':>10} "
      f"{'ass_text%':>10} {'tool_use%':>10} {'user_text%':>11}")
    for r in top5:
        p(f"{r['project'][:45]:<45} {r['n_runs']:>7} {fmt_int(r['median_end_context_tokens']):>20} "
          f"{r['pct_tool_result']:>9.1f}% {r['pct_assistant_text']:>9.1f}% "
          f"{r['pct_tool_use_input']:>9.1f}% {r['pct_user_text']:>10.1f}%")
    if wlh_row and wlh_row["project"] not in names_top5:
        p("--- zusaetzlich ausgewiesen (nicht unter Top 5) ---")
        r = wlh_row
        p(f"{r['project'][:45]:<45} {r['n_runs']:>7} {fmt_int(r['median_end_context_tokens']):>20} "
          f"{r['pct_tool_result']:>9.1f}% {r['pct_assistant_text']:>9.1f}% "
          f"{r['pct_tool_use_input']:>9.1f}% {r['pct_user_text']:>10.1f}%")
    elif not wlh_row:
        p("Hinweis: kein Projekt mit 'wlh-preiskalkulation-app' im Namen unter den "
          "Subagent-Transkripten des Zeitraums gefunden (Projekt existiert im Korpus "
          "u. U. nur unter einem anderen Ordnernamen, z. B. 'WlH Preiskalkulation' "
          "als separater Klon -- siehe Top-Liste).")
    p()
    p(f"(Projekte insgesamt mit Subagent-Laeufen im Zeitraum: {len(e_rows)}. "
      f"Projekt-Schluessel = Ordnername aus dem cwd-Feld, Worktree-Suffix "
      f"'\\.claude\\worktrees\\<name>' abgeschnitten.)")
    p()

    p("=" * 78)
    p(f"ABSCHNITT F -- Grosse Kontexte (Subagent-Transkripte > 300K Tokens Endkontext)")
    p("=" * 78)
    f_rows = section_f(sub_results, 300_000)
    if not f_rows:
        p("Keine Subagent-Transkripte im Zeitraum mit Endkontext > 300K Tokens (Naeherung).")
    else:
        p(f"Anzahl: {len(f_rows)}")
        p(f"{'Datum':<12} {'Projekt':<38} {'Endktx(~Tok)':>13} {'Turns':>6}  Top-3-Kategorien (Anteil)")
        top_cat_counter = Counter()
        for r in f_rows:
            top3_str = "; ".join(f"{k} {v:.0f}%" for k, v in r["top3"])
            p(f"{r['date']:<12} {r['project'][:38]:<38} {fmt_int(r['end_context_tokens']):>13} "
              f"{r['n_turns']:>6}  {top3_str}")
            if r["top3"]:
                top_cat_counter[r["top3"][0][0]] += 1
        p()
        dominant = top_cat_counter.most_common(1)[0] if top_cat_counter else None
        if dominant:
            p(f"Dominante Kategorie (haeufigste Top-1-Kategorie in dieser Gruppe): "
              f"{dominant[0]} in {dominant[1]} von {len(f_rows)} Transkripten "
              f"({pct(dominant[1], len(f_rows)):.0f}%).")
    p()

    p("=" * 78)
    p("ABSCHNITT G -- Hebel-Kennzahlen fuer Token-Spar-Policies (Subagent-Transkripte)")
    p("=" * 78)
    g = section_g(sub_results)
    p(f"Basis: {len(sub_results)} Subagent-Transkripte. Alle Kennzahlen G1-G6 gelten nur fuer "
      f"Subagent-Transkripte. G1-Verbrauchswerte sind exakte Tokens aus den usage-Feldern "
      f"(wie Endkontext in E/F), alle anderen Zeichen-Werte in G sind Roh-Zeichen (Naeherung "
      f"Zeichen/4 fuer ~Tokens, sofern angegeben).")
    p()

    p("-" * 78)
    p("G1 -- Anteil grosser Laeufe am Gesamtverbrauch")
    p("-" * 78)
    g1 = g["g1"]
    p(f"Gesamt-Input-Verbrauch ueber alle {fmt_int(g1['n_total'])} Subagent-Transkripte "
      f"(Summe input_tokens+cache_read+cache_creation ueber ALLE Assistant-Turns, exakt): "
      f"{fmt_int(g1['total_input_all'])} Tokens, davon Cache-Writes (cache_creation_input_tokens): "
      f"{fmt_int(g1['total_cc_all'])} Tokens.")
    p(f"{'Endkontext':<12} {'Anzahl':>8} {'Anteil Transkr.':>16} {'Anteil Input-Verbr.':>20} {'Anteil Cache-Writes':>20}")
    for row in g1["rows"]:
        label = f"> {row['threshold'] // 1000}K"
        p(f"{label:<12} {row['n']:>8} {row['pct_n']:>15.1f}% {row['pct_input']:>19.1f}% {row['pct_cc']:>19.1f}%")
    p()

    p("-" * 78)
    p("G2 -- Tool-Use-Inputs nach Tool")
    p("-" * 78)
    g2 = g["g2"]
    p(f"{'Tool':<14} {'Zeichen':>14} {'~Tokens':>12} {'Anteil':>8}")
    for b in g2["buckets"]:
        c = g2["bucket_chars"].get(b, 0)
        p(f"{b:<14} {fmt_int(c):>14} {fmt_tokens(c):>12} {pct(c, g2['total_bucket_sum']):>7.1f}%")
    p(f"{'Summe':<14} {fmt_int(g2['total_bucket_sum']):>14} {fmt_tokens(g2['total_bucket_sum']):>12} {100.0:>7.1f}%")
    p(f"Summenprobe: Gesamt-Tool-Use-Inputs aus Abschnitt A (Subagent) = {fmt_int(g2['total_from_a'])} Zeichen; "
      f"Differenz zur G2-Summe: {fmt_int(abs(g2['total_bucket_sum'] - g2['total_from_a']))} Zeichen.")
    p()
    p(f"Write: {fmt_int(g2['write_n'])} Aufrufe, Median content-Laenge {fmt_int(g2['write_median'])} Zeichen, "
      f"p90 {fmt_int(g2['write_p90'])} Zeichen.")
    p(f"  Anteil Writes > 10.000 Zeichen an Summe content-Zeichen ({fmt_int(g2['write_total_content_chars'])}): "
      f"{g2['write_over_10k_pct']:.1f}% ({fmt_int(g2['write_over_10k_chars'])} Zeichen)")
    p(f"Edit: {fmt_int(g2['edit_n'])} Aufrufe, Median new_string-Laenge {fmt_int(g2['edit_median'])} Zeichen.")
    p(f"Zweit-Writes (2. und weitere Writes derselben Datei im selben Transkript): "
      f"{fmt_int(g2['second_write_count'])} Aufrufe, {fmt_int(g2['second_write_chars'])} Zeichen.")
    p()

    p("-" * 78)
    p(f"G3 -- Dateigroesse nur bei Code-Reads ({' '.join(sorted(CODE_EXTS))})")
    p("-" * 78)
    g3 = g["g3"]

    def print_g3_block(label, stats):
        p(f"[{label}]")
        p(f"  Code-Reads: {fmt_int(stats['n'])} Aufrufe, {fmt_int(stats['chars'])} Zeichen "
          f"({stats['pct_of_all_reads']:.1f}% aller Read-Zeichen in diesem Bereich)")
        p(f"  davon > 300 Zeilen: {stats['over_300_pct']:.1f}% ({fmt_int(stats['over_300_chars'])} Zeichen)")
        p(f"  davon > 400 Zeilen: {stats['over_400_pct']:.1f}% ({fmt_int(stats['over_400_chars'])} Zeichen)")
        p(f"  davon > 800 Zeilen: {stats['over_800_pct']:.1f}% ({fmt_int(stats['over_800_chars'])} Zeichen)")
        p(f"  Voll-Reads: {fmt_int(stats['full_n'])} ({fmt_int(stats['full_chars'])} Zeichen)  |  "
          f"Teil-Reads: {fmt_int(stats['partial_n'])} ({fmt_int(stats['partial_chars'])} Zeichen)")
        if stats["top10"]:
            p("  Top-10 Code-Dateien nach Zeichensumme:")
            p(f"  {'#':>3} {'Reads':>6} {'Zeichen':>10}  Pfad")
            for i, (fp, cnt, chars) in enumerate(stats["top10"], 1):
                p(f"  {i:>3} {cnt:>6} {fmt_int(chars):>10}  {fp}")
        else:
            p("  Keine Code-Reads in diesem Bereich.")
        p()

    print_g3_block("Alle Subagent-Transkripte", g3["overall"])
    print_g3_block("Projekt: wlh-preiskalkulation-app", g3["projects"]["wlh-preiskalkulation-app"])
    print_g3_block("Projekt: fantasy-draft-helper", g3["projects"]["fantasy-draft-helper"])

    p("-" * 78)
    p("G4 -- Bash-Ausgaben nach Kommandoklasse")
    p("-" * 78)
    g4 = g["g4"]
    p(f"{'Klasse':<16} {'Anzahl':>8} {'Zeichen':>14} {'Anteil':>8} {'Median':>10} {'p90':>10}")
    for row in g4["rows"]:
        p(f"{row['class']:<16} {row['n']:>8} {fmt_int(row['chars']):>14} {row['pct']:>7.1f}% "
          f"{fmt_int(row['median']):>10} {fmt_int(row['p90']):>10}")
    p(f"{'Summe':<16} {'':>8} {fmt_int(g4['total']):>14} {100.0:>7.1f}%")
    p(f"Summenprobe: Bash+PowerShell-Zeichen aus Abschnitt A/C (Subagent) = {fmt_int(g4['total_from_c'])} Zeichen; "
      f"Differenz: {fmt_int(abs(g4['total'] - g4['total_from_c']))} Zeichen.")
    p(f"Zusatz 'datei-lesen': {fmt_int(g4['n_datei_lesen'])} Aufrufe insgesamt, davon "
      f"{fmt_int(g4['junk_datei_lesen_count'])} mit Junk-Segment oder .log-Endung im Kommandotext.")
    p()

    p("-" * 78)
    p("G5 -- Je Projekt: Read und Bash")
    p("-" * 78)
    for row in g["g5"]:
        p(f"[{row['project']}]  ({fmt_int(row['n_runs'])} Laeufe)")
        p(f"  Read gesamt: {fmt_int(row['total_read_chars'])} Zeichen")
        p(f"    .md:      {fmt_int(row['md_chars']):>12} Zeichen ({row['md_pct']:.1f}%)")
        p(f"    Code:     {fmt_int(row['code_chars']):>12} Zeichen ({row['code_pct']:.1f}%)")
        p(f"    sonstige: {fmt_int(row['sonstige_chars']):>12} Zeichen ({row['sonstige_pct']:.1f}%)")
        bs = row["bash_stats"]
        p(f"  Bash/PowerShell-Ausgaben gesamt: {fmt_int(bs['total'])} Zeichen")
        for r2 in bs["rows"]:
            if r2["n"] == 0:
                continue
            p(f"    {r2['class']:<14} {r2['n']:>6} Aufrufe  {fmt_int(r2['chars']):>12} Zeichen  ({r2['pct']:.1f}%)")
        p()

    p("-" * 78)
    p("G6 -- Hook-Ausgabe ohne Kappung (ESLint) und Junk-Pfade Read vs. Bash")
    p("-" * 78)
    g6 = g["g6"]
    p(f"ESLint mit 60.000-Zeichen-Kappung (statt 6.000 in Abschnitt D): n={fmt_int(g6['eslint60_n'])}, "
      f"Median {fmt_int(g6['eslint60_median'])} Zeichen, p90 {fmt_int(g6['eslint60_p90'])} Zeichen, "
      f"echtes Maximum {fmt_int(g6['eslint60_max'])} Zeichen, Summe {fmt_int(g6['eslint60_sum'])} Zeichen.")
    if g6["eslint60_capped_n"]:
        p(f"  Hinweis: {g6['eslint60_capped_n']} von {g6['eslint60_n']} Funden treffen weiterhin die "
          f"60.000-Kappung exakt und sind in der Realitaet ggf. laenger.")
    p(f"  (Zum Vergleich Abschnitt D, 6.000-Cap: n={fmt_int(g6['eslint_d_n'])} Funde.)")
    p(f"  Hooks aktiv seit {HOOKS_ACTIVE_SINCE}; n={g6['n_since_hooks_active']} von "
      f"{g6['n_transcripts_total']} Subagent-Transkripten mit mtime ab diesem Datum "
      f"(Trefferquote je Transkript siehe Abschnitt D).")
    p()
    p(f"Junk-/.log-Pfade ({', '.join(sorted(JUNK_SEGMENTS_G4))}, dist-*, Lockfile-Namen, "
      f"oder .log-Endung):")
    p(f"  Read-Tool: {fmt_int(g6['read_junk_count'])} Aufrufe auf solche Pfade (das sieht der read-gate-Hook).")
    p(f"  Bash 'datei-lesen': {fmt_int(g6['bash_junk_datei_lesen_count'])} Aufrufe auf solche Pfade "
      f"(am read-gate-Hook vorbei, da kein Read-Tool-Aufruf).")
    p()

    p("=" * 78)
    p("ENDE DES REPORTS")
    p("=" * 78)

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def parse_datetime_bound(s):
    """Parst --since/--until: YYYY-MM-DD oder YYYY-MM-DDTHH:MM (lokale Zeit,
    wie os.path.getmtime()). Ein reines Datum wird zu Mitternacht dieses Tages --
    bei --until schliesst das den Vortag komplett ein (exklusive Obergrenze)."""
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Ungueltiges Datum/Zeit: {s!r} (erwartet YYYY-MM-DD oder YYYY-MM-DDTHH:MM)")


def describe_window(since_dt, until_dt):
    """Menschenlesbare Beschreibung des verwendeten Datumsfensters fuer den
    Report-Kopf, als (lang, kurz). Ohne --since/--until identisch zum
    bisherigen Text (Default: letzte CUTOFF_DAYS Tage)."""
    if since_dt is None and until_dt is None:
        return f"letzte {CUTOFF_DAYS} Tage", f"<= {CUTOFF_DAYS} Tage"
    since_s = since_dt.strftime("%Y-%m-%d %H:%M") if since_dt is not None else "Anfang"
    until_s = until_dt.strftime("%Y-%m-%d %H:%M") if until_dt is not None else "jetzt"
    long_label = f"--since {since_s} bis --until {until_s} (until exklusiv)"
    short_label = f"{since_s} bis {until_s}"
    return long_label, short_label


def build_arg_parser():
    ap = argparse.ArgumentParser(
        description="Analyse von Claude-Code-Transkripten: WOMIT wird der Kontext gefuellt "
                     "(siehe Modul-Docstring).")
    ap.add_argument("--since", type=parse_datetime_bound, default=None,
                     help="Nur Transkripte mit Datei-mtime ab diesem Zeitpunkt "
                          "(YYYY-MM-DD oder YYYY-MM-DDTHH:MM). Ersetzt zusammen mit --until "
                          f"das Default-Fenster der letzten {CUTOFF_DAYS} Tage.")
    ap.add_argument("--until", type=parse_datetime_bound, default=None,
                     help="Nur Transkripte mit Datei-mtime vor diesem Zeitpunkt (exklusiv). "
                          "Ein reines Datum schliesst den Vortag komplett ein.")
    ap.add_argument("--out", default=None,
                     help="Pfad fuer den Report (UTF-8). Ohne Angabe: "
                          "<Skriptordner>/context_fill_analysis_output_<YYYY-MM-DD>.txt "
                          "(Datum des Laufs, nicht mehr Temp).")
    return ap


def default_out_path():
    """Default-Ausgabepfad ohne --out: im Ordner dieses Skripts (nicht mehr Temp),
    Dateiname mit Datum des Laufs."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(script_dir, f"context_fill_analysis_output_{date_str}.txt")


def main():
    args = build_arg_parser().parse_args()
    t0 = time.time()
    sub_files, main_files, skipped_sub, skipped_main = discover_files(args.since, args.until)
    _, window_short = describe_window(args.since, args.until)
    print(f"Subagent-Dateien ({window_short}): {len(sub_files)}, uebersprungen: {skipped_sub}",
          file=sys.stderr)
    print(f"Hauptsession-Dateien ({window_short}): {len(main_files)}, uebersprungen: {skipped_main}",
          file=sys.stderr)

    sub_results = run(sub_files, True, "SUB")
    main_results = run(main_files, False, "MAIN")

    elapsed = time.time() - t0

    out_path = args.out if args.out else default_out_path()
    write_report(out_path, len(sub_files), len(main_files), skipped_sub, skipped_main,
                 sub_results, main_results, elapsed, args.since, args.until)

    print(f"\nReport geschrieben: {out_path}", file=sys.stderr)
    print(f"Laufzeit: {elapsed:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
