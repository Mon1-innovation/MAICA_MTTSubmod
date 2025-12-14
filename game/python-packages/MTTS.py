import json
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


import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

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

class MTTSAudio:
    def __init__(self, data):
        self.data = data
    
    def is_success(self):
        return not (self.data[-1] == "}" and self.data[0] == "{")
    
class DataCache:
    def __init__(self, cache_path):
        self.cache_path = cache_path
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
    
    def save(self, filename, data):
        with open(os.path.join(self.cache_path, filename), "wb") as f:
            f.write(data)
    
    def load(self, filename):
        with open(os.path.join(self.cache_path, filename), "rb") as f:
            return f.read()
    
    def get_cachename(self, label_name, text):
        # 生成text的hash值
        import hashlib
        hash_object = hashlib.md5(text.encode())
        return label_name + "_" + hash_object.hexdigest()[:8]

    def is_cached(self, label_name, text):
        # 检查缓存是否存在
        filename = self.get_cachename(label_name, text)
        return os.path.exists(os.path.join(self.cache_path, filename))
    
    def get_total_cache_size_mb(self):
        # 获取缓存目录的总大小
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.cache_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)
        

    def clear_cache(self):
        # 清空缓存目录
        for dirpath, dirnames, filenames in os.walk(self.cache_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    os.remove(fp)
                except OSError:
                    logger.warning("Failed to delete file: {}".format(fp))
        logger.info("Cache cleared.")

class MTTS:
    def __init__(self, url = "https://maicadev.monika.love/tts/", token = "", cache_path = ""):
        self.baseurl = url
        self.token = token
        self.cache_path = cache_path
        self.target_lang = "zh"
        self.cache = DataCache(cache_path)
        self.conversion = True
        self.local_cache = True
        self.remote_cache = True

    def generate(self, text, emotion=u"微笑", label_name="none", player_name=""):
        if self.cache.is_cached(label_name, text) and self.local_cache:
            class FakeReqData:
                def __init__(self, data):
                    self.data = data
                def is_success(self):
                    return True
                def status_code(self):
                    return 200
                def reason(self):
                    return "OK"
            logger.debug("MTTS:load from cache {}".format((label_name, text)))
            return FakeReqData(self.cache.load(self.cache.get_cachename(label_name, text)))
        if player_name and len(player_name.encode()) >= 3 and player_name in text:
            rc_override = False
        else:
            rc_override = self.remote_cache
        req = requests.get(self.api_url("generate"), params={"access_token": self.token,
             "content": json.dumps({
                "text": text,
                "emotion": emotion,
                "target_lang": "zh",
                "persistence": True,
                "lossless": False
            })
        })
        if req.status_code == 200:
            try:
                req.json()
                logger.error("MTTS:generate failed because {}".format(req.json()))
                raise Exception(req)
            except Exception as e:
                self.cache.save(self.cache.get_cachename(label_name, text), req.content)
                logger.debug("MTTS:generated {}".format((label_name, text)))
                return MTTSAudio(req.content)
        else:
            raise Exception("{} {}".format(req.status_code, req.reason))
    
    def save_audio(self, audio, filename):
        with open(os.path.join(self.cache_path,  filename), "wb") as f:
            f.write(audio)
    

    def api_url(self, endpoint):
        return self.baseurl + endpoint
    
    def get_strategy(self):
        # 请求服务器负载能力 L/M/H
        # L: 家用机/边缘服务器 / 强制本地+远程
        # M: 工作站/个人服务器 / 强制远程缓存
        # H: 大型服务器
        req = requests.post(self.api_url("strategy"), json={})
        if req.status_code == 200:
            return req.json()["strategy"]
        else:
            raise Exception("{} {}".format(req.status_code, req.reason))
        
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
        
import threading

class AsyncTask(object):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self.result = None
        self.exception = None
        self.is_finished = False
        self.is_success = False
        
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        try:
            self.result = self._func(*self._args, **self._kwargs)
            self.is_success = True
        except Exception as e:
            self.exception = e
            self.is_success = False
        finally:
            self.is_finished = True

    @property
    def is_alive(self):
        return self._thread.is_alive()

    def wait(self, timeout=None):
        """等待任务完成（可选超时时间）"""
        self._thread.join(timeout=timeout)


