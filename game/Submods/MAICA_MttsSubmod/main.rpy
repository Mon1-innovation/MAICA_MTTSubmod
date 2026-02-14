init -1500 python:
    if not config.language:
        config.language = "english"

init -990 python:
    mtts_defaultsettings = {
        "enabled": False,
        "_chat_installed": False,
        "volume": 1.0,
        "acs_enabled": True,
        "_outdated": False,
        "ministathud": True,
        "provider_id": 1 if renpy.windows else 2,
        "drift_statshud_l": False,
        "drift_statshud_r": False,
        "use_custom_model_config": False,
        "replace_playername": False,
        "playername_replacement": "",
    }
    if persistent.mtts is None:
        persistent.mtts = mtts_defaultsettings
    import copy
    setting = copy.deepcopy(mtts_defaultsettings)
    setting.update(persistent.mtts)
    persistent.mtts = setting

    # Initialize MTTS advanced settings
    if not persistent.mtts_advanced_setting:
        persistent.mtts_advanced_setting = {}
    mtts_default_advanced_setting = {
        "parallel_infer": False,
        "repetition_penalty": 0.5,
        "seed": 0,
        "speed_factor": 1.0,
        "temperature": 0.8,
        "text_split_method": "cut2",
        "top_k": 15,
        "top_p": 0.9,
    }
    _conf = copy.deepcopy(mtts_default_advanced_setting)
    _conf.update(persistent.mtts_advanced_setting)
    persistent.mtts_advanced_setting = _conf

    if persistent.mtts_advanced_setting_status is None or not isinstance(persistent.mtts_advanced_setting_status, dict):
        persistent.mtts_advanced_setting_status = {}
    for k in persistent.mtts_advanced_setting:
        if k not in persistent.mtts_advanced_setting_status:
            persistent.mtts_advanced_setting_status[k] = False

    # Initialize backup dictionaries for advanced settings
    if persistent.mtts_advanced_setting_backup is None or not isinstance(persistent.mtts_advanced_setting_backup, dict):
        persistent.mtts_advanced_setting_backup = {}

    if persistent.mtts_advanced_setting_status_backup is None or not isinstance(persistent.mtts_advanced_setting_status_backup, dict):
        persistent.mtts_advanced_setting_status_backup = {}


