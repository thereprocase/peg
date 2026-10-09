# HX05 source moved

The HX05 pipeline and selected layouts now live in [tee_racks_v1](../../tee_racks_v1/README.md). This isolates its changes from the exact source hashes attached to published HX04 v2 evidence. The original HX04 pipeline remains in `key_fan_v1`.

[Branch reconciliation](RECONCILIATION.md) was completed before layout changes.

From the repository root on the owner Windows machine: `python bench/source/tee_racks_v1/tools/hx05_build.py`. Native CAD, FEA, slicing and physical qualification remain pending.
