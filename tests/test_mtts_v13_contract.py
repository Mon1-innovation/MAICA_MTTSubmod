import os
import sys

import pytest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_PACKAGES = os.path.join(ROOT, "game", "python-packages")
if PYTHON_PACKAGES not in sys.path:
    sys.path.insert(0, PYTHON_PACKAGES)

import mtts_package
import mtts_provider_manager


class ResponseStub(object):
    def __init__(self, status_code=200, payload=None, content=b"", reason="OK"):
        self.status_code = status_code
        self.payload = payload
        self.content = content
        self.reason = reason
        self.text = ""

    def json(self):
        if self.payload is None:
            raise ValueError("not JSON")
        return self.payload


@pytest.fixture
def instance(tmp_path):
    result = mtts_package.MTTS(
        url="https://example.test/tts/",
        token="secret-token",
        cache_path=str(tmp_path),
    )
    result._MTTS__accessable = True
    return result


def test_verify_token_uses_bearer_auth_and_normalizes_protocol_status(monkeypatch, instance):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return ResponseStub(
            401,
            {"success": False, "exception": "maica_login_token_invalid: bad password"},
            reason="Unauthorized",
        )

    monkeypatch.setattr(mtts_package.requests, "get", fake_get)

    result = instance._verify_token()

    assert result == {
        "success": False,
        "status": "maica_login_token_invalid",
        "exception": "bad password",
        "code": 401,
    }
    assert instance.status == instance.MttsStatus.TOKEN_INVALID
    assert calls[0][1]["headers"] == {"Authorization": "Bearer secret-token"}
    assert "access_token" not in calls[0][1].get("params", {})


def test_token_generation_uses_post_json(monkeypatch, instance):
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return ResponseStub(200, {"success": True, "exception": None, "content": "new-token"})

    monkeypatch.setattr(mtts_package.requests, "post", fake_post)

    instance._gen_token("alice", "password")

    assert instance.token == "new-token"
    assert not instance.has_error()
    assert calls == [
        (
            "https://example.test/tts/register",
            {
                "json": {"content": {"username": "alice", "password": "password"}},
                "timeout": instance.HTTP_TIMEOUT,
            },
        )
    ]


def test_mtts_status_codes_align_with_chat_shared_statuses(instance):
    status = instance.MttsStatus

    assert status.SERVER_REJECTED == 13408
    assert status.SERVER_ERROR == 13409
    assert status.TOKEN_GENERATION_FAILED == 13410
    assert status.CONNECT_PROBLEM == 13411
    assert status.RESPONSE_INVALID == 13412
    assert status.SERVER_MAINTAIN == 13413
    assert status.FAILED_GET_NODE == 13415
    assert status.GENERATION_FAILED == 13418
    assert status.from_protocol_status("client_availability_failed") == status.CONNECT_PROBLEM


@pytest.mark.parametrize(
    "protocol_status,fallback,expected_status",
    [
        ("client_provider_unavailable", "FAILED_GET_NODE", "FAILED_GET_NODE"),
        ("client_network_error", None, "CONNECT_PROBLEM"),
        ("client_response_invalid", None, "RESPONSE_INVALID"),
        ("client_server_unavailable", None, "SERVER_MAINTAIN"),
    ],
)
def test_token_operations_preserve_availability_failures(
    instance,
    protocol_status,
    fallback,
    expected_status,
):
    instance._MTTS__accessable = False
    fallback_status = getattr(instance.MttsStatus, fallback) if fallback else None
    instance.set_error(protocol_status, "original availability failure", fallback=fallback_status)

    generation_result = instance._gen_token("alice", "password")

    assert generation_result is None
    assert instance.status == getattr(instance.MttsStatus, expected_status)
    assert instance.error_protocol_status == protocol_status
    assert instance.error_message == "original availability failure"

    verification_result = instance._verify_token()

    assert verification_result["status"] == protocol_status
    assert verification_result["exception"] == "original availability failure"
    assert instance.status == getattr(instance.MttsStatus, expected_status)


def test_unknown_token_generation_unavailability_is_connection_problem(tmp_path):
    instance = mtts_package.MTTS(
        url="https://example.test/tts/",
        token="",
        cache_path=str(tmp_path),
    )

    instance._gen_token("alice", "password")
    verification_result = instance._verify_token()

    assert instance.status == instance.MttsStatus.CONNECT_PROBLEM
    assert verification_result["status"] == "client_availability_failed"
    assert verification_result["exception"] == "MTTS server availability is unknown"


