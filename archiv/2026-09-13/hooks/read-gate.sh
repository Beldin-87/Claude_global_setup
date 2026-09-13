#!/usr/bin/env bash
# PreToolUse-Hook (matcher: Read)
# Blockiert vollstaendige Lesezugriffe auf Dateien in Bibliotheks-/Build-Ordnern,
# auf Lockfiles und auf grosse Dateien. Gezieltes Lesen mit offset/limit bleibt erlaubt.
# Exit 0 = Lesen erlaubt, Exit 2 = Lesen blockiert (stderr geht an Claude).
set -u

[ "${CLAUDE_HOOK_READ_GATE:-}" = "off" ] && exit 0

# --- jq auflösen: erst PATH, dann voller Pfad (per CLAUDE_HOOK_JQ überschreibbar) ---
JQ_FALLBACK="${CLAUDE_HOOK_JQ:-C:/Users/szieg/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe/jq.exe}"
if command -v jq >/dev/null 2>&1; then
  JQ="jq"
elif [ -x "$JQ_FALLBACK" ]; then
  JQ="$JQ_FALLBACK"
else
  printf 'Lese-Schranke: jq nicht gefunden (weder im PATH noch unter "%s"). Die Prüfung konnte nicht laufen.\n' "$JQ_FALLBACK" >&2
  exit 2
fi

input=$(cat)
jqr() { printf '%s' "$input" | "$JQ" -r "$1" 2>/dev/null | tr -d '\r'; }

file_path=$(jqr '.tool_input.file_path // empty')
[ -n "$file_path" ] || exit 0

# --- gezieltes Lesen (offset/limit > 0) ist immer erlaubt ---
offset=$(jqr '.tool_input.offset // empty')
limit=$(jqr '.tool_input.limit // empty')
is_positive() {
  case "$1" in
    '' | *[!0-9.]*) return 1 ;;
  esac
  awk -v n="$1" 'BEGIN { exit !(n > 0) }'
}
if is_positive "$offset" || is_positive "$limit"; then
  exit 0
fi

# --- Pfad normalisieren: Backslash -> Slash, Vergleich case-insensitive ---
BS=$(printf '\134')
norm_path=${file_path//"$BS"//}
low=${norm_path,,}

# --- Bild-/PDF-Formate: das Read-Tool verarbeitet diese selbst ---
case "$low" in
  *.png | *.jpg | *.jpeg | *.gif | *.webp | *.svg | *.pdf | *.ipynb)
    exit 0
    ;;
esac

# --- Junk-Ordner als echte Pfadsegmente ---
JUNK_DIRS="node_modules .git dist build out coverage __pycache__ .venv venv .next .nuxt .cache .turbo target vendor"
wrapped="/$low/"
for seg in $JUNK_DIRS; do
  case "$wrapped" in
    *"/$seg/"*)
      printf 'Lese-Schranke: %s\nGrund: Junk-Ordner "%s"\nInhalte generierter oder installierter Ordner sind selten nötig.\nNutze Grep mit einem Suchbegriff, oder Read mit offset und limit für den benötigten Ausschnitt.\n' "$file_path" "$seg" >&2
      exit 2
      ;;
  esac
done

# --- Lockfiles ---
base=${low##*/}
case "$base" in
  package-lock.json | yarn.lock | pnpm-lock.yaml | cargo.lock | poetry.lock | uv.lock | composer.lock | gemfile.lock)
    printf 'Lese-Schranke: %s\nGrund: Lockfile\nNutze Grep mit einem Suchbegriff, oder Read mit offset und limit für den benötigten Ausschnitt.\n' "$file_path" >&2
    exit 2
    ;;
esac

# --- Größenschwelle ---
MAX_BYTES="${CLAUDE_HOOK_READ_MAX_BYTES:-100000}"

[ -e "$norm_path" ] || exit 0
[ -d "$norm_path" ] && exit 0

size=$(stat -c %s "$norm_path" 2>/dev/null)
if [ -z "$size" ]; then
  size=$(wc -c < "$norm_path" 2>/dev/null | tr -d ' ')
fi
[ -n "$size" ] || exit 0

if [ "$size" -gt "$MAX_BYTES" ] 2>/dev/null; then
  size_kb=$(awk -v b="$size" 'BEGIN { printf "%.0f", b / 1000 }')
  max_kb=$(awk -v b="$MAX_BYTES" 'BEGIN { printf "%.0f", b / 1000 }')
  printf 'Lese-Schranke: %s\nGrund: Größe %s KB über %s KB\nNutze Grep mit einem Suchbegriff, oder Read mit offset und limit für den benötigten Ausschnitt.\n' "$file_path" "$size_kb" "$max_kb" >&2
  exit 2
fi

exit 0
