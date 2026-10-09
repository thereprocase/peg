# HX05 branch reconciliation — 2026-10-08

Completed before layout or pipeline changes.

- Requested dev-box main: `7d7b2fc7b3a247175a9d6e5113c681e19e873aec`.
- Published main, confirmed with `git ls-remote origin refs/heads/main`: `2d509de64a004053536e96282084c970441bce6c`.
- Starting HX05: `c108ee4d8fdfda912aecf81bc551a740966eb0a6`.
- `git merge-base 7d7b2fc hx05` returns exactly `7d7b2fc`; `git merge-base --is-ancestor 7d7b2fc hx05` succeeds.
- Eleven main commits follow `7d7b2fc`, including HX04 v1/v2. The key-fan pipeline does not exist in the `7d7b2fc` tree; it was added later. HX05 adds its T-only changes to published HX04 v2.
- Dev-box main checkout has no tracked edits, including none in `bench/source/key_fan_v1`; its unrelated untracked `result.json` is left alone.

Decision: retain the existing linear HX05 history. Both the native-connector navigation work and HX04 pipeline are already inherited. A rebase onto the older main checkout or replacing pipeline files would discard later work. No merge, forced push or main checkout mutation is needed. The requested commit is already published through main ancestry, so no redundant push to main is needed.

The handoff's statement that this commit is unpushed and has conflicting changes to the key-fan pipeline does not match the observed Git history. This record supersedes that statement only; tool dimensions and CAD qualification remain unresolved.
