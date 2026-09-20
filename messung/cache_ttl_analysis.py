"""
Analyse von Claude-Code-Transkripten: Wie viele Prompt-Cache-Writes in
Subagents sind "Re-Writes" nach einer Cache-TTL-Luecke (> 5 Minuten)?

Liest NUR, streamt JSONL zeilenweise, laedt keine ganzen Dateien in den
Speicher. Keine Nachrichtentexte werden im Ergebnis gespeichert -- nur
Zahlen, Zeitstempel, Modellnamen und Dateinamen der Transkripte.
"""

import glob
import json
import os
import sys
import time
from datetime import datetime, timezone
from collections import defaultdict

BASE = r"C:\Users\szieg\.claude\projects"
CUTOFF_DAYS = 60
REWRITE_THRESHOLD = 50_000
GAP_THRESHOLD_SEC = 300
SESSION_PAUSE_SEC = 3 * 3600


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


def short_project_name(path):
    # Projektordner-Kurzname: Ordnername unter BASE, gekuerzt
    rel = os.path.relpath(path, BASE)
    parts = rel.split(os.sep)
    proj = parts[0]
    # kuerzen: nur die letzten 2 Pfadsegmente des urspruenglichen Repo-Pfads
    segs = [s for s in proj.split("-") if s]
    short = "-".join(segs[-3:]) if len(segs) > 3 else proj
    if len(short) > 40:
        short = short[-40:]
    return short


def short_label(path, is_subagent):
    proj = short_project_name(path)
    base_name = os.path.basename(path)
    if is_subagent:
        agent_id = base_name.replace("agent-", "").replace(".jsonl", "")
        return f"{proj}/{agent_id[:12]}"
    else:
        sess_id = base_name.replace(".jsonl", "")
        return f"{proj}/{sess_id[:8]}"


def discover_files():
    sub_files = glob.glob(os.path.join(BASE, "**", "subagents", "agent-*.jsonl"), recursive=True)
    all_jsonl = glob.glob(os.path.join(BASE, "**", "*.jsonl"), recursive=True)
    sep = os.sep + "subagents" + os.sep
    main_files = [f for f in all_jsonl if sep not in f]
    cutoff = time.time() - CUTOFF_DAYS * 86400
    sub_recent = [f for f in sub_files if os.path.getmtime(f) >= cutoff]
    main_recent = [f for f in main_files if os.path.getmtime(f) >= cutoff]
    skipped_sub = len(sub_files) - len(sub_recent)
    skipped_main = len(main_files) - len(main_recent)
    return sub_recent, main_recent, skipped_sub, skipped_main


def process_file(path, is_subagent):
    """Liest eine Transkriptdatei, dedupliziert Assistant-Fragmente nach
    message.id zu logischen 'Turns' und gibt eine Ergebnisstruktur zurueck."""

    groups = []  # chronologisch geordnete deduplizierte Assistant-Turns
    resume_after = set()  # Indizes in groups: Resume-Muster danach erkannt
    parsed_assistant_lines = 0
    total_lines = 0
    json_errors = 0

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
            total_lines += 1
            try:
                obj = json.loads(raw_line)
            except Exception:
                json_errors += 1
                continue

            t = obj.get("type")
            if t == "assistant":
                parsed_assistant_lines += 1
                msg = obj.get("message") or {}
                mid = msg.get("id")
                ts_raw = obj.get("timestamp")
                content = msg.get("content")
                has_tu = content_has_tool_use(content)

                if cur is not None and cur["id"] == mid and mid is not None:
                    if has_tu:
                        cur["has_tool_use"] = True
                    continue

                if cur is not None:
                    groups.append(cur)

                usage = msg.get("usage") or {}
                cache_cre = usage.get("cache_creation") or {}
                cur = {
                    "id": mid,
                    "ts_raw": ts_raw,
                    "ts": parse_ts(ts_raw),
                    "model": msg.get("model"),
                    "input_tokens": usage.get("input_tokens") or 0,
                    "cache_creation_input_tokens": usage.get("cache_creation_input_tokens") or 0,
                    "cache_read_input_tokens": usage.get("cache_read_input_tokens") or 0,
                    "ephemeral_5m": cache_cre.get("ephemeral_5m_input_tokens"),
                    "ephemeral_1h": cache_cre.get("ephemeral_1h_input_tokens"),
                    "has_tool_use": has_tu,
                }
            else:
                if cur is not None:
                    groups.append(cur)
                    closed_index = len(groups) - 1
                    if is_subagent and t == "user" and not groups[closed_index]["has_tool_use"]:
                        content = (obj.get("message") or {}).get("content")
                        if not content_is_tool_result_only(content):
                            resume_after.add(closed_index)
                    cur = None
    if cur is not None:
        groups.append(cur)

    return {
        "path": path,
        "groups": groups,
        "resume_after": resume_after,
        "total_lines": total_lines,
        "parsed_assistant_lines": parsed_assistant_lines,
        "json_errors": json_errors,
    }


