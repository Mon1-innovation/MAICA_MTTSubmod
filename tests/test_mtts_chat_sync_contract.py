import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

import mtts_package
import mtts_renpy_text


def read_source(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_renpy_external_text_escape_covers_brackets_braces_and_trusted_names():
    assert mtts_renpy_text.escape_renpy_text(None) == ""
    assert mtts_renpy_text.escape_renpy_text("[field] {value}") == "[[field] {{value}"

    escaped = mtts_renpy_text.escape_renpy_text(
        "[player] [m_name] [unknown] {w=0.3}",
        mtts_renpy_text.RENPY_DIALOGUE_SUBSTITUTIONS,
    )
    assert "[player]" in escaped
    assert "[m_name]" in escaped
    assert "[[unknown]" in escaped
    assert "{{w=0.3}" in escaped


def test_renpy_preview_drops_partial_markers_before_escaping():
    assert mtts_renpy_text.build_renpy_text_preview(
        "prefix [player] suffix",
        12,
        mtts_renpy_text.RENPY_DIALOGUE_SUBSTITUTIONS,
    ) == "prefix ..."
    assert mtts_renpy_text.escape_exception_text("[x] {w=1}") == "[[x] {{w=1}"


def test_mtts_dynamic_ui_uses_explicit_scope_and_display_escape():
    header = read_source("game/Submods/MAICA_MttsSubmod/header.rpy")
    main = read_source("game/Submods/MAICA_MttsSubmod/main.rpy")
    setting = read_source("game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy")
    screens = read_source("game/Submods/MAICA_MttsSubmod/screen_subs.rpy")
    templates = read_source("game/Submods/MAICA_MttsSubmod/screen_templates.rpy")

    assert "mtts_renpy_text.escape_exception_text" in main
    assert "detail = detail.replace" not in header
    assert 'scope={"provider_name": provider_name}' in setting
    assert 'scope={"user_disp": user_disp}' in setting
    assert "mtts_escape_display_text(" in screens
    assert "mtts_escape_display_text(provider_url" not in screens
    assert "action OpenURL(provider_url)" in screens
    assert "label mtts_escape_display_text(_(message))" in templates

    status = read_source("game/Submods/MAICA_MttsSubmod/status.rpy")
    advanced = read_source("game/Submods/MAICA_MttsSubmod/screen_advanced_setting.rpy")
    assert 'scope={"status_text": store.mtts_status}' in status
    assert '"CURR: {}".format(store.mtts._current_label)' in status
    assert 'scope={"replacement": replacement}' in setting
    assert 'scope={"split_method": split_method}' in advanced
    assert '"VRAM: {} / {}".format(' in header

    status_translation = read_source("game/Submods/MAICA_MttsSubmod/tl/status.rpy")
    setting_translation = read_source("game/Submods/MAICA_MttsSubmod/tl/screen_main_setting.rpy")
    advanced_translation = read_source("game/Submods/MAICA_MttsSubmod/tl/screen_advanced_setting.rpy")
    assert 'old "MTTS status: [status_text]"' in status_translation
    assert 'new "MTTS状态: [status_text]"' in status_translation
    assert 'new "替换为: [replacement]"' in setting_translation
    assert 'new "切换: 当前为 [split_method]"' in advanced_translation
    assert 'old "Current provider: [provider_name]"' in setting_translation
    assert 'new "服务提供节点: [provider_name]"' in setting_translation


def test_mtts_persistent_repairs_use_builtin_container_guards():
    main = read_source("game/Submods/MAICA_MttsSubmod/main.rpy")
    migration = read_source("game/Submods/MAICA_MttsSubmod/migration.rpy")
    named_store = main.split("init -100 python in mtts:", 1)[1].split(
        "\ninit 10 python in mtts:", 1
    )[0]
    provider_sync = named_store.split("    def sync_provider_id", 1)[1].split(
        "\n    @store.mas_submod_utils.functionplugin", 1
    )[0]

    assert "if not mtts_is_builtin_dict(getattr(persistent, \"mtts\", None)):" in main
    assert "persistent.mtts_advance_params = {}" in main
    assert "store.mtts_is_builtin_dict(store.persistent.maica_setting_dict)" in provider_sync
    assert not re.search(r"(?<![\w.])persistent\b", named_store)
    assert "mtts_is_builtin_sequence(item)" in migration
    assert "mtts_is_builtin_sequence(migration_result)" in migration


def test_error_wording_and_logger_manager_noise_follow_chat_sync():
    package = read_source("game/python-packages/mtts_package.py")
    translation = read_source("game/Submods/MAICA_MttsSubmod/tl/main.rpy")
    logger = read_source("game/python-packages/logger_manager.py")

    assert mtts_package.MTTS.MttsStatus.get_description(
        mtts_package.MTTS.MttsStatus.SERVER_REJECTED
    ) == "A user-level error occurred"
    assert mtts_package.MTTS.MttsStatus.get_description(
        mtts_package.MTTS.MttsStatus.SERVER_ERROR
    ) == "A server-side error occurred"
    assert 'old "A user-level error occurred"' in translation
    assert 'old "A server-side error occurred"' in translation
    assert "LoggerManager initialized" not in logger
    assert "Logger replaced with custom logger instance" not in logger
    assert "Handler added:" not in logger
    assert "Handler removed:" not in logger
    assert "Formatter updated:" not in logger
