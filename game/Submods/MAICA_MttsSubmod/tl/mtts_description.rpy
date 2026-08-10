translate chinese python:

    import mtts_provider_manager as mpm

    mpm.MTTSProviderManager._isfailedresponse.update(
        {
            "name":"错误：无法获取节点信息",
            "description": "查看更新日志以获取当前服务状态，或查看 submod_log.log 获取失败原因",
            "isOfficial": False,
            "portalPage": "https://forum.monika.love/d/3954",
            "servingModel": "查看更新日志以获取当前服务状态，或查看 submod_log.log 获取失败原因",
            "modelLink": "",
            "wsInterface": "wss://maicadev.monika.love/websocket",
            "httpInterface": "https://maicadev.monika.love/api"
        }
    )
    mpm.MTTSProviderManager._fakelocalprovider.update(
        {
            "name":"本地部署",
            "description": "当你有可用的本地部署时，选择此节点",
            "isOfficial": False,
            "portalPage": "https://github.com/PencilMario/MAICA",
            "servingModel": "None",
            "modelLink": "",
            "wsInterface": "ws://127.0.0.1:5000",
            "httpInterface": "http://127.0.0.1:6000",
        }
    )
