from pathlib import Path
import sys
import struct


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


def test_extend_generation_indicator_keeps_previous_text_visible():
    text = MAIN.read_text(encoding="utf-8")

    assert "define MTTS_SPINNER_CYCLE_SECONDS = 1.2" in text
    assert "def build_generation_wait_text(self, is_extend, wait_seconds):" in text
    assert 'u" {image=mtts_spinner}{fast}{w=%s}{nw}" % wait_seconds' in text
    assert "return self._last_raw_text + spinner" in text
    assert 'return spinner' in text
    assert 'u" {color=#9a9a9a}"' not in text
    assert "mtts_spinner_0" not in text
    assert '"...{w=0.3}{nw}"' not in text


def test_generation_indicator_uses_scaled_frames_from_single_strip_image():
    text = MAIN.read_text(encoding="utf-8")

    assert "def mtts_build_spinner_animation():" in text
    assert "renpy.display.anim.Animation(*args)" in text
    assert "renpy.display.layout.Position(" in text
    assert '"mod_assets/mtts_img/mtts_spinner_strip.png"' in text
    assert "frame_width = 260" in text
    assert "frame_height = 320" in text
    assert "frame_count = 12" in text
    assert "define MTTS_SPINNER_DISPLAY_SIZE = 20" in text
    assert "MTTS_SPINNER_CYCLE_SECONDS / float(frame_count)" in text
    assert "im.Crop(source, index * frame_width, 0, frame_width, frame_height)" in text
    assert "im.Scale(frame, MTTS_SPINNER_DISPLAY_SIZE, MTTS_SPINNER_DISPLAY_SIZE)" in text
    assert "yanchor=0.5" in text
    assert "ypos=0.5" in text
    assert "maxsize=" not in text


def test_generation_indicator_strip_keeps_twelve_source_frames():
    spinner_path = ROOT / "game" / "mod_assets" / "mtts_img" / "mtts_spinner_strip.png"

    with spinner_path.open("rb") as handle:
        header = handle.read(24)

    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", header[16:24])
    assert (width, height) == (3120, 320)


def test_async_task_is_renamed_and_supports_done_callbacks():
    assert hasattr(mtts_package, "MTTSAsyncTask")
    assert not hasattr(mtts_package, "AsyncTask")

    callback_seen = []
    task = mtts_package.MTTSAsyncTask(lambda: "ok")
    task.add_done_callback(lambda finished_task: callback_seen.append(finished_task.result))
    task.wait(2)

    assert task.is_finished
    assert task.is_success
    assert callback_seen == ["ok"]


def test_async_task_runs_callback_registered_after_completion():
    callback_seen = []
    task = mtts_package.MTTSAsyncTask(lambda: "late")
    task.wait(2)

    task.add_done_callback(lambda finished_task: callback_seen.append(finished_task.result))

    assert callback_seen == ["late"]


def test_main_uses_event_wakeup_for_generation_wait_instead_of_fixed_polling():
    text = MAIN.read_text(encoding="utf-8")

    assert "MTTSAsyncTask = mtts_package.MTTSAsyncTask" in text
    assert "task = mtts.MTTSAsyncTask(" in text
    assert "def wake_generation_wait" in text
    assert 'renpy.queue_event("dismiss")' in text
    assert "while not task.is_finished:" not in text


def test_generation_wait_uses_remaining_timeout_not_spinner_period():
    text = MAIN.read_text(encoding="utf-8")

    assert "def build_generation_wait_text(self, is_extend, wait_seconds):" in text
    assert 'u" {image=mtts_spinner}{fast}{w=%s}{nw}" % wait_seconds' in text
    assert "remaining_wait = max(0.1, generate_timeout - elapsed)" in text