def analyse(files, is_subagent, label):
    agg = {
        "files_ok": 0,
        "files_failed": 0,
        "total_lines": 0,
        "parsed_assistant": 0,
        "json_errors": 0,
        "sum_cache_creation": 0,
        "sum_cache_read": 0,
        "sum_input": 0,
        "sum_ephemeral_5m": 0,
        "sum_ephemeral_1h": 0,
        "ephemeral_5m_seen": False,
        "ephemeral_1h_seen": False,
        "rewrites": [],  # dicts: tokens, gap, gap_over_300, model, file
        "resume_writes": [],  # dicts: tokens, gap, model, file
        "gaps_all": [],  # alle Abstaende zwischen aufeinanderfolgenden Assistant-Turns (fuer Histogramm)
        "per_file": [],  # pro Datei: label, model(most common), max_cache_read, n_rewrites, rewrite_tokens
        "by_model": defaultdict(lambda: {"cache_write": 0, "rewrite_count": 0, "rewrite_tokens": 0}),
        "min_ts": None,
        "max_ts": None,
    }

    n = len(files)
    for i, path in enumerate(files):
        if (i + 1) % 100 == 0 or (i + 1) == n:
            print(f"[{label}] {i+1}/{n} Dateien verarbeitet...", file=sys.stderr, flush=True)

        result = process_file(path, is_subagent)
        if result is None:
            agg["files_failed"] += 1
            continue
        agg["files_ok"] += 1
        agg["total_lines"] += result["total_lines"]
        agg["parsed_assistant"] += result["parsed_assistant_lines"]
        agg["json_errors"] += result["json_errors"]

        groups = result["groups"]
        file_rewrite_count = 0
        file_rewrite_tokens = 0
        file_max_cache_read = 0
        model_counts = defaultdict(int)

        for g in groups:
            agg["sum_cache_creation"] += g["cache_creation_input_tokens"]
            agg["sum_cache_read"] += g["cache_read_input_tokens"]
            agg["sum_input"] += g["input_tokens"]
            if g["ephemeral_5m"] is not None:
                agg["ephemeral_5m_seen"] = True
                agg["sum_ephemeral_5m"] += g["ephemeral_5m"]
            if g["ephemeral_1h"] is not None:
                agg["ephemeral_1h_seen"] = True
                agg["sum_ephemeral_1h"] += g["ephemeral_1h"]
            if g["model"]:
                model_counts[g["model"]] += 1
                agg["by_model"][g["model"]]["cache_write"] += g["cache_creation_input_tokens"]
            if g["ts"] is not None:
                if agg["min_ts"] is None or g["ts"] < agg["min_ts"]:
                    agg["min_ts"] = g["ts"]
                if agg["max_ts"] is None or g["ts"] > agg["max_ts"]:
                    agg["max_ts"] = g["ts"]
            if g["cache_read_input_tokens"] > file_max_cache_read:
                file_max_cache_read = g["cache_read_input_tokens"]

        for i2 in range(1, len(groups)):
            prev = groups[i2 - 1]
            curg = groups[i2]
            if prev["ts"] is None or curg["ts"] is None:
                continue
            gap = (curg["ts"] - prev["ts"]).total_seconds()

            if is_subagent and gap <= SESSION_PAUSE_SEC:
                agg["gaps_all"].append(gap)

            if (curg["cache_creation_input_tokens"] >= REWRITE_THRESHOLD
                    and prev["cache_read_input_tokens"] >= REWRITE_THRESHOLD):
                rw = {
                    "tokens": curg["cache_creation_input_tokens"],
                    "gap": gap,
                    "gap_over_300": gap > GAP_THRESHOLD_SEC,
                    "model": curg["model"],
                    "file": path,
                }
                agg["rewrites"].append(rw)
                file_rewrite_count += 1
                file_rewrite_tokens += curg["cache_creation_input_tokens"]
                if curg["model"]:
                    agg["by_model"][curg["model"]]["rewrite_count"] += 1
                    agg["by_model"][curg["model"]]["rewrite_tokens"] += curg["cache_creation_input_tokens"]

            if is_subagent and (i2 - 1) in result["resume_after"]:
                agg["resume_writes"].append({
                    "tokens": curg["cache_creation_input_tokens"],
                    "gap": gap,
                    "model": curg["model"],
                    "file": path,
                })

        if is_subagent:
            most_common_model = max(model_counts.items(), key=lambda kv: kv[1])[0] if model_counts else None
            agg["per_file"].append({
                "path": path,
                "model": most_common_model,
                "max_cache_read": file_max_cache_read,
                "n_rewrites": file_rewrite_count,
                "rewrite_tokens": file_rewrite_tokens,
            })

    return agg


