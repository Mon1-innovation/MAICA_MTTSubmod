import json
import requests, os, chardet
import re
import unicodedata

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel(logging.DEBUG)  # 也可以不设置，不设置就默认用logger的level
logger.addHandler(chlr)

import mtts_provider_manager


class LimitedList(list):
    """Might not have applied to all functionalities!"""
    def __init__(self, max_size, *args, **kwargs):
        self.max_size = max_size
        super(LimitedList, self).__init__(*args, **kwargs)
        
        while len(self) > self.max_size:
            self.pop(0)

    @property
    def list(self):
        while len(self) > self.max_size:
            self.pop(0)
        return list(self)

    def append(self, item):
        if len(self) >= self.max_size:
            self.pop(0)
        super(LimitedList, self).append(item)
    
    def extend(self, iterable):
        for item in iterable:
            self.append(item)
    
    def insert(self, index, item):
        if len(self) >= self.max_size:
            self.pop(0)
        super(LimitedList, self).insert(index, item)
    
    def __repr__(self):
        # return f"LimitedList(max_size={self.max_size}, {super().__repr__()})"
        return "LimitedList(max_size={}, {})".format(self.max_size, super(LimitedList, self).__repr__())

class RuleMatcher:
    """缓存规则匹配器，用于根据文本和标签匹配缓存规则"""

    def __init__(self, rules_config_path):
        """
        初始化规则匹配器

        Args:
            rules_config_path: cache_rules.json 文件的路径
        """
        self.rules_config_path = rules_config_path
        self.rules = []
        self.replace_rules = []
        self.default_action = []
        self._load_rules()

    def _load_rules(self):
        """从配置文件加载规则"""
        try:
            import io
            with io.open(self.rules_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                cache_rules = config.get('cacheRules', )
                self.rules = cache_rules.get('rules', [])
                self.default_action = cache_rules.get('default_action', [])
                # 支持两种配置格式：直接数组或包含rules键的对象
                replace_rules_config = config.get('replaceRules', {})
                if isinstance(replace_rules_config, list):
                    self.replace_rules = replace_rules_config
                else:
                    self.replace_rules = replace_rules_config.get('rules', [])
        except Exception as e:
            raise Exception("Failed to load cache rules: {}".format(e))
            self.rules = []
            self.default_action = []
            self.replace_rules = []

    def _count_content_chars(self, text):
        """
        计算文本中的非符号字符数（字母、数字，排除符号、标点、空白等）
        """
        try:
            count = 0
            for char in text:
                # category(char) 返回字符的 Unicode 类别
                # 'L' 代表 Letter (字母, 包括汉字、日文、韩文、英文字母等)
                # 'N' 代表 Number (数字)
                try:
                    cat = unicodedata.category(char)
                    if cat[0] in ('L', 'N'):
                        count += 1
                except TypeError:
                    continue

            return count
        except Exception as e:
            # 如果发生任何异常，回退到使用 len(text)
            logger.warning("_count_content_chars failed, fallback to len: %s", e)
            return len(text)

    def _apply_text_replacement(self, text, rule):
        """
        应用规则中定义的文本替换

        Args:
            text: 原始文本
            rule: 规则字典

        Returns:
            str: 替换后的文本，如果没有替换则返回None
        """
        replace_pattern = rule.get('replace_pattern')
        replace_with = rule.get('replace_with')

        if replace_pattern is not None:
            try:
                return re.sub(replace_pattern, replace_with if replace_with is not None else '', text)
            except Exception as e:
                logger.warning("Text replacement failed: {}".format(e))
        return None

    def match_cache_rule(self, text, label, store=None):
        """
        根据文本和标签匹配规则

        Args:
            text: 要匹配的文本（翻译后的文本）
            label: 标签名称
            store: Ren'Py store 对象，用于获取变量值（可选）

        Returns:
            dict: 匹配到的规则，如果没有匹配则返回包含默认action的字典
        """
        # 按优先级排序规则（优先级高的在前）
        sorted_rules = sorted(self.rules, key=lambda r: r.get('priority', 0), reverse=True)

        for rule in sorted_rules:
            # 检查最小长度要求（非符号字符长度）
            min_len = rule.get('min_len', 0)

            if self._count_content_chars(text) < min_len:
                logger.warning("Text length is too short: {}".format(text))
                continue

            # 检查 variable 字段
            variables = rule.get('variable', [])
            if variables and store is not None:
                for var_name in variables:
                    try:
                        var_value = getattr(store, var_name, None)
                        if var_value is not None and str(var_value) in text:
                            return rule
                    except Exception as e:
                        logger.warning("Failed to get variable '{}': {}".format(var_name, e))

            # 尝试匹配 regex_text
            regex_text = rule.get('regex_text')
            if regex_text:
                try:
                    if re.search(regex_text, text):
                        # 执行文本替换（如果规则包含替换字段）
                        replaced_text = self._apply_text_replacement(text, rule)
                        if replaced_text is not None:
                            rule['replaced_text'] = replaced_text
                        return rule
                except Exception as e:
                    logger.warning("Invalid regex_text pattern: {}".format(e))

            # 尝试匹配 regex_label
            regex_label = rule.get('regex_label')
            if regex_label:
                try:
                    if re.match(regex_label, label):
                        # 执行文本替换（如果规则包含替换字段）
                        replaced_text = self._apply_text_replacement(text, rule)
                        if replaced_text is not None:
                            rule['replaced_text'] = replaced_text
                        return rule
                except Exception as e:
                    logger.warning("Invalid regex_label pattern: {}".format(e))

        # 如果没有匹配任何规则，返回默认action
        return {
            'action': self.default_action,
            'is_default': True
        }

    def apply_replace_rules(self, text, store=None):
        """
        应用所有替换规则到文本

        Args:
            text: 原始文本
            store: Ren'Py store 对象，用于获取变量值（可选）

        Returns:
            str: 应用替换后的文本
        """
        # 按优先级排序规则（优先级高的在前）
        sorted_rules = sorted(self.replace_rules, key=lambda r: r.get('priority', 0), reverse=True)

        result = text
        for rule in sorted_rules:
            # 检查 variable 字段
            variables = rule.get('variable', [])
            if variables and store is not None:
                for var_name in variables:
                    try:
                        var_value = getattr(store, var_name, None)
                        if var_value is not None and str(var_value) in result:
                            break
                    except Exception as e:
                        logger.warning("Failed to get variable '{}': {}".format(var_name, e))

            regex_pattern = rule.get('regex_text')
            replace_with = rule.get('replace_with', '')

            if regex_pattern is not None:
                try:
                    # 先检查是否有匹配
                    if re.search(regex_pattern, result):
                        new_result = re.sub(regex_pattern, replace_with, result)
                        logger.debug("Applied replace rule '{}': {} -> {}".format(
                            rule.get('name', 'unnamed'),
                            regex_pattern,
                            replace_with if replace_with else '(empty)'
                        ))
                        result = new_result
                except Exception as e:
                    logger.warning("Replace rule '{}' failed: {}".format(
                        rule.get('name', 'unnamed'),
                        e
                    ))
        return result

    def get_action(self, text, label, original_text=None, store=None):
        """
        获取匹配规则的action

        Args:
            text: 要匹配的文本
            label: 标签名称
            original_text: 原始文本（可选）
            store: Ren'Py store 对象，用于获取变量值（可选）

        Returns:
            list: action列表
        """
        rule = self.match_cache_rule(text, label, store)
        return rule.get('action', self.default_action)

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
        
        self._cache_size = None
    
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
        
    @property
    def cache_size(self):
        if self._cache_size == None:
            self._cache_size = self.get_total_cache_size_mb()
        return self._cache_size

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
        self._cache_size = self.get_total_cache_size_mb()

class MTTS:
    def __init__(self, url = "https://maicadev.monika.love/tts/", token = "", cache_path = ""):
        self.baseurl = url
        self.token = token
        self.cache_path = cache_path
        self.target_lang = "zh"
        self.cache = DataCache(cache_path)
        self.local_cache = True
        self.remote_cache = True
        self.lossless = False
        self.__accessable = False
        self._ignore_accessable = False
        
        self.enabled = False
        self.volume = 1.0
        self.acs_enabled = True
        self.ministathud = True
        self.drift_statshud_l = False
        self.drift_statshud_r = False
        # self.user_acc = ""
        # self.provider_id = None
        self.provider_manager = mtts_provider_manager.MTTSProviderManager()


        self.workload_raw = {
            "None":{
                "0": {
                    "name": "Super PP 0",
                    "vram": "100000 MiB",
                    "mean_utilization": 100,
                    "mean_memory": 21811,
                    "mean_consumption": 100,
                    "tflops": 400,
                },                
                "1": {
                    "name": "if you see this, requests workload is failed",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "tflops": 400,
                    "mean_consumption": 100
                },
            },
            "None2":{
                "0": {
                    "name": "Super PP 2",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "tflops": 400,
                    "mean_consumption": 100
                    
                },                
                "1": {
                    "name": "Super PP 3",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "tflops": 400,
                    "mean_consumption": 100
                },
            },
            "onliners":0
        }


        # 初始化缓存规则匹配器
        rules_config_path = os.path.join(cache_path, "..", "cache_rules.json")
        if os.path.exists(rules_config_path):
            self.rule_matcher = RuleMatcher(rules_config_path)
        else:
            self.rule_matcher = None

    def generate(self, text, emotion=u"微笑", label_name="none", player_name="", target_lang="zh"):
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
        req = requests.get(self.get_api_url("generate"), params={"access_token": self.token,
             "content": json.dumps({
                "text": text,
                "emotion": emotion,
                "target_lang": target_lang,
                "persistence": self.remote_cache,
                "lossless": self.lossless
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
            logger.error("MTTS:generate failed because {} {}".format(req.reason, req.text))
            raise Exception("{} {}".format(req.status_code, req.reason))
    
    def save_audio(self, audio, filename):
        with open(os.path.join(self.cache_path,  filename), "wb") as f:
            f.write(audio)
    

    def get_api_url(self, endpoint):
        return self.baseurl + endpoint
    
    def get_strategy(self):
        # 请求服务器负载能力 L/M/H
        # L: 家用机/边缘服务器 / 强制本地+远程
        # M: 工作站/个人服务器 / 强制远程缓存
        # H: 大型服务器
        req = requests.post(self.get_api_url("strategy"), json={})
        if req.status_code == 200:
            return req.json()["strategy"]
        else:
            raise Exception("{} {}".format(req.status_code, req.reason))

    def _gen_token(self, account, pwd, token = "", email = None):
        if token != "":
            self.token = token
            return
        if not self.__accessable and token == "":
            return logger.error("_gen_token:MTTS server not serving.")
        import requests
        data = {
            "username":account,
            "password":pwd
        }
        if email:
            data = {
            "email":email,
            "password":pwd
        }
        try:
            import json
            response = requests.get(self.get_api_url("register"), params={"content":json.dumps(data)}, timeout=5)
            if (response.status_code != 200): 
                raise Exception("MTTS::_gen_token response process failed because server return {}/{}".format(response.status_code, response.text))

        except Exception as e:
            import traceback
            logger.error("MTTS::_gen_token requests failed because can't connect to server: {}".format(e))
            return
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success"):
                self.token = response_data.get("content")
            else:
                logger.error("MTTS::_gen_token response process failed because server response failed: {}".format(response_data))
        else:
            logger.error("MTTS::_gen_token response process failed because server return {}".format(response.status_code))
        return

    def _verify_token(self):
        """
        验证token是否有效。
        
        Returns:
            bool: 验证结果。
        
        """
        if not self.__accessable:
            return {"success": False, "exception": "MTTS: not serving"}
        import requests
        try:
            res = requests.get(self.get_api_url("legality"), params={"access_token": self.token})
            if res.status_code == 200:
                res = res.json()
                if res.get("success", False):
                    return res
                else:
                    logger.warning("MTTS::_verify_token not passed: {}".format(res))
                    return res
            else:
                logger.error("MTTS::_verify_token requests.post failed because can't connect to server: {}".format(res.text))
                return {"success":False, "exception": "MTTS::_verify_token requests.post failed"}

        except Exception as e:
            import traceback
            logger.error("MTTS::_verify_token requests.post failed because can't connect to server: {}".format(traceback.format_exc()))
            return {"success":False, "exception": "MTTS::_verify_token failed"}
    def update_workload(self):
        """
        更新工作负载信息（后台执行）。

        Args:
            无。

        Returns:
            threading.Thread对象，可以用于检查线程的状态。
        """
        import requests
        import threading
        if not self.__accessable:
            logger.error("Maica is not serving")
            return None

        def task():
            res = requests.get(self.get_api_url("workload"))
            if res.status_code == 200:
                data = res.json()
                if data["success"]:
                    self.workload_raw = data["content"]
                    #logger.debug("Workload updated successfully.")
                else:
                    logger.error("Failed to update workload: {}".format(data))
            else:
                logger.error("Failed to update workload.")

        thread = threading.Thread(target=task)
        thread.daemon = True  # Optional: allow the program to exit even if the thread is running
        thread.start()
        return thread

    def get_workload_lite(self):
        """
        获取最高负载设备的占用

        Args:
            无。

        Returns:
            工作负载信息简化版。

        """

        data = {
            "avg_usage": 0,
            "max_usage": 0,
            "total_vmem": 0,
            "total_inuse_vmem": 0,
            "total_w": 0,
            "mem_pencent":0,
            "max_tflops":0,
            "cur_tflops":0,
            "onliners":0
        }
        if not self.__accessable:
            return data
    # Use iteritems() for Python 2
        avgcount = 0
        if PY2:
            # 处理 onliners 键
            if isinstance(self.workload_raw.get('onliners'), (int, float)):
                data['onliners'] = int(self.workload_raw['onliners'])

            for group_name, group in self.workload_raw.iteritems():
                if group_name == 'onliners':
                    continue
                for card in group.itervalues():
                    if card["mean_utilization"] > data["max_usage"]:
                        data["max_usage"] = card["mean_utilization"]
                    data["avg_usage"] += card["mean_utilization"]
                    avgcount+=1
                    data["total_vmem"] += int(card["vram"][:-4].strip())
                    data["total_inuse_vmem"] += card["mean_memory"]
                    data["total_w"] += card["mean_consumption"]
                    data["max_tflops"] += int(card["tflops"])
                    data["cur_tflops"] += int(card["tflops"]) * card["mean_utilization"] * 0.01
        elif PY3:
            # 处理 onliners 键
            if isinstance(self.workload_raw.get('onliners'), (int, float)):
                data['onliners'] = int(self.workload_raw['onliners'])

            for group_name, group in self.workload_raw.items():
                if group_name == 'onliners':
                    continue
                for card in group.values():
                    if card["mean_utilization"] > data["max_usage"]:
                        data["max_usage"] = card["mean_utilization"]
                    data["avg_usage"] += card["mean_utilization"]
                    avgcount+=1
                    data["total_vmem"] += int(card["vram"][:-4].strip())
                    data["total_inuse_vmem"] += card["mean_memory"]
                    data["total_w"] += card["mean_consumption"]
                    data["max_tflops"] += int(card["tflops"])
                    data["cur_tflops"] += int(card["tflops"]) * card["mean_utilization"] * 0.01

        if avgcount > 0:
            data["avg_usage"] /= avgcount
        return data

    def get_version(self):

        """
        获取版本信息。
        
        Returns: dict:
            curr_version: 后端当前版本
            legc_version: 兼容的最旧版本 
            fe_synbrace_version: Synbrace前端的可用最旧版本
            exception: 默认None
            success: bool
        
        """

        import requests
        import traceback

        try:
            res = requests.get(self.get_api_url("version"))
            if res.status_code == 200:
                res = res.json()
                if res.get("success", False):
                    return res
                else:
                    logger.warning("MTTS: Get version failed: {}".format(res))
                    return res
            else:
                logger.error("MTTS: Get version request failed: Server returned {} - {}".format(res.status_code, res.text))
                return {"success": False, "exception": "MTTS: Get version request failed"}
            
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("MTTS: Get version request encountered an error: {}".format(error_msg))
            return {"success": False, "exception": "MTTS: Get version request failed"}
        
    @property
    def provider_id(self):
        return self.provider_manager.get_provider_id()

    @provider_id.setter
    def provider_id(self, value):
        self.provider_manager.set_provider_id(self.provider_id)
    
    def accessable(self):
        if self._ignore_accessable:
            self.__accessable = True
            return
        
        try:
            if not self.provider_manager.get_provider():
                if self.provider_id != 9999:
                    self.__accessable = False
                    return
        except Exception as e:
            logger.error("accessable(): MTTS get Service Provider Error: {}".format(e))
            if self.provider_id != 9999:
                self.__accessable = False
                return


        import requests, json
        res = requests.get(self.get_api_url("accessibility"))
        logger.debug("accessable(): try get accessibility from {}".format(self.get_api_url("accessibility")))
        d = res.json()
        if d.get(u"success", False):
            self._serving_status = d["content"]
            if self._serving_status != "serving" and not self._ignore_accessable:
                self.__accessable = False
                logger.error("accessable(): Maica is not serving: {}".format(d["content"]))
            else:
                self.__accessable = True
        else:
            self.__accessable = False
            logger.error("accessable(): Maica is not serving: request failed: {}".format(d))
    
    @property
    def is_accessable(self):
        return self.__accessable
import threading

class AsyncTask(object):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self.result = None
        self.exception = None
        self.traceback = None
        self.is_finished = False
        self.is_success = False
        
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        try:
            self.result = self._func(*self._args, **self._kwargs)
            self.is_success = True
        except Exception as e:
            import traceback
            self.exception = e
            self.traceback = traceback.format_exc()
            self.is_success = False
            logger.error("AsyncTask failed with exception: %s", e)
            logger.debug("Traceback: %s", self.traceback)
        finally:
            self.is_finished = True

    @property
    def is_alive(self):
        return self._thread.is_alive()

    def wait(self, timeout=None):
        """等待任务完成（可选超时时间）"""
        self._thread.join(timeout=timeout)


