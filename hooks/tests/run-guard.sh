#!/usr/bin/env bash
# Regressionsmatrix fuer guard-destructive.sh. Laeuft ohne Umgebungsvariablen:
# cases.txt liegt neben diesem Skript, das Payload landet in einer Temp-Datei.
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES="$DIR/cases.txt"
GUARD="$HOME/.claude/hooks/guard-destructive.sh"

if command -v jq >/dev/null 2>&1; then
  JQ="jq"
else
  JQ="C:/Users/szieg/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe/jq.exe"
fi

T_PAYLOAD=$(mktemp)
trap 'rm -f "$T_PAYLOAD"' EXIT

pass=0; fail=0
printf '%-6s %-11s %-46s %-4s %s\n' "ERW" "TOOL" "BEFEHL" "RC" "ERGEBNIS"
while read -r expect tool cmd; do
  [ -n "${expect:-}" ] || continue
  "$JQ" -n --arg t "$tool" --arg c "$cmd" \
    '{session_id:"t",transcript_path:"x",cwd:"/tmp",hook_event_name:"PreToolUse",tool_name:$t,tool_input:{command:$c}}' > "$T_PAYLOAD"
  err=$(bash "$GUARD" < "$T_PAYLOAD" 2>&1 >/dev/null); rc=$?
  muster=$(printf '%s' "$err" | head -1 | sed -n 's/.*Muster "\(.*\)".*/\1/p')
  if [ "$expect" = "BLOCK" ]; then
    if [ "$rc" -eq 2 ] && [ -n "$muster" ]; then res="OK  -> $muster"; pass=$((pass+1));
    else res="FEHLER (rc=$rc, msg=${err:0:60})"; fail=$((fail+1)); fi
  else
    if [ "$rc" -eq 0 ] && [ -z "$err" ]; then res="OK  (frei)"; pass=$((pass+1));
    else res="FEHLER (rc=$rc, msg=${err:0:60})"; fail=$((fail+1)); fi
  fi
  printf '%-6s %-11s %-46s %-4s %s\n' "$expect" "$tool" "$cmd" "$rc" "$res"
done < "$CASES"
echo "----"
echo "bestanden: $pass   fehlgeschlagen: $fail"
