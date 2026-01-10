translate english python:

    import mtts_provider_manager as mpm

    mpm.MTTSProviderManager._isfailedresponse.update(
        {
            "name":"ERROR: Unable to retrieve node information.",
            "description": "Check the update log to get the current service status, or check submod_log.log for the cause of the failure.",
            "isOfficial": False,
            "portalPage": "https://forum.monika.love/d/3954",
            "servingModel": "Check the update log to get the current service status, or check submod_log.log for the cause of the failure.",
            "modelLink": "",
            "wsInterface": "wss://maicadev.monika.love/websocket",
            "httpInterface": "https://maicadev.monika.love/api"
        }
    )
    mpm.MTTSProviderManager._fakelocalprovider.update(
        {
            "name":"Local Deployment",
            "description": "When you have an available local deployment, select this node.",
            "isOfficial": False,
            "portalPage": "https://github.com/PencilMario/MAICA",
            "servingModel": "None",
            "modelLink": "",
            "wsInterface": "ws://127.0.0.1:5000",
            "httpInterface": "http://127.0.0.1:6000",
        }
    )