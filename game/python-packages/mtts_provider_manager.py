# -*- coding: utf-8 -*-

class DefaultLogger(object):
    """
    默认日志记录器，用于在没有提供日志记录器的情况下输出日志信息。
    """
    def debug(self, msg):
        """输出调试级别的日志"""
        print("[DEBUG] {}".format(msg))

    def info(self, msg):
        """输出信息级别的日志"""
        print("[INFO] {}".format(msg))

    def error(self, msg):
        """输出错误级别的日志"""
        print("[ERROR] {}".format(msg))

    def warning(self, msg):
        """输出警告级别的日志"""
        print("[WARNING] {}".format(msg))


logger = DefaultLogger()

class MTTSProviderManager:
    """MTTS服务提供商管理器 - 实例化模式"""

    # 类级别的共享数据
    _isfailedresponse = {
        "id": 0,
        "name": u"ERROR: 无法获取节点信息",
        "deviceName": u"查看更新日志来获取当前的服务状态, 或者查看submod_log.log获取失败原因",
        "isOfficial": False,
        "portalPage": "https://forum.monika.love/d/3954",
        "servingModel": u"查看更新日志来获取当前的服务状态, 或者查看submod_log.log获取失败原因",
        "modelLink": "",
        # "wsInterface": "wss://maicadev.monika.love/websocket",
        "httpInterface": "https://maicadev.monika.love/api",
        "ttsInterface": "https://maicadev.monika.love/tts"
    }

    _fakelocalprovider = {
        "id": 9999,
        "name": u"本地部署",
        "deviceName": u"当你有可用的本地部署时, 选择此节点",
        "isOfficial": False,
        "portalPage": "https://github.com/PencilMario/MAICA",
        "servingModel": "None",
        "modelLink": "",
        # "wsInterface": "ws://127.0.0.1:5000",
        "httpInterface": "http://127.0.0.1:7000",
        "ttsInterface": "http://127.0.0.1:7000/tts"
    }

    _provider_list = "https://maicadev.monika.love/api/servers"
    

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

    def get_provider(self):
        """获取服务提供商列表"""
        import requests
        try:
            res = requests.get(self._provider_list, json={})
            if res.status_code != 200:
                logger.error("Cannot get providers because server return non 200: {}".format(res.content))
                self._isfailedresponse["deviceName"] = "Cannot get providers because server {}".format(res.status_code)
                new_servers = [self._isfailedresponse, self._fakelocalprovider]
            else:
                res = res.json()
                if res["success"]:
                    self._isMaicaNameServer = res["content"].get("isMaicaNameServer")
                    new_servers = res["content"].get("servers", [])
                    new_servers.append(self._fakelocalprovider)

                    if not self._provider_id:
                        self._provider_id = self._last_provider_id

                    self._servers = new_servers
                    return True
                else:
                    self._isfailedresponse["description"] = res["exception"]
                    new_servers = [self._isfailedresponse, self._fakelocalprovider]
                    logger.error("Cannot get providers because server return: {}".format(res))
        except Exception as e:
            logger.error("Error getting providers: {}".format(e))
            new_servers = [self._isfailedresponse, self._fakelocalprovider]

        self._servers = new_servers
        return False

    def _get_server_by_id(self, server_id):
        """根据ID获取服务器信息"""
        for server in self._servers:
            if int(server["id"]) == server_id:
                return server
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
