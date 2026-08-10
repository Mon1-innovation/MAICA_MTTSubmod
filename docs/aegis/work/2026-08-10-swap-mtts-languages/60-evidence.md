# Evidence Bundle

## Fresh commands

| Check | Result |
| --- | --- |
| `pytest -q tests/test_mtts_language_swap.py` | 4 passed |
| `pytest -q tests` | 25 passed; one `RequestsDependencyWarning` |
| Ren'Py 8.2.3 `lint` on disposable merged MAS staging | exit 0 |
| Ren'Py 8.2.3 `compile` on disposable merged MAS staging | exit 0 |
| `generate-translations.ps1` with `-Language chinese -NoTodo -KeepTemp` | exit 0; 368 files generated/updated |
| Translation ID comparison against staged generation | 47/47 dialogue blocks match |
| Local translation completeness scan | 134 `old` and 134 non-empty `new` entries |
| `git diff --check` | clean |

## Side effects

- The generator used only `C:\Users\Administrator.DESKTOP-465SP1L\AppData\Local\Temp\mtts-language-swap-staging-final-20260810` as project staging.
- The temporary `zz_mas_cli_translation.rpy` SDK patch was removed after verification.
- Recursive deletion of the staging directory was rejected by the host policy; the directory remains in Temp and contains no repository changes.
- No external MAS checkout files are part of the repository diff.

## Residual risk

- Full interactive MAS startup and the user-facing MTTS journey were not automated.
- The repository test suite does not execute Ren'Py runtime behavior; lint/compile only establish script parse/compile validity.
- Translation quality beyond key coverage remains a human-language review item.