init -100 python in mtts:
    import mtts_package, store, os
    from mtts_provider_manager import MTTSProviderManager

    from logger_manager import get_logger_manager
    _logger_manager = get_logger_manager()
    _logger_manager.set_logger(store.mas_submod_utils.submod_log)

    _logger_manager.register_injected_reference("mtts_package.logger", mtts_package, "logger")

    import mtts_provider_manager
    _logger_manager.register_injected_reference("mtts_provider_manager.logger", mtts_provider_manager, "logger")

    basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MttsSubmod"))
    store.mas_registerAPIKey("Maica_Token", "Maica Token")
    _current_label = ""
    provider_id = store.persistent.mtts.get("provider_id", 1 if renpy.windows else 2)
    provider_manager = MTTSProviderManager(provider_id)
    try:
        provider_manager.get_provider()
    except Exception:
        pass
    # store.mas_registerAPIKey("MTTS_endpoint", _("MTTS 服务器 (修改需要重启)"))
    # if not store.mas_hasAPIKey("MTTS_endpoint"):
    #     store.mas_api_keys.api_keys.update({"MTTS_endpoint":"https://maicadev.monika.love/tts/"})
    mtts_instance = mtts_package.MTTS(
        # url = store.mas_getAPIKey("MTTS_endpoint"),
        url = provider_manager.get_tts_url(),
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    mtts_instance.user_acc = u""
    matcher = mtts_package.RuleMatcher(os.path.join(basedir, "cache_rules.json"))
    AsyncTask = mtts_package.AsyncTask
    def sync_provider_id(pid):
        """Switch provider node immediately (updates baseurl + reruns accessibility check)."""
        try:
            pid = int(pid)
        except Exception:
            pid = 0
        store.persistent.mtts["provider_id"] = pid
        # Keep MAICA_CHAT setting in sync if installed
        try:
            if store.persistent.mtts.get("_chat_installed", False) and hasattr(store.persistent, "maica_setting_dict") and isinstance(store.persistent.maica_setting_dict, dict):
                store.persistent.maica_setting_dict["provider_id"] = pid
        except Exception:
            pass
        provider_manager.set_provider_id(pid)
        mtts_instance.baseurl = provider_manager.get_tts_url()
        mtts_instance.provider_id = pid
        # restart accessibility async task
        global _acc
        try:
            _acc = AsyncTask(mtts_instance.accessable)
        except Exception:
            _acc = None
        try:
            renpy.notify(_("MTTS: 已切换节点, 正在重新检测可用性"))
        except Exception:
            pass
    mtts_package.logger = store.mas_submod_utils.submod_log


    
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def mtts_check_outdated():
        version = mtts_instance.get_version()
        if version.get("success"):
            min_version = version['content']['fe_synbrace_version']
            if store.mas_utils.compareVersionLists(mtts_version.strip().split('.'), min_version.strip().split('.')) < 0:
                persistent.mtts["_outdated"] = True
        else:
            store.mas_submod_utils.submod_log.error("Failed to check MaicaTTS version.")

        if _acc is not None:
            _acc.wait()
            if _acc.is_finished:
                if _acc.exception:
                    store.mas_submod_utils.submod_log.error("Failed to access MaicaTTS server: {}".format(_acc.exception))
        else:
            store.mas_submod_utils.submod_log.warning("")

    def validate_version():
        # if not (config.debug or config.developer or store.maica.maica_instance._ignore_accessable):
        libv_path = os.path.normpath(os.path.join(renpy.config.basedir, "game", "python-packages", "mtts_release_version"))
        if not os.path.exists(libv_path):
            return None, None, None
        else:
            with open(libv_path, 'r') as libv_file:
                libv = libv_file.read()
        uiv = store.mtts_version
        return store.mas_utils.compareVersionLists(libv.strip().split('.'), uiv.strip().split('.')), libv, uiv

    def progress_bar(percentage, current=None, total=None, bar_length=20, unit=None):
        # Calculate the number of filled positions in the progress bar
        filled_length = int(round(bar_length * percentage / 100.0))
        
        # Generate the progress bar string
        bar = '▇' * filled_length + '▁' * (bar_length - filled_length)
        
        # Format the output string based on the presence of total
        if total is not None:
            if not current:
                current = total * percentage / 100.0
            if unit:
                return '|{}| {}% | {}{} / {}{}'.format(bar, int(percentage), int(current), unit, total, unit)
            else:
                return '|{}| {}% | {} / {}'.format(bar, int(percentage), int(current), total)
        elif current is not None:
            if unit:
                return '|{}| {}% | {}{}'.format(bar, int(percentage), current, unit)
            else:
                return '|{}| {}% | {}'.format(bar, int(percentage), current)
        else:
            return '|{}| {}%'.format(bar, int(percentage))

init 10 python in mtts:
    import store
    def apply_settings():
        store.mtts.mtts_instance.enabled = store.persistent.mtts["enabled"]
        store.mtts.mtts_instance.volume = store.persistent.mtts["volume"]
        store.mtts.mtts_instance.acs_enabled = store.persistent.mtts["acs_enabled"]
        store.mtts.mtts_instance.ministathud = store.persistent.mtts["ministathud"]
        store.mtts.mtts_instance.provider_id = store.persistent.mtts["provider_id"]
        store.mtts.mtts_instance.drift_statshud_l = store.persistent.mtts["drift_statshud_l"]
        store.mtts.mtts_instance.drift_statshud_r = store.persistent.mtts["drift_statshud_r"]
        
    def discard_settings():
        store.persistent.mtts["enabled"] = store.mtts.mtts_instance.enabled
        store.persistent.mtts["volume"] = store.mtts.mtts_instance.volume
        store.persistent.mtts["acs_enabled"] = store.mtts.mtts_instance.acs_enabled
        store.persistent.mtts["ministathud"] = store.mtts.mtts_instance.ministathud
        store.persistent.mtts["provider_id"] = store.mtts.mtts_instance.provider_manager._provider_id
        store.persistent.mtts["drift_statshud_l"] = store.mtts.mtts_instance.drift_statshud_l
        store.persistent.mtts["drift_statshud_r"] = store.mtts.mtts_instance.drift_statshud_r
        

    def reset_settings():
        store.persistent.mtts = store.setting.copy()

init -100 python:
    import json_exporter_mtts
    def get_emote_mood(emote, emotion_selector = json_exporter_mtts.emotion_selector):  # 获取情绪
        try:
            for mood, keywords in emotion_selector.items():  # 遍历情绪和关键词字典
                for key in keywords:  # 遍历当前情绪的所有关键词
                    if emote in key:  # 检查关键词是否存在于输入字符串
                        return mood
        except Exception as e:
            pass
        return "微笑"  # 无匹配时返回 None
init python in mtts:
    _acc = AsyncTask(mtts_instance.accessable)
init python:
    persistent.mtts["_chat_installed"] = store.mas_submod_utils.isSubmodInstalled("MAICA Blessland")
    old_renpysay = renpy.say
    import mtts_package
    PY2, PY3 = mtts_package.PY2, mtts_package.PY3

    def hijack_build_gift_react_labels(function):
        def wrapper(
            evb_details=[],
            gsp_details=[],
            gen_details=[],
            gift_cntrs=None,
            ending_label=None,
            starting_label=None,
            prepare_data=True
        ):
            labels = function(evb_details, gsp_details, gen_details, gift_cntrs, ending_label, starting_label, prepare_data)
            if not mas_seenEvent("mas_reaction_gift_mttsheadset") and "mas_reaction_gift_mttsheadset" in labels:
                index = labels.index("mas_reaction_gift_mttsheadset")
                mtts_is_first = index == int(bool(starting_label))
                mtts_is_last = index == len(labels) - 1 - int(bool(ending_label))
                if mtts_is_first and mtts_is_last:
                    labels = ["mas_reaction_gift_mttsheadset"]
                    if ending_label:
                        labels.append("mas_reaction_end")
                else:
                    if not mtts_is_last and gift_cntrs:
                        labels.pop(index + 1)
                    # labels.pop(index)
                    if not mtts_is_first and gift_cntrs:
                        labels.pop(index - 1)
            return labels
        return wrapper

    store.mas_filereacts.build_gift_react_labels = hijack_build_gift_react_labels(store.mas_filereacts.build_gift_react_labels)

    class MttsSay(object):

        def __init__(self):
            self._history = mtts_package.LimitedList(3)

        @property
        def conditions(self):
            _acc = store.mtts._acc
            if _acc is not None:
                _acc.wait()
            if not renpy.seen_label("mtts_greeting_end"):
                store.mtts_status = renpy.substitute(_("未解锁"))
                return False
            elif not persistent.mtts["enabled"]:
                store.mtts_status = renpy.substitute(_("未启用"))
                return False
            elif persistent.mtts["_outdated"]:
                store.mtts_status = renpy.substitute(_("版本过旧"))
                return False
            elif not store.mtts.mtts_instance.is_accessable:
                store.mtts_status = renpy.substitute(_("无连接"))
                return False
            else:
                return True

        def is_duplicated(self, what):
            for sentence in self._history:
                if sentence in what and not sentence == what:
                    return True
            return False

        def remove_duplicated(self, what):
            for sentence in self._history:
                if sentence in what and not sentence == what:
                    what = what.replace(sentence, '', 1)
            what = what.strip()
            return what

        @staticmethod
        def decode_str(text):
            import sys
            from cp936_decode import decode_cp936
            # 1. 统一转换为 Unicode 字符串
            decoded_text = text

            # 判断是否为字节流 (兼容 Python 2/3)
            is_bytes = (
                (sys.version_info[0] == 3 and isinstance(text, bytes))
                or
                (sys.version_info[0] == 2 and isinstance(text, str))
            )

            if is_bytes and len(text) > 0:

                # 使用 chardet 检测编码
                detection = chardet.detect(text)
                encoding = detection.get('encoding')
                confidence = detection.get('confidence', 0)

                if encoding.lower() in ('utf8', 'utf-8'):
                    decoded_text = text.decode('utf-8', errors='strict')
                else:
                    store.mas_submod_utils.submod_log.warning("Encoding not utf-8 detected: %s, trying GBK", encoding)
                    decoded_text = decode_cp936(text)

            elif sys.version_info[0] == 2 and not isinstance(text, unicode):
                # 兼容处理 Py2 某些奇怪的对象类型
                decoded_text = unicode(text)

            return decoded_text

        @staticmethod
        def escape_brackets_in_exceptions_and_ellipsis(err, max_chars=120):
            #输入转可显示文本 + 转义Exception里的中括号 (如requests)
            try:
                if isinstance(err, basestring):
                    s = err
                else:
                    s = unicode(err)
            except Exception:
                s = u"{}".format(err)

            if max_chars and len(s) > max_chars:
                s = s[:max_chars-1] + u"\u2026" # \u2026: 省略号字符: …

            s = s.replace(u"[", u"[[")
            s = s.replace(u"]", u"]]")
            return s

        @staticmethod
        def determ_lang(input, suppose='zh'):
            # If the input is of correct lang
            if PY2:
                import datapy2_mtts
                pattern_content_zh = datapy2_mtts.pattern_content_zh
                # pattern_content_en = datapy2.pattern_content_en
            else:
                pattern_content_zh = re.compile(r'[一-龥]')
                # pattern_content_en = re.compile(r'[A-Za-z]')

            input_len = len(input)
            zh_search = pattern_content_zh.search(input)
            # zh_len = len(pattern_content_zh.findall(input))
            if suppose == 'zh':
                # zh_rate = zh_len / input_len
                if input_len >= 5 and not zh_search:
                    return 'en'
                else:
                    return 'zh'
            else:
                if zh_search:
                    return 'zh'
                else:
                    return 'en'

        def __call__(self, who, what, interact=True, *args, **kwargs):
            if (
                not self.conditions
                # or self.is_duplicated(what)
            ):
                return old_renpysay(who, what, interact, *args, **kwargs)
            
            if who != store.m:
                return old_renpysay(who, what, interact, *args, **kwargs)

            original_text = renpy.substitute(what)
            decoded_text = self.decode_str(original_text)
            replaced_text = store.mtts.matcher.apply_replace_rules(decoded_text, store=store)
            unduplicated_text = self.remove_duplicated(replaced_text)
            text = unduplicated_text


            # 调试日志：记录文本替换过程
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Original text: {0}".format(repr(original_text)))
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Decoded text: {0}".format(repr(decoded_text)))
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] After replace rules: {0}".format(repr(replaced_text)))
            # store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] After process_str: {0}".format(repr(clean_text)))
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] After unduplication: {0}".format(repr(unduplicated_text)))

            if store.mas_submod_utils.current_label[0] != '_':
                store.mtts._current_label = store.mas_submod_utils.current_label
            rule = store.mtts.matcher.match_cache_rule(text, store.mtts._current_label, store=store)

            # 添加字符计数调试日志
            content_char_count = store.mtts.matcher._count_content_chars(text)
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Content char count: {0}".format(content_char_count))
            store.mtts_match_rule = rule.get('name', 'Default')
            
            # 添加匹配规则调试日志
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Matched rule: {0}".format(store.mtts_match_rule))
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Rule action: {0}".format(rule.get('action', [])))

            if not rule['action']:
                store.mtts_status = renpy.substitute(_("规则为空"))
                return old_renpysay(who, what, interact, *args, **kwargs)
            
            replacement_str = persistent.mtts.get("playername_replacement", "")
            if persistent.mtts.get("replace_playername") and player in text:
                text = text.replace(player, replacement_str)
                store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Replaced player name with: {0}".format(replacement_str))


            if rule['name'] == 'MAICA_Chat':
                target_lang = store.maica.maica_instance.target_lang
            else:
                target_lang = "zh" if config.language == 'chinese' else 'en'

            target_lang = self.determ_lang(text, suppose=target_lang)

            store.mtts_status = renpy.substitute(_("生成中"))
            exp = store.get_emote_mood(store.mas_getCurrentMoniExp())

            mtts.mtts_instance.local_cache = 'local' in rule['action']
            mtts.mtts_instance.remote_cache = 'remote' in rule['action']

            task = mtts.AsyncTask(
                mtts.mtts_instance.generate, 
                text=text, 
                label_name=store.mtts._current_label, 
                emotion=exp, 
                target_lang=target_lang, 
                kwargs=persistent.mtts_advance_params if persistent.mtts.get('use_custom_model_config', False) else {}
            )
            name = mtts.mtts_instance.cache.get_cachename(text = text, label_name=store.mtts._current_label)

            while not task.is_finished:
                old_renpysay(who, "...{w=0.3}{nw}", interact, *args, **kwargs)
                _history_list.pop()

            if task.is_success:
                res = task.result
                if res.is_success():
                    store.mtts_status = renpy.substitute(_("播放中"))
                    renpy.music.set_volume(persistent.mtts["volume"], channel="voice")
                    renpy.music.play(
                        store.MASAudioData(res.data, name),#os.path.join(mtts.mtts.cache_path, "test.ogg"),
                        channel="voice",
                    )
                else:
                    # renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + "{}".format(res.reason() if getattr(res, 'reason', None) else 'Unknown'))
                    error_msg = res.reason() if getattr(res, 'reason', None) else 'Unknown'
                    renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + self.escape_brackets_in_exceptions_and_ellipsis(error_msg))
                    # 添加详细日志：输出错误内容和输入文本
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Input text: {0}".format(repr(text)))
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Error reason: {0}".format(repr(error_msg)))
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Label: {0}".format(store.mtts._current_label))
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Target language: {0}".format(target_lang))
            else:
                # renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + "{}".format(task.exception))
                exception_msg = str(task.exception)
                renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + self.escape_brackets_in_exceptions_and_ellipsis(exception_msg))
                # 添加详细日志：输出错误内容和输入文本
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Input text: {0}".format(repr(text)))
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Exception: {0}".format(repr(exception_msg)))
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Label: {0}".format(store.mtts._current_label))
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Target language: {0}".format(target_lang))

            store.mtts_status = renpy.substitute(_("待机"))

            self._history.append(text)
            old_renpysay(who, what, interact, *args, **kwargs)

    def mtts_refresh_status_once():
        # 一次性刷新，开关手动调用
        if not renpy.seen_label("mtts_greeting_end"):
            store.mtts_status = renpy.substitute(_("未解锁"))
            return

        if not persistent.mtts.get("enabled", False):
            store.mtts_status = renpy.substitute(_("未启用"))
            return

        if persistent.mtts.get("_outdated", False):
            store.mtts_status = renpy.substitute(_("版本过旧"))
            return

        ok = store.mtts.mtts_instance.is_accessable
        store.mtts_status = renpy.substitute(_("待机")) if ok else renpy.substitute(_("无连接"))

    mtts_say = MttsSay()
    renpy.say = mtts_say
