# -*- coding: utf-8 -*-

import re

from logger_manager import LoggerWrapper

try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)

class DefaultLogger(object):
    """
    Compatibility logger that follows the active MAS logger.
    """
    def __init__(self, logger=None):
        self._logger = logger or LoggerWrapper()

    def _log(self, method_name, msg, *args, **kwargs):
        msg, args = self._prepare_call(msg, args)
        return getattr(self._logger, method_name)(
            self._log_value(msg),
            *(self._log_value(arg) for arg in args),
            **kwargs
        )

    @staticmethod
    def _prepare_call(msg, args):
        if args and isinstance(msg, string_types):
            try:
                formatted = (
                    msg % args[0]
                    if len(args) == 1 and isinstance(args[0], dict)
                    else msg % args
                )
                return formatted, ()
            except Exception:
                pass

        token_context = (
            isinstance(msg, string_types)
            and "access_token" in msg.lower()
        )
        return msg, tuple(
            "{}***".format(arg[:4])
            if token_context and isinstance(arg, string_types)
            else arg
            for arg in args
        )

    def debug(self, msg, *args, **kwargs):
        return self._log("debug", msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self._log("info", msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self._log("error", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self._log("warning", msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self._log("critical", msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        return self._log("exception", msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        msg, args = self._prepare_call(msg, args)
        return self._logger.log(
            level,
            self._log_value(msg),
            *(self._log_value(arg) for arg in args),
            **kwargs
        )

    def _log_value(self, value):
        if isinstance(value, dict):
            return dict(
                (
                    key,
                    "{}***".format(item[:4])
                    if self._is_token_key(key) and isinstance(item, string_types)
                    else self._log_value(item)
                )
                for key, item in value.items()
            )
        if isinstance(value, tuple):
            return tuple(self._log_value(item) for item in value)
        if isinstance(value, list):
            return [self._log_value(item) for item in value]
        if isinstance(value, string_types):
            return re.sub(
                r'(?P<prefix>["\']?access_token["\']?\s*[:=]\s*["\']?)'
                r'(?P<value>[^,\s}\]"\'&;]+)',
                lambda match: "{}{}***".format(
                    match.group("prefix"), match.group("value")[:4]
                ),
                value,
            )
        return value

    @staticmethod
    def _is_token_key(key):
        return isinstance(key, string_types) and key.lower() == "access_token"

    def __getattr__(self, name):
        return getattr(self._logger, name)


logger = DefaultLogger()

class MTTSProviderManager(object):
    """MTTS服务提供商管理器 - 实例化模式"""

    REQUEST_TIMEOUT = 10

    # 类级别的共享数据
    _isfailedresponse = {
        "id": 0,
        "name": "ERROR: Unable to retrieve node information.",
        "description": "Check the update log to get the current service status, or check submod_log.log for the cause of the failure.",
        "isOfficial": False,
        "portalPage": "https://forum.monika.love/d/3954",
        "servingModel": "Check the update log to get the current service status, or check submod_log.log for the cause of the failure.",
        "modelLink": "",
        # "wsInterface": "wss://maicadev.monika.love/websocket",
        "httpInterface": "https://maicadev.monika.love/api",
        "ttsInterface": "https://maicadev.monika.love/tts"
    }

    _fakelocalprovider = {
        "id": 9999,
        "name": "Local Deployment",
        "description": "When you have an available local deployment, select this node.",
        "isOfficial": False,
        "portalPage": "https://github.com/Mon1-innovation/MAICA_MTTS",
        "servingModel": "None",
        "modelLink": "",
        # "wsInterface": "ws://127.0.0.1:5000",
        "httpInterface": "http://127.0.0.1:7000",
        "ttsInterface": "http://127.0.0.1:7000"
    }

    _provider_list = "https://maicadev.monika.love/tts/servers"
    

    def __init__(self, pid=None):
        """
        初始化MTTSProviderManager实例

        Args:
            pid: 服务提供商ID，如果为None则使用默认值
        """
        self._provider_id = pid
        self._last_provider_id = pid
        self._servers = [self._fakelocalprovider]
        self._isMaicaNameServer = None
        self.last_error = None

    @staticmethod
    def _normalize_failure(data, fallback_status="client_provider_unavailable"):
        try:
            string_types = (basestring,)
        except NameError:
            string_types = (str,)
        if not isinstance(data, dict):
            data = {"exception": u"{}".format(data)}
        status = data.get("status")
        message = data.get("exception")
        if not status and isinstance(message, string_types) and ":" in message:
            candidate, detail = message.split(":", 1)
            if candidate.startswith("maica_"):
                status = candidate.strip()
                message = detail.strip()
        return {
            "success": False,
            "status": status or fallback_status,
            "exception": message or "Failed to retrieve service providers",
            "code": data.get("code"),
        }

    def _set_failed_servers(self, error):
        self.last_error = error
        failed = dict(self._isfailedresponse)
        failed["description"] = error.get("exception") or failed["description"]
        self._servers = [failed, self._fakelocalprovider]

    def get_provider(self):
        """获取服务提供商列表"""
        import requests
        try:
            response = requests.get(self._provider_list, timeout=self.REQUEST_TIMEOUT)
            try:
                data = response.json()
            except Exception:
                error = self._normalize_failure(
                    {"exception": "Provider server returned invalid JSON", "code": response.status_code},
                    "client_response_invalid",
                )
                self._set_failed_servers(error)
                logger.error("Cannot get providers because the response is invalid")
                return False

            if not isinstance(data, dict):
                error = self._normalize_failure(
                    {"exception": "Provider server returned an invalid response"},
                    "client_response_invalid",
                )
                error["code"] = response.status_code
                self._set_failed_servers(error)
                logger.error("Cannot get providers because the response is not an object")
                return False

            if response.status_code == 200 and data.get("success", False):
                content = data.get("content")
                if not isinstance(content, dict) or not isinstance(content.get("servers"), list):
                    error = self._normalize_failure(
                        {"exception": "Provider response has no server list"},
                        "client_response_invalid",
                    )
                    self._set_failed_servers(error)
                    logger.error("Cannot get providers because the response has no server list")
                    return False

                self._isMaicaNameServer = content.get("isMaicaNameServer")
                new_servers = list(content.get("servers", []))
                new_servers.append(self._fakelocalprovider)

                if not self._provider_id:
                    self._provider_id = self._last_provider_id

                self._servers = new_servers
                self.last_error = None
                return True

            error = self._normalize_failure(data)
            error["code"] = response.status_code
            self._set_failed_servers(error)
            logger.error("Cannot get providers because server returned: {}".format(data))
        except Exception as e:
            logger.error("Error getting providers: {}".format(e))
            self._set_failed_servers(self._normalize_failure(
                {"exception": u"{}".format(e)},
                "client_network_error",
            ))

        return False

    def _get_server_by_id(self, server_id):
        """根据ID获取服务器信息"""
        for server in self._servers:
            try:
                if int(server["id"]) == int(server_id):
                    return server
            except (KeyError, TypeError, ValueError):
                continue
        logger.error("Cannot find server by id: {}, returning default failed response".format(server_id))
        return self._isfailedresponse

    def get_api_url(self):
        """获取API URL"""
        if self._provider_id is None:
            logger.warning("Cannot find server by id: {}, returning default failed response".format(self._provider_id))
            return self._isfailedresponse["httpInterface"] + "/"
        return self._get_server_by_id(self._provider_id)["httpInterface"] + "/"

    @staticmethod
    def _ensure_trailing_slash(url):
        if not url:
            return ""
        if not url.endswith("/"):
            url += "/"
        return url

    @staticmethod
    def _derive_tts_from_http(http_interface):
        # Derive a /tts base url from a server httpInterface (usually /api).
        if not http_interface:
            return ""
        base = http_interface.strip()
        if base.endswith("/"):
            base = base[:-1]
        # already a tts endpoint
        if "/tts" in base:
            return base
        # common case: .../api -> .../tts
        if base.endswith("/api"):
            return base[:-4] + "/tts"
        if "/api/" in base:
            return base.replace("/api/", "/tts/")
        # fallback: append /tts
        return base + "/tts"

    def get_tts_url(self):
        # Get TTS base url (for MTTS).
        if self._provider_id is None:
            logger.warning("Cannot find server by id: {}, returning default failed response".format(self._provider_id))
            base = self._isfailedresponse.get("ttsInterface") or self._derive_tts_from_http(self._isfailedresponse.get("httpInterface"))
            return self._ensure_trailing_slash(base)
        server = self._get_server_by_id(self._provider_id)
        base = server.get("ttsInterface") or self._derive_tts_from_http(server.get("httpInterface"))
        return self._ensure_trailing_slash(base)
    def get_server_info(self):
        """获取当前服务器信息"""
        if self._provider_id is None:
            logger.error("Cannot find server by id: {}, returning default failed response".format(self._provider_id))
            return self._isfailedresponse
        return self._get_server_by_id(self._provider_id)

    def set_provider_id(self, pid):
        """设置provider_id"""
        self._provider_id = pid
        if pid:
            self._last_provider_id = pid

    def get_provider_id(self):
        """获取provider_id"""
        return self._provider_id
