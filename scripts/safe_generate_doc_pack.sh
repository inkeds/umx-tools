#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT_PATH="${1:-$SKILL_DIR/assets/requirements.example.json}"
OUTPUT_ROOT="${2:-./umx-doc-pack}"
COMBO="${3:-auto}"
MODE="${4:-auto}"

if [[ ! -f "$INPUT_PATH" ]]; then
  echo "Input JSON not found: $INPUT_PATH" >&2
  exit 1
fi

python3 "$SCRIPT_DIR/generate_doc_pack.py" \
  --input "$INPUT_PATH" \
  --output "$OUTPUT_ROOT" \
  --combo "$COMBO" \
  --mode "$MODE"
