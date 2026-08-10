# Todo Checkpoint

## Current todo

- [x] Convert MTTS source/UI strings to English.
- [x] Move local MTTS translations to the `chinese` namespace.
- [x] Regenerate and reconcile Chinese dialogue/string translations.
- [x] Verify source contracts, repository tests, Ren'Py lint/compile, and generator output.
- [x] Request advisory review and commit the branch.
- [ ] Fast-forward merge the branch into `main` and rerun merged-result checks.

## Active slice

Review completed; final branch integration is active.

## Evidence refs

- `pytest -q tests/test_mtts_language_swap.py` -> 4 passed.
- `pytest -q tests` -> 25 passed, 1 dependency warning.
- Ren'Py 8.2.3 `lint` and `compile` on the disposable merged project -> exit 0.
- `generate-translations.ps1` in disposable staging -> exit 0, 368 Chinese files generated/updated.
- Local MTTS translation IDs -> 47 dialogue blocks, matching staged generator output.
- Local translation entries -> 134 non-empty `old`/`new` pairs.
- `git diff --check` -> clean.
- Advisory review of `63fc46d..24fec5e` -> no Critical/Important findings; ready to merge.

## Blockers

No implementation blockers. The SDK launcher patch is removed; recursive deletion of the Temp staging directory is blocked by the host policy.

## Drift check draft

- Scope: remains limited to MTTS source/UI text, local Chinese translations, provider display data, tests, and task records.
- Compatibility: language routing, persistent keys, event labels, and migration behavior remain unchanged.
- Retirement: local `translate english` ownership is retired; shared `OK`/`Cancel` remain owned by MAS global Chinese translations.
- Review: two Minor follow-ups were recorded: dynamic non-200 provider errors can remain English in Chinese mode, and the contract test could assert exact key coverage.
- Decision: continue.

## Next step

Merge the reviewed implementation into `main`, rerun the verification suite on the merged result, and report the retained Temp staging path for manual cleanup.
