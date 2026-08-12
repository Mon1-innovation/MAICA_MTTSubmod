import json
import requests, os, chardet
import re
import unicodedata

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
import logging

class TokenRedactionFilter(logging.Filter):
    """Filter that redacts sensitive tokens from log messages."""
    def filter(self, record):
        # Redact access_token values in log messages
        record.msg = self._redact_tokens(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._redact_tokens(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._redact_tokens(str(arg)) for arg in record.args)
        return True

    def _redact_tokens(self, text):
        """Replace token values with first 4 characters + ***"""
        # Pattern: access_token=<value> where value is alphanumeric, +, /, or - (URL-safe base64)
        def replace_token(match):
            full_match = match.group(0)
            token_value = match.group(1)
            prefix = token_value[:4] if len(token_value) >= 4 else token_value
            return "access_token={}***".format(prefix)

        return re.sub(r'access_token=([a-zA-Z0-9+/_-]+)', replace_token, text)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel(logging.DEBUG)  # 也可以不设置，不设置就默认用logger的level
logger.addHandler(chlr)
logger.addFilter(TokenRedactionFilter())

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


class ExtendTextTracker(object):
    def __init__(self, default_interjection="{fast}"):
        self.default_interjection = default_interjection
        self.pending_raw = None

    def begin_extend(self, raw_text):
        self.pending_raw = raw_text

    def resolve(self, text, previous_text=None, interjection=None):
        if self.pending_raw is not None:
            raw_text = self.pending_raw
            self.pending_raw = None
            return True, raw_text

        marker = interjection if interjection is not None else self.default_interjection
        if previous_text:
            prefix = previous_text + marker
            if text.startswith(prefix):
                return True, text[len(prefix):]

        return False, text

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

    def _evaluate_condition(self, condition_expr, text, label, store=None):
        """
        评估条件表达式

        Args:
            condition_expr: 条件表达式字符串（Python代码）
            text: 要匹配的文本
            label: 标签名称
            store: Ren'Py store 对象，用于获取变量值（可选）

        Returns:
            bool: 表达式评估结果，如果出错返回False
        """
        if not condition_expr:
            return False

        try:
            # 构建安全的求值上下文
            safe_dict = {
                'text': text,
                'label': label,
                'len': len,
                're': re,
            }

            # 从store对象中提取变量到安全字典
            if store is not None:
                try:
                    # 获取store对象的所有属性（变量）
                    store_vars = {}
                    for attr_name in dir(store):
                        if not attr_name.startswith('_'):  # 跳过私有属性
                            try:
                                store_vars[attr_name] = getattr(store, attr_name)
                            except:
                                pass
                    safe_dict.update(store_vars)
                except Exception as e:
                    logger.warning("Failed to extract variables from store: {}".format(e))

            # 使用eval执行表达式（在受限的命名空间中）
            result = eval(condition_expr, {"__builtins__": {}}, safe_dict)
            return bool(result)

        except Exception as e:
            logger.warning("Failed to evaluate condition '{}': {}".format(condition_expr, e))
            return False

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

            # 尝试匹配 condition 表达式（新增）
            condition = rule.get('condition')
            if condition:
                if self._evaluate_condition(condition, text, label, store):
                    return rule

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


class MTTSRequestError(Exception):
    """A request failure already normalized into the MTTS status model."""

    def __init__(self, result):
        self.result = result
        message = result.get("exception") or result.get("status") or "MTTS request failed"
        Exception.__init__(self, message)


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
    HTTP_TIMEOUT = 10

    class MttsStatus(object):
        STANDING_BY = 10000
        TOKEN_MISSING = 13400
        TOKEN_CORRUPTED = 13401
        TOKEN_INVALID = 13402
        LOGIN_BLOCKED = 13403
        ACCOUNT_BANNED = 13404
        EMAIL_UNVERIFIED = 13405
        TOS_UNACCEPTED = 13406
        SERVER_REJECTED = 13407
        SERVER_ERROR = 13408
        TOKEN_GENERATION_FAILED = 13409
        GENERATION_FAILED = 13410
        CONNECT_PROBLEM = 13411
        RESPONSE_INVALID = 13412
        SERVER_MAINTAIN = 13413
        FAILED_GET_NODE = 13414

        _protocol_error_map = {
            "client_token_missing": TOKEN_MISSING,
            "maica_login_token_corrupted": TOKEN_CORRUPTED,
            "maica_login_token_invalid": TOKEN_INVALID,
            "client_auth_failed": TOKEN_INVALID,
            "maica_login_f2b": LOGIN_BLOCKED,
            "maica_login_banned": ACCOUNT_BANNED,
            "maica_login_email_unchecked": EMAIL_UNVERIFIED,
            "maica_login_tos_unaccepted": TOS_UNACCEPTED,
            "maica_unified_warning": SERVER_REJECTED,
            "maica_unified_error": SERVER_ERROR,
            "client_token_generation_failed": TOKEN_GENERATION_FAILED,
            "client_generation_failed": GENERATION_FAILED,
            "client_network_error": CONNECT_PROBLEM,
            "client_response_timeout": CONNECT_PROBLEM,
            "client_response_invalid": RESPONSE_INVALID,
            "client_server_unavailable": SERVER_MAINTAIN,
            "client_provider_unavailable": FAILED_GET_NODE,
        }

        _descriptions = {
            STANDING_BY: u"Standing by",
            TOKEN_MISSING: u"No token is configured",
            TOKEN_CORRUPTED: u"The token is corrupted",
            TOKEN_INVALID: u"The account or password is invalid",
            LOGIN_BLOCKED: u"Login is temporarily blocked",
            ACCOUNT_BANNED: u"The account is suspended",
            EMAIL_UNVERIFIED: u"The account email is not verified",
            TOS_UNACCEPTED: u"The latest terms are not accepted",
            SERVER_REJECTED: u"An user level exception happened",
            SERVER_ERROR: u"An server level exception happened",
            TOKEN_GENERATION_FAILED: u"Token generation failed",
            GENERATION_FAILED: u"Speech generation failed",
            CONNECT_PROBLEM: u"Unable to connect to the server",
            RESPONSE_INVALID: u"The server returned an invalid response",
            SERVER_MAINTAIN: u"The server is unavailable or under maintenance",
            FAILED_GET_NODE: u"Failed to retrieve an available service provider",
        }

        @classmethod
        def from_protocol_status(cls, status, fallback=None):
            return cls._protocol_error_map.get(
                status,
                cls.SERVER_REJECTED if fallback is None else fallback,
            )

        @classmethod
        def get_description(cls, status):
            return cls._descriptions.get(status, u"Unknown MTTS failure")

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
        self.status = self.MttsStatus.STANDING_BY
        self.error_protocol_status = None
        self.error_message = None
        self.error_protocol_code = None
        
        self.enabled = False
        self.volume = 1.0
        self.acs_enabled = True
        self.ministathud = True
        self.drift_statshud_l = False
        self.drift_statshud_r = False
        self.generate_timeout = 15
        # self.user_acc = ""
        # self.provider_id = None
        self.provider_manager = mtts_provider_manager.MTTSProviderManager()

        self.default_settings = {}


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

    def clear_error(self):
        self.status = self.MttsStatus.STANDING_BY
        self.error_protocol_status = None
        self.error_message = None
        self.error_protocol_code = None

    def set_error(self, status, message=None, code=None, fallback=None):
        self.error_protocol_status = status
        self.error_message = message
        self.error_protocol_code = code
        self.status = self.MttsStatus.from_protocol_status(status, fallback)

    def has_error(self):
        return self.error_protocol_status is not None

    def get_error_result(self):
        return {
            "success": False,
            "status": self.error_protocol_status,
            "exception": self.error_message,
            "code": self.error_protocol_code,
        }

    def get_status_description(self):
        return self.MttsStatus.get_description(self.status)

    @staticmethod
    def _normalize_failure(data, fallback_status):
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
        return status or fallback_status, message

    def _set_response_failure(self, data, fallback_status, code=None, fallback=None):
        status, message = self._normalize_failure(data, fallback_status)
        self.set_error(status, message, code, fallback)
        return self.get_error_result()

    def _auth_headers(self):
        return {"Authorization": "Bearer {}".format(self.token)} if self.token else {}

    @staticmethod
    def _response_json(response):
        try:
            data = response.json()
        except Exception:
            return None
        return data if isinstance(data, dict) else None

    def generate(self, text, emotion=u"微笑", label_name="none", player_name="", target_lang="zh", kwargs = {}):
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
            self.clear_error()
            return FakeReqData(self.cache.load(self.cache.get_cachename(label_name, text)))
        if player_name and len(player_name.encode()) >= 3 and player_name in text:
            rc_override = False
        else:
            rc_override = self.remote_cache

        params = {
                "text": text,
                "emotion": emotion,
                "target_lang": target_lang,
                "persistence": self.remote_cache,
                "lossless": self.lossless
            }
        params.update(**kwargs)
        if not self.token:
            self.set_error(
                "client_token_missing",
                "Access token is not configured",
                fallback=self.MttsStatus.TOKEN_MISSING,
            )
            raise MTTSRequestError(self.get_error_result())

        try:
            response = requests.get(
                self.get_api_url("generate"),
                params={"content": json.dumps(params)},
                headers=self._auth_headers(),
                timeout=self.generate_timeout,
            )
        except Exception as e:
            self.set_error("client_network_error", u"{}".format(e))
            logger.error("MTTS:generate request failed: {}".format(e))
            raise MTTSRequestError(self.get_error_result())

        response_data = self._response_json(response)
        if response_data is not None:
            fallback = self.MttsStatus.SERVER_ERROR if response.status_code >= 500 else self.MttsStatus.GENERATION_FAILED
            result = self._set_response_failure(
                response_data,
                "client_generation_failed",
                response.status_code,
                fallback,
            )
            logger.error("MTTS:generate failed because {}".format(response_data))
            raise MTTSRequestError(result)

        if response.status_code != 200 or not response.content:
            result = self._set_response_failure(
                {"exception": getattr(response, "reason", None) or "Empty audio response"},
                "client_generation_failed",
                response.status_code,
                self.MttsStatus.SERVER_ERROR if response.status_code >= 500 else self.MttsStatus.GENERATION_FAILED,
            )
            logger.error("MTTS:generate failed with HTTP {}".format(response.status_code))
            raise MTTSRequestError(result)

        self.clear_error()
        self.cache.save(self.cache.get_cachename(label_name, text), response.content)
        logger.debug("MTTS:generated {}".format((label_name, text)))
        return MTTSAudio(response.content)
    
    def save_audio(self, audio, filename):
        with open(os.path.join(self.cache_path,  filename), "wb") as f:
            f.write(audio)
    

    def get_api_url(self, endpoint):
        return self.baseurl + endpoint
    
    def _gen_token(self, account, pwd, token = "", email = None):
        if token != "":
            self.token = token
            self.clear_error()
            return
        if not self.__accessable and token == "":
            self.set_error(
                "client_server_unavailable",
                "MTTS server is not serving",
                fallback=self.MttsStatus.SERVER_MAINTAIN,
            )
            return logger.error("_gen_token:MTTS server not serving.")
        self.token = ""
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
            response = requests.post(
                self.get_api_url("register"),
                json={"content": data},
                timeout=self.HTTP_TIMEOUT,
            )
        except Exception as e:
            self.set_error("client_network_error", u"{}".format(e))
            logger.error("MTTS::_gen_token request failed: {}".format(e))
            return

        response_data = self._response_json(response)
        if response_data is None:
            self.set_error("client_response_invalid", "Token response was not valid JSON", response.status_code)
            logger.error("MTTS::_gen_token returned an invalid response")
            return
        if response.status_code != 200 or not response_data.get("success", False):
            self._set_response_failure(
                response_data,
                "client_token_generation_failed",
                response.status_code,
                self.MttsStatus.TOKEN_GENERATION_FAILED,
            )
            logger.error("MTTS::_gen_token failed: {}".format(response_data))
            return

        self.token = response_data.get("content") or ""
        if not self.token:
            self.set_error("client_response_invalid", "Token response did not contain a token", response.status_code)
            return
        self.clear_error()
        return

    def _verify_token(self):
        """
        验证token是否有效。
        
        Returns:
            bool: 验证结果。
        
        """
        if self.error_protocol_status and not self.token:
            return self.get_error_result()
        if not self.token:
            self.set_error(
                "client_token_missing",
                "Access token is not configured",
                fallback=self.MttsStatus.TOKEN_MISSING,
            )
            return self.get_error_result()
        if not self.__accessable:
            self.set_error(
                "client_server_unavailable",
                "MTTS server is not serving",
                fallback=self.MttsStatus.SERVER_MAINTAIN,
            )
            return self.get_error_result()
        try:
            response = requests.get(
                self.get_api_url("legality"),
                headers=self._auth_headers(),
                timeout=self.HTTP_TIMEOUT,
            )
        except Exception as e:
            self.set_error("client_network_error", u"{}".format(e))
            logger.error("MTTS::_verify_token request failed: {}".format(e))
            return self.get_error_result()

        result = self._response_json(response)
        if result is None:
            self.set_error("client_response_invalid", "Token verification response was not valid JSON", response.status_code)
            return self.get_error_result()
        if response.status_code == 200 and result.get("success", False):
            self.clear_error()
            return result

        normalized = self._set_response_failure(
            result,
            "client_auth_failed",
            response.status_code,
            self.MttsStatus.TOKEN_INVALID,
        )
        logger.warning("MTTS::_verify_token not passed: {}".format(result))
        return normalized
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
            try:
                response = requests.get(self.get_api_url("workload"), timeout=self.HTTP_TIMEOUT)
                data = self._response_json(response)
                if response.status_code == 200 and data and data.get("success", False):
                    content = data.get("content")
                    if isinstance(content, dict):
                        self.workload_raw = content
                        return
                if data is None:
                    self.set_error("client_response_invalid", "Workload response was not valid JSON", response.status_code)
                else:
                    self._set_response_failure(data, "client_server_unavailable", response.status_code)
                logger.error("Failed to update workload: {}".format(data))
            except Exception as e:
                self.set_error("client_network_error", u"{}".format(e))
                logger.error("Failed to update workload: {}".format(e))

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
            response = requests.get(self.get_api_url("version"), timeout=self.HTTP_TIMEOUT)
            result = self._response_json(response)
            if result is None:
                logger.error("MTTS: Get version returned an invalid response")
                return {
                    "success": False,
                    "status": "client_response_invalid",
                    "exception": "Version response was not valid JSON",
                    "code": response.status_code,
                }
            if response.status_code == 200 and result.get("success", False):
                return result

            status, message = self._normalize_failure(result, "client_server_unavailable")
            logger.warning("MTTS: Get version failed: {}".format(result))
            return {
                "success": False,
                "status": status,
                "exception": message,
                "code": response.status_code,
            }
            
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("MTTS: Get version request encountered an error: {}".format(error_msg))
            return {
                "success": False,
                "status": "client_network_error",
                "exception": "Version request failed",
                "code": None,
            }

    def get_defaults(self):
        """
        获取默认设置。

        Returns: dict:
            Dictionary containing default hyperparameters (parallel_infer, repetition_penalty, seed, etc.)
            Returns empty dict if request fails or server not accessible.
        """
        import requests
        import traceback

        if not self.__accessable:
            return {}

        try:
            res = requests.get(
                self.get_api_url("defaults"),
                headers=self._auth_headers(),
                timeout=self.HTTP_TIMEOUT,
            )
            result = self._response_json(res)
            if res.status_code == 200 and result and result.get("success", False):
                content = result.get("content", {})
                if isinstance(content, dict):
                    self.default_settings = content
                    return content
                self.set_error("client_response_invalid", "Defaults content was not an object", res.status_code)
            elif result is None:
                self.set_error("client_response_invalid", "Defaults response was not valid JSON", res.status_code)
            else:
                self._set_response_failure(result, "client_server_unavailable", res.status_code)
            logger.warning("MTTS: Get defaults failed: {}".format(result))
            return {}

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("MTTS: Get defaults request encountered an error: {}".format(error_msg))
            self.set_error("client_network_error", u"{}".format(e))
            return {}

    @property
    def provider_id(self):
        return self.provider_manager.get_provider_id()

    @provider_id.setter
    def provider_id(self, value):
        self.provider_manager.set_provider_id(value)
    
    def accessable(self):
        if self._ignore_accessable:
            self.__accessable = True
            self.clear_error()
            return True

        self.__accessable = False
        self.clear_error()
        
        try:
            if not self.provider_manager.get_provider():
                if self.provider_id != 9999:
                    provider_error = self.provider_manager.last_error or {}
                    status, message = self._normalize_failure(provider_error, "client_provider_unavailable")
                    self.set_error(status, message, provider_error.get("code"), self.MttsStatus.FAILED_GET_NODE)
                    return False
            self.baseurl = self.provider_manager.get_tts_url()
        except Exception as e:
            logger.error("accessable(): MTTS get Service Provider Error: {}".format(e))
            if self.provider_id != 9999:
                self.set_error("client_provider_unavailable", u"{}".format(e), fallback=self.MttsStatus.FAILED_GET_NODE)
                return False


        try:
            response = requests.get(self.get_api_url("accessibility"), timeout=self.HTTP_TIMEOUT)
            logger.debug("accessable(): try get accessibility from {}".format(self.get_api_url("accessibility")))
        except Exception as e:
            self.set_error("client_network_error", u"{}".format(e))
            logger.error("accessable(): accessibility request failed: {}".format(e))
            return False

        data = self._response_json(response)
        if data is None:
            self.set_error("client_response_invalid", "Accessibility response was not valid JSON", response.status_code)
            return False
        if response.status_code != 200 or not data.get(u"success", False):
            self._set_response_failure(
                data,
                "client_server_unavailable",
                response.status_code,
                self.MttsStatus.SERVER_MAINTAIN,
            )
            logger.error("accessable(): server is not serving: {}".format(data))
            return False

        self._serving_status = data.get("content")
        if self._serving_status != "serving":
            self.set_error(
                "client_server_unavailable",
                u"Server status: {}".format(self._serving_status),
                response.status_code,
                self.MttsStatus.SERVER_MAINTAIN,
            )
            logger.error("accessable(): server is not serving: {}".format(self._serving_status))
            return False

        self.__accessable = True
        self.clear_error()

        if self.__accessable:
            self.get_defaults()
        return self.__accessable
    
    @property
    def is_accessable(self):
        return self.__accessable
import threading

class MTTSAsyncTask(object):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self.result = None
        self.exception = None
        self.traceback = None
        self.is_finished = False
        self.is_success = False
        self._done_event = threading.Event()
        self._callbacks = []
        self._callback_lock = threading.RLock()
        
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
            logger.error("MTTSAsyncTask failed with exception: %s", e)
            logger.debug("Traceback: %s", self.traceback)
        finally:
            self.is_finished = True
            self._run_done_callbacks()
            self._done_event.set()

    def add_done_callback(self, callback):
        should_call_now = False
        self._callback_lock.acquire()
        try:
            if self.is_finished:
                should_call_now = True
            else:
                self._callbacks.append(callback)
        finally:
            self._callback_lock.release()

        if should_call_now:
            self._call_done_callback(callback)

    def _run_done_callbacks(self):
        self._callback_lock.acquire()
        try:
            callbacks = self._callbacks
            self._callbacks = []
        finally:
            self._callback_lock.release()

        for callback in callbacks:
            self._call_done_callback(callback)

    def _call_done_callback(self, callback):
        try:
            callback(self)
        except Exception as e:
            logger.error("MTTSAsyncTask done callback failed with exception: %s", e)

    @property
    def is_alive(self):
        return self._thread.is_alive()

    def wait(self, timeout=None):
        """等待任务完成（可选超时时间）"""
        self._done_event.wait(timeout)
