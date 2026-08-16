import logging
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"

import sys

if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

import logger_manager
import migrations
import mtts_package
import mtts_provider_manager


CHAT = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "chat.rpy"
MIGRATION = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "migration.rpy"
UNLOCK_PROGRESS = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "unlock_progress.rpy"


def test_event_registration_matches_the_runtime_contract():
    text = CHAT.read_text(encoding="utf-8")

    prepend = text[:text.index("label mtts_prepend_1:")]
    assert "unlocked=False" in prepend
    assert "random=False" in prepend
    assert "pool=False" in prepend
    assert "action=EV_ACT_QUEUE" in prepend
    assert "not renpy.seen_label('mtts_greeting_end')" in prepend

    hint = text[text.index("    mtts_hint_conditional ="):text.index("label mtts_hint:")]
    assert "unlocked=False" in hint
    assert "random=False" in hint
    assert "pool=False" in hint
    assert "action=EV_ACT_QUEUE" in hint
    assert "not mtts_headset_gift_available()" in hint
    assert "def mtts_headset_gift_available()" in text
    assert '"mttsheadset"' in text
    assert 'return "no_unlock|derandom|rebuild_ev"' in text

    greeting = text[text.index("    mtts_greeting_conditional ="):text.index("label mas_reaction_gift_mttsheadset:")]
    assert "unlocked=True" in greeting
    assert "MASGreetingRule.create_rule(skip_visual=False)" in greeting
    assert "MASPriorityRule.create_rule(11)" in greeting
    assert "mas_isplayer_bday()" in greeting
    assert "not renpy.seen_label('mtts_greeting_end')" in greeting
    assert "mas_rmallEVL(\"mtts_hint\")" in text

    assert "ch30_post_exp_check" not in text
    assert "selected_greeting" not in text


def test_migration_repairs_legacy_events_and_only_advances_after_success():
    text = MIGRATION.read_text(encoding="utf-8")

    assert text.startswith("init 980 python:\n    import os")
    assert "def m_1_2_16()" in text
    migration_1_2_16 = text[text.index("        def m_1_2_16():"):]
    assert 'persistent._seen_ever["mtts_greeting_end"] = True' not in migration_1_2_16
    assert "mas_rebuildEventLists()" in text
    assert "queued_events" in text
    assert "_mas_player_derandomed" in text
    assert "migration_result = migration.migrate()" in text
    assert "migration_succeeded" in text
    assert "migration_result is None" in text
    assert "persistent._mtts_last_version = store.mtts_version" in text


def test_progress_diagnostics_use_the_same_end_markers_and_greeting_guards():
    text = UNLOCK_PROGRESS.read_text(encoding="utf-8")

    assert "cond1_seen_end" in text
    assert "cond2_seen_gift" in text
    assert "cond2_seen_end" in text
    assert "persistent._mas_greeting_type is None" in text
    assert "cond3_player_bday = mas_isplayer_bday()" in text
    assert "cond3_affectionate = mas_isMoniAff(higher=True)" in text


def test_migration_supports_missing_segments_and_reports_completion():
    calls = []
    migration = migrations.migration_instance("1.2", "1.2.1")
    migration.migration_queue = [("1.2.1", lambda: calls.append("upgrade"))]

    assert migration.migrate() == (True, "Migration complete")
    assert calls == ["upgrade"]


def test_migration_unchanged_path_keeps_the_legacy_result_contract():
    migration = migrations.migration_instance("1.2", "1.2.0")
    migration.migration_queue = [("1.2.0", lambda: None)]

    assert migration.migrate() == (True, "Version unchanged")


def test_migration_rejects_rollbacks_and_invalid_versions():
    rollback = migrations.migration_instance("1.2.2", "1.2.1")
    assert rollback.migrate() == (False, "Trying to revert version, denying")

    invalid = migrations.migration_instance("1.2.x", "1.2.1")
    assert invalid.migrate() == (False, "Version schemas incompatable")


def test_migration_force_current_runs_only_the_current_entry():
    calls = []
    migration = migrations.migration_instance("1.9.0", "1.8.0", force_current=True)
    migration.migration_queue = [
        ("1.8.0", lambda: calls.append("current")),
        ("1.9.0", lambda: calls.append("newer")),
    ]

    assert migration.migrate() == (True, "Migration complete")
    assert calls == ["current"]


def test_migration_failure_is_returned_without_claiming_success():
    def fail():
        raise RuntimeError("broken migration")

    migration = migrations.migration_instance("1.2.0", "1.2.1")
    migration.migration_queue = [("1.2.1", fail)]

    result = migration.migrate()

    assert result[0] is False
    assert "Migration failed" in result[1]


