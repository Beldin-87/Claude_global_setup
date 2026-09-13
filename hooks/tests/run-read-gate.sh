#!/usr/bin/env bash
# Regressionsmatrix fuer read-gate.sh. Laeuft ohne Umgebungsvariablen und ohne
# Vorbereitung: die Fixtures werden in einem eigenen Temp-Ordner angelegt und
# am Ende wieder geloescht.
set -u

GATE="$HOME/.claude/hooks/read-gate.sh"

if command -v jq >/dev/null 2>&1; then
  JQ="jq"
else
  JQ="C:/Users/szieg/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe/jq.exe"
fi

FIXDIR=$(mktemp -d)
T_PAYLOAD=$(mktemp)
trap 'rm -f "$T_PAYLOAD"; rm -rf "$FIXDIR"' EXIT

mkdir -p "$FIXDIR/build" "$FIXDIR/node_modules/pkg" "$FIXDIR/dist" "$FIXDIR/leerer-ordner"
echo "# Doku"                      > "$FIXDIR/build/x.md"
echo "Notiz"                       > "$FIXDIR/build/notes.txt"
echo "console.log(1)"              > "$FIXDIR/build/x.js"
echo "# readme"                    > "$FIXDIR/node_modules/pkg/README.md"
echo "<html></html>"               > "$FIXDIR/dist/index.html"
echo '{"name":"x"}'                > "$FIXDIR/package-lock.json"
echo "klein"                       > "$FIXDIR/klein.txt"
printf '\x89PNG\r\n1a\n'           > "$FIXDIR/build/bild.png"
awk 'BEGIN { for (i = 0; i < 110000; i++) printf "a" }' > "$FIXDIR/build/big.md"

pass=0; fail=0
printf '%-4s %-46s %s\n' "ERW" "FALL" "ERGEBNIS"

run_case() {
  local expect="$1" path="$2" limit="$3" label="$4"
  if [ -n "$limit" ]; then
    "$JQ" -n --arg p "$path" --argjson l "$limit" \
      '{session_id:"t",transcript_path:"x",cwd:"/tmp",hook_event_name:"PreToolUse",tool_name:"Read",tool_input:{file_path:$p, limit:$l}}' > "$T_PAYLOAD"
  else
    "$JQ" -n --arg p "$path" \
      '{session_id:"t",transcript_path:"x",cwd:"/tmp",hook_event_name:"PreToolUse",tool_name:"Read",tool_input:{file_path:$p}}' > "$T_PAYLOAD"
  fi
  err=$(bash "$GATE" < "$T_PAYLOAD" 2>&1 >/dev/null); rc=$?
  if [ "$rc" -eq "$expect" ]; then
    res="OK"; pass=$((pass+1))
  else
    res="FEHLER (rc=$rc, erwartet=$expect, msg=${err:0:70})"; fail=$((fail+1))
  fi
  printf '%-4s %-46s %s\n' "$expect" "$label" "$res"
}

run_case 0 "$FIXDIR/build/x.md" ""   "build/x.md frei"
run_case 0 "$FIXDIR/build/notes.txt" "" "build/notes.txt frei"
run_case 2 "$FIXDIR/build/x.js" ""   "build/x.js blockiert"
run_case 0 "$FIXDIR/node_modules/pkg/README.md" "" "node_modules/pkg/README.md frei"
run_case 2 "$FIXDIR/dist/index.html" "" "dist/index.html blockiert"
run_case 0 "$FIXDIR/dist/index.html" "50" "dist/index.html mit limit 50 frei"
run_case 2 "$FIXDIR/package-lock.json" "" "package-lock.json blockiert"
run_case 2 "$FIXDIR/build/big.md" "" "build/big.md >100 KB blockiert"
run_case 0 "$FIXDIR/klein.txt" ""   "klein.txt frei"
run_case 0 "$FIXDIR/nicht-vorhanden.dat" "" "nicht existierende Datei frei"
run_case 0 "$FIXDIR/leerer-ordner" "" "Verzeichnis frei"
run_case 0 "$FIXDIR/build/bild.png" "" "build/bild.png frei"

echo "----"
echo "bestanden: $pass   fehlgeschlagen: $fail"
