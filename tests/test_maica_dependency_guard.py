from pathlib import Path
import sys
import struct
import textwrap
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
sys.path.append(str(PYTHON_PACKAGES))

import mtts_package

HEADER = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "header.rpym"
MAIN = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "main.rpym"
HEADER_JSON = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "header.json"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def test_mtts_registers_unbounded_ignore_translation_conflicts_dependency():
    import json
    data = json.loads(HEADER_JSON.read_text(encoding="utf-8"))
    assert isinstance(data["dependencies"], dict)


def test_release_workflow_downloads_dependency_into_game_tree():
    text = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    download_block = text[
        text.index("Download Ignore Translation Conflicts dependency") :
        text.index("Create release version file")
    ]

    assert "https://github.com/MAS-Submod-MoyuTeam/MAS_ignore_tl_conficts_submod/archive/refs/tags/v1.0.0.zip" in download_block
    assert "unzip -q" in download_block
    assert 'cp -R "$source_dir/game/." game/' in download_block
    assert "zz_ignore_translation_conflicts.rpy" in download_block


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


def test_settings_pane_uses_cached_file_diagnostics():
    header_text = HEADER.read_text(encoding="utf-8")
    main_text = MAIN.read_text(encoding="utf-8")

    assert 'on "show" action Function(store.mtts.refresh_setting_pane_cache)' in header_text
    assert "store.mtts.validate_version()" not in header_text
    assert 'version_check = pane_cache.get("version_check", None)' in header_text
    assert 'pane_cache.get("donation_exists", False)' in header_text
    assert "refresh_setting_pane_cache(force_version=True)" in main_text


def test_version_and_setting_pane_caches_support_explicit_refresh(tmp_path):
    source = MAIN.read_text(encoding="utf-8")
    cache_block = source[
        source.index("    _cached_version_result = None") :
        source.index("    def progress_bar")
    ]

    python_packages = tmp_path / "game" / "python-packages"
    python_packages.mkdir(parents=True)
    version_file = python_packages / "mtts_release_version"
    version_file.write_text("1.2.13", encoding="utf-8")

    def compare_versions(left, right):
        left = [int(part) for part in left]
        right = [int(part) for part in right]
        return (left > right) - (left < right)

    namespace = {
        "os": __import__("os"),
        "renpy": SimpleNamespace(config=SimpleNamespace(basedir=str(tmp_path))),
        "store": SimpleNamespace(
            mtts_version="1.2.13",
            mas_utils=SimpleNamespace(compareVersionLists=compare_versions),
        ),
    }
    exec(textwrap.dedent(cache_block), namespace)

    first_result = namespace["validate_version"]()
    version_file.write_text("1.2.14", encoding="utf-8")

    assert first_result[0] == 0
    assert namespace["validate_version"]() is first_result
    assert namespace["validate_version"](force=True)[0] == 1

    pane_cache = namespace["refresh_setting_pane_cache"]()
    assert pane_cache["initialized"] is True
    assert pane_cache["version_check"][0] == 1
    assert pane_cache["donation_exists"] is False


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


def test_extend_tracker_can_clear_pending_text_at_a_session_boundary():
    tracker = mtts_package.ExtendTextTracker()

    tracker.begin_extend("Stale line")
    tracker.clear()

    assert tracker.resolve("Current line", "Previous line") == (
        False,
        "Current line",
    )


