"""
Ergaenzende Analyse zu cache_ttl_analysis.py: vier Kennzahlen rund um
"Resume-Writes" (Fortsetzung eines fertigen Subagents per SendMessage),
nur fuer Subagent-Transkripte.

Uebernimmt Parsing und Dateifilter (mtime <= 60 Tage) 1:1 aus
cache_ttl_analysis.py. Liest NUR, streamt JSONL zeilenweise. Keine
Nachrichtentexte werden gespeichert -- nur Zahlen, Zeitstempel,
Modellnamen und Dateinamen der Transkripte.

Kennzahlen:
1. Resume-Writes: Median/Mittelwert/p25/p75 der Token-Groesse
   (cache_creation_input_tokens der Assistant-Nachricht direkt nach
   einem Resume) + Bucket-Verteilung (<50K, 50-150K, 150-300K, >300K).
2. Startkosten eines frischen Agents: cache_creation_input_tokens der
   ERSTEN Assistant-Nachricht jedes Transkripts; Median/p25/p75.
3. Endgroesse des Kontexts: max cache_read_input_tokens je Transkript;
   Median/p25/p75, getrennt nach Transkripten mit >=1 Resume / ohne.
4. Arbeit nach dem Resume: Anzahl Assistant-Nachrichten vom Resume bis
   Transkriptende bzw. bis zum naechsten Resume; Median/p25/p75.
"""

import glob
import json
import math
import os
import statistics
import sys
import time
from datetime import datetime

BASE = r"C:\Users\szieg\.claude\projects"
CUTOFF_DAYS = 60


def parse_ts(ts_raw):
    if not ts_raw:
        return None
    try:
        return datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    except Exception:
        return None


def content_is_tool_result_only(content):
    if isinstance(content, str):
        return False
    if isinstance(content, list):
        if len(content) == 0:
            return False
        return all(isinstance(c, dict) and c.get("type") == "tool_result" for c in content)
    return False


def content_has_tool_use(content):
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                return True
    return False


def discover_sub_files():
    sub_files = glob.glob(os.path.join(BASE, "**", "subagents", "agent-*.jsonl"), recursive=True)
    cutoff = time.time() - CUTOFF_DAYS * 86400
    sub_recent = [f for f in sub_files if os.path.getmtime(f) >= cutoff]
    skipped = len(sub_files) - len(sub_recent)
    return sub_recent, skipped


def process_file(path):
    """1:1 uebernommene Parsing-Logik aus cache_ttl_analysis.py (nur
    Subagent-Zweig), dedupliziert Assistant-Fragmente nach message.id zu
    logischen 'Turns' und erkennt Resume-Stellen."""

    groups = []
    resume_after = set()
    cur = None

    try:
        fh = open(path, "r", encoding="utf-8", errors="replace")
    except Exception:
        return None

    with fh:
        for raw_line in fh:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except Exception:
                continue

            t = obj.get("type")
            if t == "assistant":
                msg = obj.get("message") or {}
                mid = msg.get("id")
                content = msg.get("content")
                has_tu = content_has_tool_use(content)

                if cur is not None and cur["id"] == mid and mid is not None:
                    if has_tu:
                        cur["has_tool_use"] = True
                    continue

                if cur is not None:
                    groups.append(cur)

                usage = msg.get("usage") or {}
                cur = {
                    "id": mid,
                    "ts": parse_ts(obj.get("timestamp")),
                    "model": msg.get("model"),
                    "cache_creation_input_tokens": usage.get("cache_creation_input_tokens") or 0,
                    "cache_read_input_tokens": usage.get("cache_read_input_tokens") or 0,
                    "has_tool_use": has_tu,
                }
            else:
                if cur is not None:
                    groups.append(cur)
                    closed_index = len(groups) - 1
                    if t == "user" and not groups[closed_index]["has_tool_use"]:
                        content = (obj.get("message") or {}).get("content")
                        if not content_is_tool_result_only(content):
                            resume_after.add(closed_index)
                    cur = None
    if cur is not None:
        groups.append(cur)

    return {"path": path, "groups": groups, "resume_after": resume_after}


def percentile(sorted_data, p):
    """Lineare Interpolation zwischen den naechsten Raengen (numpy-Default)."""
    if not sorted_data:
        return None
    if len(sorted_data) == 1:
        return sorted_data[0]
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1


def stats_line(data):
    if not data:
        return {"n": 0, "median": None, "mean": None, "p25": None, "p75": None}
    s = sorted(data)
    return {
        "n": len(s),
        "median": statistics.median(s),
        "mean": statistics.mean(s),
        "p25": percentile(s, 25),
        "p75": percentile(s, 75),
    }


def bucket_of(tokens):
    if tokens < 50_000:
        return "<50K"
    if tokens < 150_000:
        return "50-150K"
    if tokens < 300_000:
        return "150-300K"
    return ">300K"