def fmt_int(n):
    return f"{n:,}".replace(",", ".")


def main():
    t0 = time.time()
    sub_files, main_files, skipped_sub, skipped_main = discover_files()
    print(f"Subagent-Dateien (<=60 Tage): {len(sub_files)}, uebersprungen (aelter): {skipped_sub}")
    print(f"Hauptsession-Dateien (<=60 Tage): {len(main_files)}, uebersprungen (aelter): {skipped_main}")

    sub_agg = analyse(sub_files, True, "SUB")
    main_agg = analyse(main_files, False, "MAIN")

    out = {}

    def summarize(agg, is_subagent):
        s = {
            "files_ok": agg["files_ok"],
            "files_failed": agg["files_failed"],
            "total_lines": agg["total_lines"],
            "parsed_assistant": agg["parsed_assistant"],
            "json_errors": agg["json_errors"],
            "sum_cache_creation": agg["sum_cache_creation"],
            "sum_cache_read": agg["sum_cache_read"],
            "sum_input": agg["sum_input"],
            "ephemeral_5m_seen": agg["ephemeral_5m_seen"],
            "ephemeral_1h_seen": agg["ephemeral_1h_seen"],
            "sum_ephemeral_5m": agg["sum_ephemeral_5m"],
            "sum_ephemeral_1h": agg["sum_ephemeral_1h"],
            "min_ts": agg["min_ts"].isoformat() if agg["min_ts"] else None,
            "max_ts": agg["max_ts"].isoformat() if agg["max_ts"] else None,
            "n_rewrites": len(agg["rewrites"]),
            "sum_rewrite_tokens": sum(r["tokens"] for r in agg["rewrites"]),
            "n_rewrites_gap300": sum(1 for r in agg["rewrites"] if r["gap_over_300"]),
            "sum_rewrite_tokens_gap300": sum(r["tokens"] for r in agg["rewrites"] if r["gap_over_300"]),
            "by_model": {m: dict(v) for m, v in agg["by_model"].items()},
        }
        if s["sum_cache_creation"] > 0:
            s["rewrite_ratio_pct"] = 100.0 * s["sum_rewrite_tokens"] / s["sum_cache_creation"]
            s["rewrite_gap300_ratio_pct"] = 100.0 * s["sum_rewrite_tokens_gap300"] / s["sum_cache_creation"]
        else:
            s["rewrite_ratio_pct"] = 0.0
            s["rewrite_gap300_ratio_pct"] = 0.0
        return s

    out["sub_summary"] = summarize(sub_agg, True)
    out["main_summary"] = summarize(main_agg, False)

    # Resume-writes: Top 10 nach Tokens
    resume_sorted = sorted(sub_agg["resume_writes"], key=lambda r: r["tokens"], reverse=True)[:10]
    out["resume_top10"] = [
        {
            "file": short_label(r["file"], True),
            "model": r["model"],
            "tokens": r["tokens"],
            "gap_sec": round(r["gap"], 1),
        }
        for r in resume_sorted
    ]
    out["resume_total_count"] = len(sub_agg["resume_writes"])
    out["resume_total_tokens"] = sum(r["tokens"] for r in sub_agg["resume_writes"])

    # Top 10 Subagents nach Re-Write-Tokens
    top_files = sorted(sub_agg["per_file"], key=lambda f: f["rewrite_tokens"], reverse=True)[:10]
    out["top10_subagents"] = [
        {
            "file": short_label(f["path"], True),
            "model": f["model"],
            "max_cache_read": f["max_cache_read"],
            "n_rewrites": f["n_rewrites"],
            "rewrite_tokens": f["rewrite_tokens"],
        }
        for f in top_files
    ]

    # Histogramm Tool-Call-Dauern (Subagents, Abstaende zwischen Assistant-Turns, Pausen>3h raus)
    hist = {"<1min": 0, "1-5min": 0, "5-15min": 0, ">15min": 0}
    for gap in sub_agg["gaps_all"]:
        if gap < 60:
            hist["<1min"] += 1
        elif gap < 300:
            hist["1-5min"] += 1
        elif gap < 900:
            hist["5-15min"] += 1
        else:
            hist[">15min"] += 1
    out["tool_call_duration_hist"] = hist

    elapsed = time.time() - t0
    out["elapsed_sec"] = round(elapsed, 1)

    print("\n===JSON_RESULT_START===")
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    print("===JSON_RESULT_END===")
    print(f"\nLaufzeit: {elapsed:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
