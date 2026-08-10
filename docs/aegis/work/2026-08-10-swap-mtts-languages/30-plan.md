# MTTS Language Swap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make MTTS use English source/UI text with Chinese translations under its local `tl` directory.

**Architecture:** The source files remain the canonical English language. The local translation files become Ren'Py `chinese` translation blocks. Existing English translations provide the source wording where available; shared template wording follows the MAS Chat template, and the Ren'Py generator refreshes dialogue identifiers in an isolated merged project.

**Tech Stack:** Ren'Py 8.2.3 translation generation, PowerShell, Python 3 pytest, `.rpy` source files.

**Baseline / Authority Refs:** `README.md`, `README_EN.md`, `game/Submods/MAICA_MttsSubmod`, `game/Submods/MAICA_MttsSubmod/tl`, `game/python-packages/mtts_provider_manager.py`, `tests/test_maica_dependency_guard.py`, and `J:\MonikaModDev-zhCN\utils\generate-translations.ps1`.

**Compatibility Boundary:** Keep `config.language` defaulting to `english`, preserve `zh`/`en` TTS routing, preserve Chinese-language donation URL selection, preserve persistent setting keys and event labels, and leave internal diagnostics/test fixtures unchanged.

**Verification:** Run the new localization contract test, `pytest -q tests`, the translation generator in a disposable MAS staging project, Ren'Py parse/lint checks where supported, and targeted static checks for source/translation language ownership.

---

### Task 1: Localization contract test

**Files:**
- Create: `tests/test_mtts_language_swap.py`

**Why this task exists:** The language swap is distributed across source and generated translation files. A static contract test prevents a later source update from silently restoring English translations or leaving Chinese source UI strings.

**Impact / Compatibility:** The test inspects source and local translation ownership only. It must not import Ren'Py or change runtime behavior.

**Verification:** `pytest -q tests/test_mtts_language_swap.py` must fail before implementation because the current source is Chinese and local translations are `translate english`.

- [ ] Write assertions for no Chinese in the selected user-visible source strings, no `translate english` in `tl`, presence of `translate chinese`, provider description keys, and preserved language routing.
- [ ] Run the test and record the expected failure.

### Task 2: English source/UI conversion

**Files:**
- Modify: `game/Submods/MAICA_MttsSubmod/acs.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/chat.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/header.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/main.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/screen_advanced_setting.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/screen_subs.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/screen_templates.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/status.rpy`
- Modify: `game/python-packages/mtts_provider_manager.py`

**Why this task exists:** English must be the base text so the default UI does not depend on an English translation overlay.

**Impact / Compatibility:** Only user-visible source strings and built-in provider display data change. Internal comments, logs, test fixtures, labels, settings, URLs, and control flow stay stable. Provider defaults use `description`, matching `screen_subs.rpy` and remote provider payloads.

- [ ] Replace source UI/dialogue strings using the existing English translations and canonical shared template wording.
- [ ] Change built-in provider display values and the non-200 error update to the consumed `description` key.
- [ ] Run the contract test and targeted source scans.

### Task 3: Chinese translation regeneration and normalization

**Files:**
- Modify: `game/Submods/MAICA_MttsSubmod/tl/*.rpy`
- Create/modify: `game/Submods/MAICA_MttsSubmod/tl/screen_templates.rpy`
- Modify: `game/Submods/MAICA_MttsSubmod/tl/mtts_description.rpy`

**Why this task exists:** Ren'Py dialogue translation labels are tied to source text. Swapping source text without regenerating labels can make dialogue fall back to English or the wrong language.

**Impact / Compatibility:** The local `tl` path remains the package-owned translation location. No external MAS translation files are copied into the repository; generated staging output is filtered to this submod. Existing Chinese translations are retained, and missing strings receive Chinese translations.

- [ ] Generate `chinese` resources in a disposable merged MAS project with `generate-translations.ps1`.
- [ ] Reconcile generated dialogue IDs and string entries with the existing Chinese source text and the approved English source wording.
- [ ] Convert the provider Python translation block to `translate chinese python`.
- [ ] Remove stale `translate english` ownership from the local translation files.
- [ ] Run the contract test and translation completeness checks.

### Task 4: Regression and runtime-oriented verification

**Files:**
- Modify: `tests/test_mtts_language_swap.py` only if a discovered invariant needs a clearer regression assertion.

**Why this task exists:** This is a user-visible language and translation namespace migration, so static tests alone do not prove Ren'Py can parse the result.

**Impact / Compatibility:** No runtime logic changes beyond provider display-key repair. Verification must distinguish existing Python 2 package-test collection failures from new failures.

- [ ] Run `pytest -q tests`.
- [ ] Run the provided translation script in an isolated staging project and verify generated `chinese` output.
- [ ] Run Ren'Py lint/compile checks against the staged project if the SDK supports the command without launching the game.
- [ ] Inspect `git diff --check`, changed-file scope, and final source/translation language scans.

### Task 5: Review and integration

**Files:**
- Review all changed files and generated translation output.

**Why this task exists:** Generated localization output is easy to make syntactically valid but semantically incomplete.

**Impact / Compatibility:** Confirm no old English translation path, stale dialogue ID, unexpected source-language branch, or external-project side effect remains.

- [ ] Request advisory code review with the final diff and evidence bundle.
- [ ] Resolve Important/Critical findings.
- [ ] Merge the verified branch back into the user's current `main` worktree.