def test_mtts_migration_accepts_chat_shared_none_success_result():
    text = MIGRATION.read_text(encoding="utf-8")
    assert "Chat's shared migrations.py historically returned None" in text
    assert "migration_result is None" in text


class CaptureLogger(object):
    def __init__(self):
        self.calls = []

    def _capture(self, method, *args, **kwargs):
        self.calls.append((method, args, kwargs))

    debug = lambda self, *args, **kwargs: self._capture("debug", *args, **kwargs)
    info = lambda self, *args, **kwargs: self._capture("info", *args, **kwargs)
    warning = lambda self, *args, **kwargs: self._capture("warning", *args, **kwargs)
    error = lambda self, *args, **kwargs: self._capture("error", *args, **kwargs)
    critical = lambda self, *args, **kwargs: self._capture("critical", *args, **kwargs)
    exception = lambda self, *args, **kwargs: self._capture("exception", *args, **kwargs)
    log = lambda self, *args, **kwargs: self._capture("log", *args, **kwargs)


def test_loggers_follow_mas_logger_and_redact_tokens_on_all_paths():
    manager = logger_manager.get_logger_manager()
    previous = manager.logger
    capture = CaptureLogger()
    try:
        manager.set_logger(capture)
        mtts_package.logger.error("access_token=abcdefghijk")
        mtts_package.logger.error("access_token=%s", "format-secret")
        mtts_package.logger.log(logging.INFO, '{"access_token": "zyxwvuts"}')
        mtts_package.logger.log(logging.INFO, {"access_token": "structured-secret"})
        mtts_provider_manager.logger.warning("access_token=provider-secret")
        mtts_provider_manager.logger.warning("access_token=%s", "provider-format-secret")
        mtts_provider_manager.logger.log(logging.INFO, "access_token=provider-log-secret")
    finally:
        manager.set_logger(previous)

    messages = [
        " ".join(str(item) for item in call[1])
        for call in capture.calls
    ]
    assert any("abcd***" in message for message in messages)
    assert any("form***" in message for message in messages)
    assert any("zyxw***" in message for message in messages)
    assert any("stru***" in message for message in messages)
    assert any("prov***" in message for message in messages)
    assert any("prov***" in message for message in messages)
    assert all("abcdefghijk" not in message for message in messages)
    assert all("format-secret" not in message for message in messages)
    assert all("provider-secret" not in message for message in messages)
    assert all("provider-format-secret" not in message for message in messages)
    assert all("provider-log-secret" not in message for message in messages)
    assert all("structured-secret" not in message for message in messages)


def test_logger_manager_does_not_touch_process_root_handlers():
    root = logging.getLogger()
    before = list(root.handlers)
    manager = logger_manager.get_logger_manager()
    assert manager.logger is not root
    assert manager.logger.propagate is False
    assert list(root.handlers) == before


def test_logger_manager_reload_reuses_its_fallback_handler():
    script = """
import importlib
import logging
import sys

sys.path.insert(0, {package_path!r})
root = logging.getLogger()
root_handlers = list(root.handlers)
import logger_manager

for _index in range(3):
    logger_manager = importlib.reload(logger_manager)
    logger_manager.get_logger_manager()

fallback = logging.getLogger("maica_logger_manager")
marked = [
    handler
    for handler in fallback.handlers
    if getattr(handler, "_maica_logger_manager_handler", False)
]
assert len(marked) == 1
assert fallback.propagate is False
assert list(root.handlers) == root_handlers
""".format(package_path=str(PYTHON_PACKAGES))

    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )


def test_existing_package_wrappers_follow_a_reloaded_manager():
    script = """
import importlib
import sys

sys.path.insert(0, {package_path!r})
import logger_manager
import mtts_package
import mtts_provider_manager

class Capture(object):
    def __init__(self):
        self.messages = []
    def info(self, message, *args, **kwargs):
        self.messages.append(message)
    debug = warning = error = critical = exception = info
    def log(self, level, message, *args, **kwargs):
        self.messages.append(message)

logger_manager = importlib.reload(logger_manager)
capture = Capture()
manager = logger_manager.get_logger_manager()
manager.set_logger(capture)
mtts_package.logger.info("package-after-reload")
mtts_provider_manager.logger.info("provider-after-reload")
assert "package-after-reload" in capture.messages
assert "provider-after-reload" in capture.messages
""".format(package_path=str(PYTHON_PACKAGES))

    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
