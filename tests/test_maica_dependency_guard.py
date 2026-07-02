from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
sys.path.append(str(PYTHON_PACKAGES))

import mtts_package

HEADER = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "header.rpy"
MAIN = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "main.rpy"


def test_mtts_declares_maica_runtime_guard():
    text = HEADER.read_text(encoding="utf-8")

    assert "def mtts_has_maica_instance():" in text
    assert "hasattr(store.maica, \"maica_instance\")" in text


def test_settings_pane_checks_maica_runtime_before_accessing_instance():
    text = HEADER.read_text(encoding="utf-8")

    unsafe_condition = (
        'persistent.mtts["_chat_installed"] and '
        "store.maica.maica_instance.is_accessable()"
    )

    assert unsafe_condition not in text
    assert "if mtts_can_use_blessland_login():" in text


def test_user_sync_checks_maica_runtime_before_accessing_instance():
    text = HEADER.read_text(encoding="utf-8")

    sync_block = text[text.index("def mtts_try_sync_user_acc_from_blessland():") :]

    assert "if not mtts_has_maica_instance():" in sync_block
    assert "acc = getattr(store.maica.maica_instance, \"user_acc\", \"\")" in sync_block


def test_maica_chat_rule_has_language_fallback_without_instance():
    text = MAIN.read_text(encoding="utf-8")

    assert "if rule['name'] == 'MAICA_Chat' and mtts_has_maica_instance():" in text
    assert 'target_lang = "zh" if config.language == \'chinese\' else \'en\'' in text


def test_extend_tracker_consumes_pending_raw_text():
    tracker = mtts_package.ExtendTextTracker()

    tracker.begin_extend("Second line")

    assert tracker.resolve("First line{fast}Second line", "First line") == (
        True,
        "Second line",
    )
    assert tracker.pending_raw is None


def test_extend_tracker_falls_back_to_combined_text_tail():
    tracker = mtts_package.ExtendTextTracker()

    assert tracker.resolve("First line{fast}Second line", "First line") == (
        True,
        "Second line",
    )


def test_extend_tracker_treats_plain_text_as_non_extend():
    tracker = mtts_package.ExtendTextTracker()

    assert tracker.resolve("Plain line", "Previous line") == (
        False,
        "Plain line",
    )


def test_main_hijacks_exports_say_for_renpy6_ast_and_extend_paths():
    text = MAIN.read_text(encoding="utf-8")

    assert "old_renpysay = renpy.exports.say" in text
    assert "renpy.exports.say = mtts_say" in text
    assert "old_renpysay(who, what, interact," not in text
    assert "interact=interact, *args" not in text
    assert 'kw["interact"] = interact' in text


def test_main_wraps_extend_to_capture_raw_extend_text():
    text = MAIN.read_text(encoding="utf-8")

    assert "_mtts_original_extend = extend" in text
    assert "store.mtts_say.begin_extend(what)" in text
    assert "mtts_extend.record_say = False" in text
    assert "extend = mtts_extend" in text


def test_main_queues_extend_voice_segments_without_clearing_voice_queue():
    text = MAIN.read_text(encoding="utf-8")

    assert "renpy.music.queue(" in text
    assert "clear_queue=False" in text
