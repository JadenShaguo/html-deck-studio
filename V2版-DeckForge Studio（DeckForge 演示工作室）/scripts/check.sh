#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 /absolute/or/relative/path/deck.html [source|viewer]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${2:-auto}"

python3 "$SCRIPT_DIR/check_presentation.py" "$1" --mode "$MODE"
