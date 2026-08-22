import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "game" / "Submods" / "MAICA_MttsSubmod"
TRANSLATION_ROOT = SOURCE_ROOT / "tl"
SOURCE_FILES = (
    "acs.rpy",
    "chat.rpy",
    "header.rpy",
    "main.rpy",
    "screen_advanced_setting.rpy",
    "screen_main_setting.rpy",
    "screen_subs.rpy",
    "screen_templates.rpy",
    "status.rpy",
)
CHINESE = re.compile(r"[\u4e00-\u9fff]")


def read_source(name):
    return (SOURCE_ROOT / name).read_text(encoding="utf-8")


def test_mtts_source_ui_strings_are_english():
    source_text = "\n".join(read_source(name) for name in SOURCE_FILES)
    translatable_lines = [
        line.split("#", 1)[0]
        for line in source_text.splitlines()
        if not line.lstrip().startswith("#")
        if "_(" in line or re.match(r"\s*(?:m|extend)\s", line)
    ]

    assert translatable_lines
    assert not any(CHINESE.search(line) for line in translatable_lines)


def test_mtts_translation_files_use_chinese_namespace_and_english_source_keys():
    translation_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in TRANSLATION_ROOT.glob("*.rpy")
    )

    assert "translate chinese" in translation_text
    assert "translate english" not in translation_text

    old_lines = re.findall(r'^\s*old\s+"(.*)"$', translation_text, re.MULTILINE)
    new_lines = re.findall(r'^\s*new\s+"(.*)"$', translation_text, re.MULTILINE)
    assert old_lines
    assert len(new_lines) == len(old_lines)
    assert all(value.strip() for value in new_lines)
    assert not any(CHINESE.search(value) for value in old_lines)


def test_mtts_source_contains_english_defaults_and_preserves_language_routing():
    header = read_source("header.rpy")
    chat = read_source("chat.rpy")
    main = read_source("main.rpy")
    provider = (ROOT / "game" / "python-packages" / "mtts_provider_manager.py").read_text(
        encoding="utf-8"
    )

    assert 'description=_("MAICA-MTTS Official Submod Frontend")' in header
    assert 'eventlabel="mtts_greeting"' in chat
    assert 'prompt=_("MTTS knock")' in chat
    assert 'config.language = "english"' in main
    assert 'target_lang = "zh" if config.language == \'chinese\' else \'en\'' in main
    assert '"name": "ERROR: Unable to retrieve node information."' in provider
    assert '"description": "Check the update log to get the current service status' in provider
    assert '"name": "Local Deployment"' in provider
    assert '"description": "When you have an available local deployment' in provider


def test_mtts_source_covers_shared_template_strings_in_english():
    template = read_source("screen_templates.rpy")

    for value in (
        'minutes',
        'seconds',
        'Enter {} ({}-{}{}):',
        'Please input a valid value!',
        'Cancel',
    ):
        assert value in template