def test_extend_tracker_falls_back_to_combined_text_tail():
    tracker = mtts_package.ExtendTextTracker()

    assert tracker.resolve("First line{fast}Second line", "First line") == (
        True,
        "Second line",
    )
    assert tracker.resolve("First line{fast}", "First line{nw}") == (
        True,
        "",
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


def test_main_clears_tts_session_when_unavailable_and_invalidates_old_generations():
    text = MAIN.read_text(encoding="utf-8")

    assert "def reset_session(self, stop_audio=False):" in text
    assert "self._extend_tracker.clear()" in text
    assert "del self._history[:]" in text
    assert "self._session_id += 1" in text
    assert "self.reset_session(" in text[text.index("def __call__") :]
    assert "generation_session_id = self._session_id" in text
    assert "generation_is_current = self.is_generation_current(generation_session_id)" in text
    assert "Ignoring generation result from an expired session" in text


def test_main_routes_enabled_toggles_through_session_boundary_handler():
    main_text = MAIN.read_text(encoding="utf-8")
    setting_text = (ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "screen_main_setting.rpym").read_text(encoding="utf-8")
    status_text = (ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "status.rpym").read_text(encoding="utf-8")

    assert "def mtts_set_enabled(enabled, previous_enabled=None):" in main_text
    assert "def mtts_toggle_enabled():" in main_text
    assert "Function(mtts_toggle_enabled)" in setting_text
    assert "Function(mtts_toggle_enabled)" in status_text
    assert setting_text.count('selected persistent.mtts.get("enabled", False)') == 2
    assert 'ToggleDict(persistent.mtts, "enabled", True, False)' not in setting_text
    assert 'ToggleDict(persistent.mtts, "enabled", True, False)' not in status_text
    assert 'renpy.music.stop(channel="voice", fadeout=0)' in main_text


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


def test_programmatic_generation_wakeup_preserves_auto_forward_during_wait():
    text = MAIN.read_text(encoding="utf-8")

    assert "def begin_generation_wait_afm_scope(self):" in text
    assert "def end_generation_wait_afm_scope(self, should_restore):" in text
    assert "prefs.afm_after_click = True" in text
    assert "prefs.afm_after_click = False" in text
    assert "prefs.afm_enable = True" in text

    wait_start = text.index("restore_afm_scope = self.begin_generation_wait_afm_scope()")
    wait_call = text.index("self.call_old_say(who, self.build_generation_wait_text(is_extend, remaining_wait)")
    wait_end = text.index("self.end_generation_wait_afm_scope(restore_afm_scope)")
    assert wait_start < wait_call < wait_end
    assert "finally:" in text[wait_call:wait_end]


def test_auto_forward_extend_lead_line_waits_for_voice_before_no_wait():
    text = MAIN.read_text(encoding="utf-8")

    assert "def should_wait_for_voice_before_extend(self, what, is_extend, interact):" in text
    assert "def strip_no_wait_tags(what):" in text
    assert "display_what = self.strip_no_wait_tags(what) if self.should_wait_for_voice_before_extend(what, is_extend, interact) else what" in text
    assert "self.call_old_say(who, display_what, interact, args, kwargs)" in text

    final_say_block = text[text.index("self._history.append(text)") :]
    assert "self.call_old_say(who, what, interact, args, kwargs)" not in final_say_block


def test_generation_wait_uses_remaining_timeout_not_spinner_period():
    text = MAIN.read_text(encoding="utf-8")

    assert "def build_generation_wait_text(self, is_extend, wait_seconds):" in text
    assert 'u" {image=mtts_spinner}{fast}{w=%s}{nw}" % wait_seconds' in text
    assert "remaining_wait = max(0.1, generate_timeout - elapsed)" in text


def test_generation_wait_exits_immediately_when_session_is_invalidated():
    text = MAIN.read_text(encoding="utf-8")
    wait_anchor = text.index("task.add_done_callback(wake_generation_wait)")
    wait_start = text.index("            while True:", wait_anchor)
    cancel_guard = text.index(
        "if not self.is_generation_current(generation_session_id):",
        wait_start,
    )
    task_check = text.index("if task.is_finished:", wait_start)
    timeout_check = text.index("if elapsed >= generate_timeout:", wait_start)

    assert wait_start < cancel_guard < task_check < timeout_check
    assert "self._active_generation_wait_id = None" in text[cancel_guard:task_check]
    assert "break" in text[cancel_guard:task_check]


def test_reset_session_wakes_an_active_generation_wait():
    text = MAIN.read_text(encoding="utf-8")
    reset_start = text.index("def reset_session(self, stop_audio=False):")
    reset_end = text.index("        @staticmethod\n        def stop_voice", reset_start)
    reset_block = text[reset_start:reset_end]

    assert "had_active_generation_wait = self._active_generation_wait_id is not None" in reset_block
    assert "if had_active_generation_wait:" in reset_block
    assert "renpy.restart_interaction()" in reset_block