def test_generation_json_failure_sets_stable_failure_status(monkeypatch, instance):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return ResponseStub(
            403,
            {"success": False, "exception": "maica_input_query_censored: query rejected"},
            reason="Forbidden",
        )

    monkeypatch.setattr(mtts_package.requests, "get", fake_get)

    with pytest.raises(mtts_package.MTTSRequestError) as exc_info:
        instance.generate("hello", label_name="contract")

    assert exc_info.value.result["status"] == "maica_input_query_censored"
    assert exc_info.value.result["exception"] == "query rejected"
    assert instance.status == instance.MttsStatus.GENERATION_FAILED
    assert instance.get_status_description() == "Speech generation failed"
    assert calls[0][1]["headers"] == {"Authorization": "Bearer secret-token"}
    assert "access_token" not in calls[0][1]["params"]


def test_generation_audio_success_clears_previous_failure(monkeypatch, instance):
    instance.set_error("client_network_error", "offline")

    def fake_get(url, **kwargs):
        return ResponseStub(200, payload=None, content=b"audio-data")

    monkeypatch.setattr(mtts_package.requests, "get", fake_get)

    result = instance.generate("hello", label_name="contract")

    assert result.data == b"audio-data"
    assert not instance.has_error()


def test_version_failure_result_is_normalized(monkeypatch, instance):
    def fake_get(url, **kwargs):
        return ResponseStub(
            503,
            {"success": False, "exception": "maica_unified_error: maintenance"},
        )

    monkeypatch.setattr(mtts_package.requests, "get", fake_get)

    assert instance.get_version() == {
        "success": False,
        "status": "maica_unified_error",
        "exception": "maintenance",
        "code": 503,
    }


def test_version_invalid_response_and_network_failure_are_normalized(
    monkeypatch, instance
):
    monkeypatch.setattr(
        mtts_package.requests,
        "get",
        lambda *args, **kwargs: ResponseStub(502, None),
    )

    assert instance.get_version() == {
        "success": False,
        "status": "client_response_invalid",
        "exception": "Version response was not valid JSON",
        "code": 502,
    }

    monkeypatch.setattr(
        mtts_package.requests,
        "get",
        lambda *args, **kwargs: (_ for _ in ()).throw(IOError("offline")),
    )

    assert instance.get_version() == {
        "success": False,
        "status": "client_network_error",
        "exception": "Version request failed",
        "code": None,
    }


def test_provider_failure_preserves_protocol_status(monkeypatch):
    manager = mtts_provider_manager.MTTSProviderManager(1)

    def fake_get(url, **kwargs):
        return ResponseStub(
            503,
            {"success": False, "exception": "maica_unified_error: maintenance"},
        )

    monkeypatch.setattr("requests.get", fake_get)

    assert manager.get_provider() is False
    assert manager.last_error == {
        "success": False,
        "status": "maica_unified_error",
        "exception": "maintenance",
        "code": 503,
    }


def test_local_provider_uses_the_documented_mtts_root():
    manager = mtts_provider_manager.MTTSProviderManager(9999)

    assert manager.get_tts_url() == "http://127.0.0.1:7000/"


def test_accessibility_refreshes_provider_url_and_clears_failure(monkeypatch, instance):
    class ProviderStub(object):
        last_error = None

        def get_provider(self):
            return True

        def get_provider_id(self):
            return 2

        def get_tts_url(self):
            return "https://new-provider.test/tts/"

    calls = []
    version_info = {
        "success": True,
        "content": {"fe_synbrace_version": "1.2.0"},
    }

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("accessibility"):
            return ResponseStub(200, {"success": True, "exception": None, "content": "serving"})
        if url.endswith("version"):
            return ResponseStub(200, version_info)
        if url.endswith("defaults"):
            return ResponseStub(200, {"success": True, "exception": None, "content": {}})
        raise AssertionError("unexpected URL: {}".format(url))

    instance.provider_manager = ProviderStub()
    instance.set_error("client_network_error", "old failure")
    monkeypatch.setattr(mtts_package.requests, "get", fake_get)

    assert instance.accessable() is True
    assert instance.baseurl == "https://new-provider.test/tts/"
    assert instance.version_info is version_info
    assert not instance.has_error()
    assert [call[0] for call in calls] == [
        "https://new-provider.test/tts/accessibility",
        "https://new-provider.test/tts/version",
        "https://new-provider.test/tts/defaults",
    ]


