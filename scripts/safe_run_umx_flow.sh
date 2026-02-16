#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT_PATH="${1:-$SKILL_DIR/assets/requirements.example.json}"
OUTPUT_ROOT="${2:-./umx-output}"
PATH_CHOICE="${3:-ask}"
COMBO="${4:-auto}"
MODE="${5:-single-file}"
TRAD_DOCS="${6:-prd,architecture,api,database}"
COMMAND_MODE="${7:-}"
ALLOW_PLACEHOLDER="${UMX_ALLOW_PLACEHOLDER:-0}"

if [[ ! -f "$INPUT_PATH" ]]; then
  echo "Input JSON not found: $INPUT_PATH" >&2
  exit 1
fi

CMD=(
  python3 "$SCRIPT_DIR/run_umx_flow.py"
  --input "$INPUT_PATH"
  --output "$OUTPUT_ROOT"
  --path "$PATH_CHOICE"
  --combo "$COMBO"
  --mode "$MODE"
  --traditional-docs "$TRAD_DOCS"
)

if [[ -n "$COMMAND_MODE" ]]; then
  CMD+=(--command "$COMMAND_MODE")
fi

if [[ "$ALLOW_PLACEHOLDER" == "1" ]]; then
  CMD+=(--allow-placeholder)
fi

"${CMD[@]}"
