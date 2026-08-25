import os
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
MAIN = ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "main.rpy"

if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

from mtts_cp936_decode import decode_cp936


def _main_source():
    return MAIN.read_text(encoding="utf-8")


def _load_decode_str():
    source = _main_source()
    start = source.index("        def decode_str(text):")
    end = source.index("\n        @staticmethod", start)
    function_source = textwrap.dedent(source[start:end])

    warnings = []
    logger = SimpleNamespace(warning=lambda message: warnings.append(message))
    namespace = {
        "store": SimpleNamespace(
            mas_submod_utils=SimpleNamespace(submod_log=logger),
        ),
    }
    exec(function_source, namespace)
    return namespace["decode_str"], warnings


def _compare_versions(current, comparative):
    current = list(current)
    comparative = list(comparative)
    width = max(len(current), len(comparative))
    current.extend([0] * (width - len(current)))
    comparative.extend([0] * (width - len(comparative)))
    return (current > comparative) - (current < comparative)


def _load_version_helpers(tmp_path, current_version="1.2.15"):
    source = _main_source()
    start = source.index("    _cached_version_result = None")
    end = source.index("    def progress_bar", start)
    version_source = textwrap.dedent(source[start:end])

    namespace = {
        "os": os,
        "renpy": SimpleNamespace(config=SimpleNamespace(basedir=str(tmp_path))),
        "store": SimpleNamespace(
            mtts_version=current_version,
            mas_utils=SimpleNamespace(compareVersionLists=_compare_versions),
        ),
    }
    exec(version_source, namespace)
    return namespace


def test_cp936_decoder_handles_python3_bytes_and_bytearray():
    encoded = "中文".encode("gbk")

    assert decode_cp936(encoded) == "中文"
    assert decode_cp936(bytearray(encoded)) == "中文"
    assert decode_cp936("already unicode") == "already unicode"


def test_cp936_decoder_preserves_single_byte_extension_and_invalid_tail():
    assert decode_cp936(b"\x80") == "\u20ac"
    assert decode_cp936("隆".encode("gbk")) == "隆"
    assert decode_cp936(b"\x81\x40") == "\u4e02"
    assert decode_cp936(b"\x81") == "\ufffd"
    assert decode_cp936(b"\x81\x30") == "\ufffd0"


def test_cp936_decoder_rejects_non_text_input():
    with pytest.raises(TypeError):
        decode_cp936(123)


def test_main_decode_str_prefers_cp936_for_legacy_bytes_and_utf8_when_needed():
    decode_str, warnings = _load_decode_str()

    assert decode_str("中文".encode("utf-8")) == "中文"
    assert decode_str("你好".encode("utf-8")) == "你好"
    assert warnings == []

    assert decode_str("中文".encode("gbk")) == "中文"
    assert warnings == []
    assert decode_str("隆".encode("gbk")) == "隆"
    assert decode_str(b"\x81") == "\ufffd"
    assert warnings == [
        "Text is not valid UTF-8 or CP936; replacement characters used."
    ]
    assert decode_str("already unicode") == "already unicode"
    assert decode_str(123) == "123"


def test_main_decode_str_does_not_depend_on_chardet_guessing():
    source = _main_source()
    start = source.index("        def decode_str(text):")
    end = source.index("\n        @staticmethod", start)
    decode_source = source[start:end]

    assert "chardet" not in decode_source
    assert "encoding.lower()" not in decode_source


def test_version_parts_are_numeric_and_outdated_check_uses_them(tmp_path):
    namespace = _load_version_helpers(tmp_path, current_version="1.2.10")

    assert namespace["mtts_version_parts"](" 1.2.10\n") == [1, 2, 10]
    assert namespace["is_mtts_frontend_outdated"]({
        "success": True,
        "content": {"fe_synbrace_version": "1.2.9"},
    }) is False
    assert namespace["is_mtts_frontend_outdated"]({
        "success": True,
        "content": {"fe_synbrace_version": "1.2.11"},
    }) is True
    assert namespace["is_mtts_frontend_outdated"]({
        "success": True,
        "content": {"fe_synbrace_version": "1.2.10.0"},
    }) is False
    assert namespace["is_mtts_frontend_outdated"]({
        "success": False,
        "content": {"fe_synbrace_version": "99.0.0"},
    }) is False
    assert namespace["is_mtts_frontend_outdated"]({
        "success": True,
        "content": {},
    }) is False
    assert namespace["is_mtts_frontend_outdated"]({
        "success": True,
        "content": None,
    }) is False
    assert namespace["is_mtts_frontend_outdated"]({
        "success": True,
        "content": [],
    }) is False
    assert namespace["mtts_version_parts"]("1.2.x") is None
    assert namespace["mtts_version_parts"]("foo") is None
    assert namespace["mtts_version_parts"]([]) is None
    assert namespace["mtts_version_parts"](None) is None

    namespace["store"].mtts = SimpleNamespace(
        mtts_instance=SimpleNamespace(
            version_info={
                "success": True,
                "content": {"fe_synbrace_version": "1.2.11"},
            },
        ),
    )
    assert namespace["is_mtts_frontend_outdated"]() is True


def test_outdated_policy_uses_transient_version_cache_only():
    main = _main_source()
    header = (
        ROOT / "game" / "Submods" / "MAICA_MttsSubmod" / "header.rpy"
    ).read_text(encoding="utf-8")
    check_start = main.index("    def mtts_check_outdated():")
    check_end = main.index("    _cached_version_result = None", check_start)
    check_source = main[check_start:check_end]

    assert main.count('"_outdated"') == 1
    assert 'setting.pop("_outdated", None)' in main
    assert 'persistent.mtts["_outdated"]' not in header
    assert 'persistent.mtts.get("_outdated"' not in header
    assert '@store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)' in main
    assert "mtts_instance.get_version(" not in check_source
    assert "store.persistent" not in check_source
    assert 'getattr(mtts_instance, "version_info", {})' in check_source


@pytest.mark.parametrize(
    ("library_version", "ui_version", "expected"),
    [
        ("1.2.10", "1.2.9", 1),
        ("1.2", "1.2.0", 0),
        ("1.2.9", "1.2.10", -1),
    ],
)
def test_release_version_check_handles_numeric_segments_and_rollbacks(
    tmp_path,
    library_version,
    ui_version,
    expected,
):
    version_dir = tmp_path / "game" / "python-packages"
    version_dir.mkdir(parents=True)
    (version_dir / "mtts_release_version").write_text(
        library_version,
        encoding="utf-8",
    )
    namespace = _load_version_helpers(tmp_path, current_version=ui_version)

    result = namespace["validate_version"]()

    assert result[0] == expected
    assert result[1] == library_version
    assert result[2] == ui_version
