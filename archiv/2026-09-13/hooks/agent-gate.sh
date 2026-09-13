#!/usr/bin/env bash
# PreToolUse-Hook (matcher: Agent|Task)
# Blockiert Subagent-Aufrufe ohne konkreten Agententyp oder mit dem Allzweck-Typ.
# Exit 0 = Aufruf erlaubt, Exit 2 = Aufruf blockiert (stderr geht an Claude).
set -u

[ "${CLAUDE_HOOK_AGENT_GATE:-}" = "off" ] && exit 0

# --- jq auflösen: erst PATH, dann voller Pfad (per CLAUDE_HOOK_JQ überschreibbar) ---
JQ_FALLBACK="${CLAUDE_HOOK_JQ:-C:/Users/szieg/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe/jq.exe}"
if command -v jq >/dev/null 2>&1; then
  JQ="jq"
elif [ -x "$JQ_FALLBACK" ]; then
  JQ="$JQ_FALLBACK"
else
  printf 'Agenten-Schranke: jq nicht gefunden (weder im PATH noch unter "%s"). Die Prüfung konnte nicht laufen.\n' "$JQ_FALLBACK" >&2
  exit 2
fi

input=$(cat)
subagent_type=$(printf '%s' "$input" | "$JQ" -r '.tool_input.subagent_type // empty' 2>/dev/null | tr -d '\r')

case "$subagent_type" in
  '' | general-purpose | claude)
    anzeige="$subagent_type"
    [ -n "$anzeige" ] || anzeige="leer"
    printf 'Agenten-Schranke: Subagent-Aufruf ohne Rolle beziehungsweise mit Allzweck-Typ `%s`. Arbeitspakete gehen an `executor` (Umsetzung) oder `verifier` (Prüfung mit Befundliste), reine Suchaufgaben an `Explore`, Fragen zu Claude Code an `claude-code-guide`. Setze `subagent_type` entsprechend; für Opus- und Fable-Pakete zusätzlich `model`.\n' "$anzeige" >&2
    exit 2
    ;;
esac

exit 0
