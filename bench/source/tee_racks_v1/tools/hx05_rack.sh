#!/usr/bin/env bash
# Bounded Windows review runner, usable from Git Bash; see ../hx05/README.md.
# tools/hx05_rack.sh HX05A   (or omit the ID to build all three)
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -gt 0 && "$1" == HX05* ]]; then
  rack=$1; shift
  exec python tools/hx05_build.py --rack "$rack" "$@"
fi
exec python tools/hx05_build.py "$@"
