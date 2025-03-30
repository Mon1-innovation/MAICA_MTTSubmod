import requests, os
""" I'm sorry for not offering an English ver of this document but it's just too much work for me.
If you want to read in English, use a translator.

此文档是MAICA-MTTS接口的使用文档. 文档内容和API结构可能在此后会有变化, 请开发者关注.

MAICA-MTTS服务的主要功能基于http-post传输, 官方部署的连接地址是https://maicadev.monika.love/mtts.
官方部署强制要求验证access_token, 私有部署可以关闭.

MAICA-MTTS生成音频的接口位于https://maicadev.monika.love/mtts/generate. 你应当遵循以下格式, 以POST形式上传你要生成的语句:
    {"access_token": "你的令牌", "content": "你要生成的语句"}
若生成成功, 接口会返回一段audio/wav格式的音频.
若生成不成功, 接口会返回形如:
    {"success": false, "exception": "生成问题"}

因部署环境可能更多样, MAICA-MTTS后端提供一个接口标记服务器负载能力, 其位于https://maicadev.monika.love/mtts/strategy. 你应当以空白的POST形式请求负载能力.
如果成功请求, 接口会返回:
    {"success": true, "exception": "", "strategy": "服务器负载能力"}
strategy可为L, M, H, 分别代表家用机/边缘服务器, 工作站/个人服务器, 大型服务器. 前端应当遵循告示的负载能力发送请求.
 """

class PrintLogger:
    def debug(self, msg):
        print(msg)
    def info(self, msg):
        print(msg)
    def warning(self, msg):
        print(msg)
    def error(self, msg):
        print(msg)
    def critical(self, msg):
        print(msg)


logger = PrintLogger()

class MTTS:
    def __init__(self, url = "https://maicadev.monika.love/", token = "", cache_path = ""):
        self.baseurl = url
        self.token = token
        self.cache_path = cache_path

    def generate(self, text):
        req = requests.post(self.api_url("mtts/generate"), json={"access_token": self.token, "content": text})
        if req.status_code == 200:
            try:
                req.json()
                logger.error("MTTS:generate failed because {}".format(req.json()))
                raise Exception(req)
            except Exception as e:
                return req.content
        else:
            raise Exception(f"{req.status_code} {req.reason}")
    
    def save_audio(self, audio, filename):
        with open(os.path.join(self.cache_path,  filename), "wb") as f:
            f.write(audio)
    

    def api_url(self, endpoint):
        return self.baseurl + endpoint
    
    def get_strategy(self):
        req = requests.post(self.api_url("mtts/strategy"), json={})
        if req.status_code == 200:
            return req.json()
        else:
            raise Exception(f"{req.status_code} {req.reason}")
        
    def _verify_token(self):
        """
        验证token是否有效。
        
        Returns:
            bool: 验证结果。
        
        """
        import requests
        try:
            res = requests.post(self.api_url("legality"), json={"access_token": self.token})
            if res.status_code == 200:
                res = res.json()
                if res.get("success", False):
                    return res
                else:
                    logger.warning("MTTS:_verify_token not passed: {}".format(res))
                    return res
            else:
                logger.error("MTTS:_verify_token requests.post failed because can't connect to server: {}".format(res.text))
                return {"success":False, "exception": "MTTS:_verify_token requests.post failed"}

        except Exception as e:
            import traceback
            logger.error("MTTS:_verify_token requests.post failed because can't connect to server: {}".format(traceback.format_exc()))
            return {"success":False, "exception": "MTTS:_verify_token failed"}