def main():
    t0 = time.time()
    sub_files, skipped = discover_sub_files()
    print(f"Subagent-Dateien gefunden: {len(sub_files) + skipped}, <=60 Tage: {len(sub_files)}, uebersprungen (aelter): {skipped}", file=sys.stderr)

    files_ok = 0
    files_failed = 0
    files_empty = 0

    resume_write_tokens = []  # Kennzahl 1: Token-Groesse jeder Resume-Write-Antwort
    first_msg_tokens = []  # Kennzahl 2: cache_creation der ersten Assistant-Nachricht je Transkript
    max_cache_read_with_resume = []  # Kennzahl 3a
    max_cache_read_without_resume = []  # Kennzahl 3b
    work_after_resume = []  # Kennzahl 4: Anzahl Assistant-Nachrichten je Resume-Fall

    n = len(sub_files)
    for i, path in enumerate(sub_files):
        if (i + 1) % 200 == 0 or (i + 1) == n:
            print(f"{i+1}/{n} Dateien verarbeitet...", file=sys.stderr, flush=True)

        result = process_file(path)
        if result is None:
            files_failed += 1
            continue
        files_ok += 1

        groups = result["groups"]
        resume_after = result["resume_after"]

        if not groups:
            files_empty += 1
            continue

        # Kennzahl 2: Startkosten
        first_msg_tokens.append(groups[0]["cache_creation_input_tokens"])

        # Kennzahl 3: Endgroesse des Kontexts
        max_cache_read = max(g["cache_read_input_tokens"] for g in groups)
        if resume_after:
            max_cache_read_with_resume.append(max_cache_read)
        else:
            max_cache_read_without_resume.append(max_cache_read)

        # Kennzahl 1 + 4: Resume-Faelle
        resume_indices = sorted(resume_after)
        for pos, r in enumerate(resume_indices):
            if r + 1 >= len(groups):
                # Resume ohne nachfolgende Assistant-Antwort im Transkript
                # (keine Cache-Creation messbar) -- wie im Basisskript
                # nicht als Resume-Write gezaehlt.
                continue
            curg = groups[r + 1]
            resume_write_tokens.append(curg["cache_creation_input_tokens"])

            next_r = resume_indices[pos + 1] if pos + 1 < len(resume_indices) else None
            end_bound = next_r if next_r is not None else (len(groups) - 1)
            work_after_resume.append(end_bound - r)

    elapsed = time.time() - t0

    def fmt(v):
        if v is None:
            return "n/a"
        return f"{v:,.0f}".replace(",", ".")

    print("\n=== ERGEBNIS ===")
    print(f"Ausgewertete Transkripte (files_ok): {files_ok}")
    print(f"Fehlgeschlagene Dateien: {files_failed}")
    print(f"Leere Transkripte (0 Assistant-Nachrichten): {files_empty}")
    print(f"Transkripte mit >=1 Resume: {len(max_cache_read_with_resume)}")
    print(f"Transkripte ohne Resume: {len(max_cache_read_without_resume)}")
    print(f"Resume-Faelle (mit messbarer Folge-Antwort): {len(resume_write_tokens)}")

    print("\n-- 1) Resume-Writes: Token-Groesse --")
    s1 = stats_line(resume_write_tokens)
    print(f"n={s1['n']} median={fmt(s1['median'])} mean={fmt(s1['mean'])} p25={fmt(s1['p25'])} p75={fmt(s1['p75'])}")
    buckets = {"<50K": [0, 0], "50-150K": [0, 0], "150-300K": [0, 0], ">300K": [0, 0]}
    for tok in resume_write_tokens:
        b = bucket_of(tok)
        buckets[b][0] += 1
        buckets[b][1] += tok
    for b, (cnt, tok_sum) in buckets.items():
        print(f"Bucket {b}: n={cnt} tokens_sum={fmt(tok_sum)}")

    print("\n-- 2) Startkosten frischer Agent (erste Assistant-Nachricht) --")
    s2 = stats_line(first_msg_tokens)
    print(f"n={s2['n']} median={fmt(s2['median'])} p25={fmt(s2['p25'])} p75={fmt(s2['p75'])}")

    print("\n-- 3) Endgroesse Kontext (max cache_read je Transkript) --")
    s3a = stats_line(max_cache_read_with_resume)
    s3b = stats_line(max_cache_read_without_resume)
    print(f"mit Resume: n={s3a['n']} median={fmt(s3a['median'])} p25={fmt(s3a['p25'])} p75={fmt(s3a['p75'])}")
    print(f"ohne Resume: n={s3b['n']} median={fmt(s3b['median'])} p25={fmt(s3b['p25'])} p75={fmt(s3b['p75'])}")

    print("\n-- 4) Arbeit nach Resume (Anzahl Assistant-Nachrichten) --")
    s4 = stats_line(work_after_resume)
    print(f"n={s4['n']} median={fmt(s4['median'])} p25={fmt(s4['p25'])} p75={fmt(s4['p75'])}")

    print(f"\nLaufzeit: {elapsed:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
