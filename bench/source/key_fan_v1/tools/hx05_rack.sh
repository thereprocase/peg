#!/usr/bin/env bash
# HX05 (owner, 2026-10-08): one single-set T-handle rack end to end, unattended: candidate pass, install swing,
# fit-coupon blocks + slice, wait for the exact check and stiffness screen, then the review evidence.
#   tools/hx05_rack.sh <ID e.g. HX05A> <tee set json> <layout json> <coupon blocks> "<name>"
set -euo pipefail
cd "$(dirname "$0")/.."
export HX_ID=$1 SHORT_TEE_SET=$2 HX_COUPON=$4 HX_NAME=$5 COUPON_BLOCKS=$4
export SHORT_TONLY=1 SHORT_CELLS=10 SHORT_PLATE_HALF=118 SHORT_REC_CELLS=9 XENV=141 SHORT_HMAX=232 SHORT_TEE_EQUAL=39.2
export HX4S_GUSSET=cheek HX4S_LAYOUT=$3 HX_FAMILY=tee-racks HX4_VERSION=1
OUT=${HX_ID,,}_v1; COUT=${HX_ID,,}_coupon
# Legolas (2026-10-08): coupon from the same build, swing + coupon slice alongside check/fea, coarser FEA mesh,
# capped CalculiX threads (three racks at once), 5 mm check sweep steps, 1 deg swing steps
export COUPON_OUT=$COUT RUN_SWING=1 FEA_H=10 FEA_THREADS=4 CHECK_STEP=5 SWING_STEP=1
rm -f "$OUT/checks.json" "$OUT/fea.json" "$OUT/swing.json"
tools/run_candidate.sh "$OUT" "$3"
for i in $(seq 1 360); do [ -f "$OUT/checks.json" ] && [ -f "$OUT/fea.json" ] && [ -f "$OUT/swing.json" ] && grep -q . "$COUT/slice.log" 2>/dev/null && break; sleep 10; done
tail -n 2 "$OUT/swing.log" | head -n 1
python tools/evidence.py "$OUT" "$COUT" 2>&1 | tail -n 2
