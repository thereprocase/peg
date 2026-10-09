#!/usr/bin/env bash
# Compatibility entry point; HX05 sources are isolated from published HX04 evidence.
set -euo pipefail
exec "$(dirname "$0")/../../tee_racks_v1/tools/hx05_rack.sh" "$@"
