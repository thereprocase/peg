#!/usr/bin/env bash
# Full HX04 candidate pass: build, exact check, overhang gate, inked renders, slice, stiffness screen.
#   tools/run_candidate.sh <out dir> <layout json in study/>
# Env (current design): SHORT_CELLS SHORT_PLATE_HALF SHORT_REC_CELLS XENV SHORT_HMAX SHORT_HAND HX4S_GUSSET HX4S_WEB_Y
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=$1; export HX4S_LAYOUT=$2
FC=${FREECAD_PYTHON:?set FREECAD_PYTHON to the FreeCAD 1.1 python executable}
mkdir -p "$OUT"
timeout 2400 "$FC" build_short.py --quick "$OUT" > "$OUT/build.log" 2>&1
tail -n 1 "$OUT/build.log"
(HX4_BUILD=build_short.py timeout 5400 "$FC" check.py "$OUT" > "$OUT/check.log" 2>&1 &)
(timeout 7000 python fea_run.py "$OUT" > "$OUT/fea.log" 2>&1 &)
if [ -n "${RUN_SWING:-}" ]; then (timeout 3600 "$FC" swing.py "$OUT" > "$OUT/swing.log" 2>&1 &); fi
if [ -n "${COUPON_OUT:-}" ]; then (cd tools && timeout 1700 python quickslice.py "../$COUPON_OUT/print.stl" "../$COUPON_OUT/slice" > "../$COUPON_OUT/slice.log" 2>&1 &); fi
cd tools
timeout 900 python gate3.py "../$OUT" > "../$OUT/gate.log" 2>&1 || true
head -n 4 "../$OUT/gate.log"
python glb.py "../$OUT" > /dev/null
OUTDIR=wb VIEWS='[["loaded","hero","30deg 70deg auto"],["installed","empty","30deg 70deg auto"],["loaded","front","0deg 85deg auto"],["loaded","side","90deg 85deg auto"],["installed","below","-35deg 115deg auto"],["print","print","35deg 60deg auto"]]' timeout 600 node shots3.cjs "../$OUT" > /dev/null
timeout 1700 python quickslice.py "../$OUT/print.stl" "../$OUT/slice" > "../$OUT/slice.log" 2>&1 || true
head -n 1 "../$OUT/slice.log"; grep "^Support " "../$OUT/slice.log" || true
if [ -f "../$OUT/print_solid.stl" ]; then
  timeout 2600 python slice3mf.py "../$OUT" "../$OUT/slice_solid" > "../$OUT/slice_solid.log" 2>&1 || true
  echo "with solid zones:"; head -n 1 "../$OUT/slice_solid.log"; grep -i "^Sparse infill\|^Internal solid\|^Support " "../$OUT/slice_solid.log" || true
fi
