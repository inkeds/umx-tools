#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT_PATH="${1:-$SKILL_DIR/assets/requirements.example.json}"
OUTPUT_ROOT="${2:-./umx-output}"
MAX_INPUT_AGE_SECONDS="${UMX_MAX_INPUT_AGE_SECONDS:-600}"
ALLOW_STALE_INPUT="${UMX_ALLOW_STALE_INPUT:-0}"

if [[ ! -f "$INPUT_PATH" ]]; then
  echo "Input JSON not found: $INPUT_PATH" >&2
  exit 1
fi

if [[ "$ALLOW_STALE_INPUT" != "1" ]]; then
  # Stale check only applies to temporary inputs under /tmp.
  # Repo templates/examples are intentionally reusable and should not be blocked by age.
  if [[ "$INPUT_PATH" == /tmp/* ]]; then
    now_ts="$(date +%s)"
    if stat_ts="$(stat -c %Y "$INPUT_PATH" 2>/dev/null)"; then
      age="$((now_ts - stat_ts))"
      if [[ "$age" -gt "$MAX_INPUT_AGE_SECONDS" ]]; then
        echo "Input JSON appears stale (${age}s old): $INPUT_PATH" >&2
        echo "Refuse to continue to avoid using outdated requirements." >&2
        echo "Tip: regenerate requirements JSON under /tmp/umx-tools-v3/inputs/, or set UMX_ALLOW_STALE_INPUT=1 to bypass." >&2
        exit 1
      fi
    fi
  fi
fi

bash "$SCRIPT_DIR/safe_run_umx_flow.sh" \
  "$INPUT_PATH" \
  "$OUTPUT_ROOT" \
  direct \
  auto \
  single-file \
  prd,architecture,api,database \
  "接受推荐"