def test_accessibility_keeps_version_failure_separate_and_clears_stale_cache(
    monkeypatch, instance
):
    class ProviderStub(object):
        last_error = None

        def get_provider(self):
            return True

        def get_provider_id(self):
            return 2

        def get_tts_url(self):
            return "https://provider.test/tts/"

    version_failure = {
        "success": False,
        "status": "client_server_unavailable",
        "exception": "version unavailable",
    }

    def successful_access_get(url, **kwargs):
        if url.endswith("accessibility"):
            return ResponseStub(
                200,
                {"success": True, "exception": None, "content": "serving"},
            )
        if url.endswith("version"):
            return ResponseStub(200, version_failure)
        if url.endswith("defaults"):
            return ResponseStub(
                200,
                {"success": True, "exception": None, "content": {}},
            )
        raise AssertionError("unexpected URL: {}".format(url))

    instance.provider_manager = ProviderStub()
    monkeypatch.setattr(mtts_package.requests, "get", successful_access_get)

    assert instance.accessable() is True
    assert instance.version_info == {
        "success": False,
        "status": "client_server_unavailable",
        "exception": "version unavailable",
        "code": 200,
    }
    assert not instance.has_error()

    monkeypatch.setattr(
        mtts_package.requests,
        "get",
        lambda *args, **kwargs: ResponseStub(
            200,
            {"success": True, "content": "maintenance"},
        ),
    )

    assert instance.accessable() is False
    assert instance.version_info == {"success": False, "content": {}}
    assert instance.status == instance.MttsStatus.SERVER_MAINTAIN


def test_accessibility_only_uses_maintenance_for_explicit_non_serving(monkeypatch, instance):
    class ProviderStub(object):
        last_error = None

        def get_provider(self):
            return True

        def get_provider_id(self):
            return 2

        def get_tts_url(self):
            return "https://provider.test/tts/"

    responses = iter(
        [
            ResponseStub(200, {"success": True, "content": "maintenance"}),
            ResponseStub(
                503,
                {
                    "success": False,
                    "exception": "maica_unified_error: temporary gateway failure",
                },
            ),
        ]
    )
    instance.provider_manager = ProviderStub()
    monkeypatch.setattr(
        mtts_package.requests,
        "get",
        lambda *args, **kwargs: next(responses),
    )

    assert instance.accessable() is False
    assert instance.status == instance.MttsStatus.SERVER_MAINTAIN
    assert instance.error_protocol_status == "client_server_unavailable"

    assert instance.accessable() is False
    assert instance.status == instance.MttsStatus.CONNECT_PROBLEM
    assert instance.error_protocol_status == "client_availability_failed"
    assert instance.error_message == "temporary gateway failure"


def test_renpy_status_flow_keeps_failures_visible():
    main_path = os.path.join(ROOT, "game", "Submods", "MAICA_MttsSubmod", "main.rpy")
    status_path = os.path.join(ROOT, "game", "Submods", "MAICA_MttsSubmod", "status.rpy")
    with open(main_path, "r", encoding="utf-8") as source:
        main_text = source.read()
    with open(status_path, "r", encoding="utf-8") as source:
        status_text = source.read()
    package_path = os.path.join(ROOT, "game", "python-packages", "mtts_package.py")
    with open(package_path, "r", encoding="utf-8") as source:
        package_text = source.read()

    assert "store.mtts_status = mtts_failure_status_text()" in main_text
    assert "if not generation_timed_out and task.is_success and task.result.is_success():" in main_text
    assert "if instance.has_error() or not instance.is_accessable:" in main_text
    assert 'getattr(mtts_instance, "version_info", {})' in main_text
    assert "mtts_instance.get_version()" not in main_text
    assert "store.mtts.is_mtts_frontend_outdated()" in main_text
    assert 'store.persistent.mtts["_outdated"]' not in main_text
    assert "def mtts_failure_status_text():" in status_text
    assert 'response = requests.post(\n                self.get_api_url("register")' in package_text
    assert "def get_strategy(" not in package_text
