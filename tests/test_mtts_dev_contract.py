import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "header.rpy"
MIGRATION = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "migration.rpy"
TRANSLATION = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "tl" / "header.rpy"
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def test_mtts_migrates_the_maica_development_build_contract():
    header = HEADER.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")
    translation = TRANSLATION.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert len(re.findall(r"(?m)^\s*maica_is_dev\s*=\s*(?:True|False)\s*$", header)) == 1
    assert re.search(r"(?m)^\s*maica_is_dev\s*=\s*True\s*$", header)
    assert "if store.maica_is_dev:" in header
    assert "development build" in header
    assert "force_current=store.maica_is_dev" in migration
    assert "development build" in translation
    assert "开发版本" in translation

    assert "maica_is_dev must be assigned exactly once to True or False" in workflow
    assert "steps.get_version.outputs.is_development == 'false'" in workflow
    assert "steps.get_version.outputs.is_development == 'true'" in workflow
    assert "if: always()" not in workflow
