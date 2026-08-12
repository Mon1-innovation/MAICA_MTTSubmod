define MTTS_SPINNER_CYCLE_SECONDS = 1.2
define MTTS_SPINNER_DISPLAY_SIZE = 20

init -1500 python:
    def mtts_build_spinner_animation():
        source = "mod_assets/mtts_img/mtts_spinner_strip.png"
        frame_width = 260
        frame_height = 320
        frame_count = 12
        frame_delay = MTTS_SPINNER_CYCLE_SECONDS / float(frame_count)
        args = []

        for index in range(frame_count):
            frame = im.Crop(source, index * frame_width, 0, frame_width, frame_height)
            args.append(im.Scale(frame, MTTS_SPINNER_DISPLAY_SIZE, MTTS_SPINNER_DISPLAY_SIZE))
            args.append(frame_delay)

        return renpy.display.layout.Position(
            renpy.display.anim.Animation(*args),
            yanchor=0.5,
            ypos=0.5
        )

image mtts_spinner = mtts_build_spinner_animation()

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
        "generate_timeout": 15,
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
    mtts_instance.provider_manager = provider_manager
    mtts_instance.user_acc = u""
    mtts_instance.generate_timeout = store.persistent.mtts.get("generate_timeout", 15)
    matcher = mtts_package.RuleMatcher(os.path.join(basedir, "cache_rules.json"))
    MTTSAsyncTask = mtts_package.MTTSAsyncTask
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
            _acc = MTTSAsyncTask(mtts_instance.accessable)
        except Exception:
            _acc = None
        try:
            renpy.notify(_("MTTS: Provider applied, reinitializing"))
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

        if not version.get("success") and mtts_instance.is_accessable and not mtts_instance.has_error():
            mtts_instance.set_error(
                version.get("status") or "client_server_unavailable",
                version.get("exception"),
                version.get("code"),
            )
            store.mtts_status = store.mtts_failure_status_text()

    _cached_version_result = None

    def validate_version():
        global _cached_version_result
        if _cached_version_result is not None:
            return _cached_version_result
        # if not (config.debug or config.developer or store.maica.maica_instance._ignore_accessable):
        libv_path = os.path.normpath(os.path.join(renpy.config.basedir, "game", "python-packages", "mtts_release_version"))
        if not os.path.exists(libv_path):
            _cached_version_result = (None, None, None)
        else:
            with open(libv_path, 'r') as libv_file:
                libv = libv_file.read()
            uiv = store.mtts_version
            _cached_version_result = (store.mas_utils.compareVersionLists(libv.strip().split('.'), uiv.strip().split('.')), libv, uiv)
        return _cached_version_result

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
        store.mtts.mtts_instance.generate_timeout = store.persistent.mtts["generate_timeout"]
        
    def discard_settings():
        store.persistent.mtts["enabled"] = store.mtts.mtts_instance.enabled
        store.persistent.mtts["volume"] = store.mtts.mtts_instance.volume
        store.persistent.mtts["acs_enabled"] = store.mtts.mtts_instance.acs_enabled
        store.persistent.mtts["ministathud"] = store.mtts.mtts_instance.ministathud
        store.persistent.mtts["provider_id"] = store.mtts.mtts_instance.provider_manager._provider_id
        store.persistent.mtts["drift_statshud_l"] = store.mtts.mtts_instance.drift_statshud_l
        store.persistent.mtts["drift_statshud_r"] = store.mtts.mtts_instance.drift_statshud_r
        store.persistent.mtts["generate_timeout"] = store.mtts.mtts_instance.generate_timeout
        

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
    _acc = MTTSAsyncTask(mtts_instance.accessable)
init python:
    persistent.mtts["_chat_installed"] = store.mas_submod_utils.isSubmodInstalled("MAICA Blessland")
    old_renpysay = renpy.exports.say
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
            self._extend_tracker = mtts_package.ExtendTextTracker()
            self._last_raw_text = None
            self._generation_wait_id = 0
            self._active_generation_wait_id = None

        def begin_extend(self, what):
            self._extend_tracker.begin_extend(what)

        @staticmethod
        def call_old_say(who, what, interact, args, kwargs):
            kw = dict(kwargs)
            kw["interact"] = interact
            return old_renpysay(who, what, *args, **kw)

        def build_generation_wait_text(self, is_extend, wait_seconds):
            spinner = u" {image=mtts_spinner}{fast}{w=%s}{nw}" % wait_seconds
            if is_extend and self._last_raw_text:
                return self._last_raw_text + spinner
            return spinner

        def begin_generation_wait_afm_scope(self):
            try:
                prefs = renpy.game.preferences
                should_restore = (
                    getattr(prefs, "using_afm_enable", False)
                    and getattr(prefs, "afm_enable", False)
                    and not getattr(prefs, "afm_after_click", False)
                )
                if should_restore:
                    prefs.afm_after_click = True
                return should_restore
            except Exception as e:
                store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Failed entering AFM wait scope: {0}".format(e))
                return False

        def end_generation_wait_afm_scope(self, should_restore):
            if not should_restore:
                return

            try:
                prefs = renpy.game.preferences
                prefs.afm_after_click = False
                if getattr(prefs, "using_afm_enable", False):
                    prefs.afm_enable = True
                    renpy.restart_interaction()
            except Exception as e:
                store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Failed leaving AFM wait scope: {0}".format(e))

        def should_wait_for_voice_before_extend(self, what, is_extend, interact):
            if is_extend or not interact or "{nw}" not in what:
                return False

            try:
                prefs = renpy.game.preferences
                return (
                    getattr(prefs, "using_afm_enable", False)
                    and getattr(prefs, "afm_enable", False)
                    and getattr(prefs, "afm_time", 0)
                )
            except Exception as e:
                store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Failed checking AFM extend wait state: {0}".format(e))
                return False

        @staticmethod
        def strip_no_wait_tags(what):
            return what.replace("{nw}", "")

        @property
        def conditions(self):
            _acc = store.mtts._acc
            if _acc is not None:
                _acc.wait()
            if not renpy.seen_label("mtts_greeting_end"):
                store.mtts_status = renpy.substitute(_("Not revealed"))
                return False
            elif not persistent.mtts["enabled"]:
                store.mtts_status = renpy.substitute(_("Not enabled"))
                return False
            elif persistent.mtts["_outdated"]:
                store.mtts_status = renpy.substitute(_("Outdated"))
                return False
            elif not store.mtts.mtts_instance.is_accessable:
                store.mtts_status = mtts_failure_status_text()
                return False
            else:
                if store.mtts.mtts_instance.has_error():
                    store.mtts_status = mtts_failure_status_text()
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
            ):
                return self.call_old_say(who, what, interact, args, kwargs)
            
            if who != store.m:
                self._extend_tracker.pending_raw = None
                return self.call_old_say(who, what, interact, args, kwargs)

            is_extend, raw_tts_text = self._extend_tracker.resolve(
                what,
                self._last_raw_text,
                getattr(config, "extend_interjection", "{fast}")
            )
            original_text = renpy.substitute(raw_tts_text)
            decoded_text = self.decode_str(original_text)
            replaced_text = store.mtts.matcher.apply_replace_rules(decoded_text, store=store)
            unduplicated_text = self.remove_duplicated(replaced_text)
            text = unduplicated_text


            # 调试日志：记录文本替换过程
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Original text: {0}".format(repr(original_text)))
            store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Is extend: {0}".format(is_extend))
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
                store.mtts_status = renpy.substitute(_("Blank rule"))
                self._last_raw_text = what
                return self.call_old_say(who, what, interact, args, kwargs)
            
            replacement_str = persistent.mtts.get("playername_replacement", "")
            if persistent.mtts.get("replace_playername") and player in text:
                text = text.replace(player, replacement_str)
                store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Replaced player name with: {0}".format(replacement_str))


            if rule['name'] == 'MAICA_Chat' and mtts_has_maica_instance():
                target_lang = store.maica.maica_instance.target_lang
            else:
                target_lang = "zh" if config.language == 'chinese' else 'en'

            target_lang = self.determ_lang(text, suppose=target_lang)

            store.mtts_status = renpy.substitute(_("Generating"))
            exp = store.get_emote_mood(store.mas_getCurrentMoniExp())

            mtts.mtts_instance.local_cache = 'local' in rule['action']
            mtts.mtts_instance.remote_cache = 'remote' in rule['action']

            task = mtts.MTTSAsyncTask(
                mtts.mtts_instance.generate, 
                text=text, 
                label_name=store.mtts._current_label, 
                emotion=exp, 
                target_lang=target_lang, 
                kwargs=persistent.mtts_advance_params if persistent.mtts.get('use_custom_model_config', False) else {}
            )
            name = mtts.mtts_instance.cache.get_cachename(text = text, label_name=store.mtts._current_label)

            import time
            generation_timed_out = False
            try:
                generate_timeout = max(1, int(persistent.mtts.get("generate_timeout", 15)))
            except Exception:
                generate_timeout = 15
            wait_started_at = time.time()
            self._generation_wait_id += 1
            generation_wait_id = self._generation_wait_id

            def wake_generation_wait(finished_task):
                if self._generation_wait_id != generation_wait_id:
                    return
                if self._active_generation_wait_id != generation_wait_id:
                    return
                try:
                    renpy.queue_event("dismiss")
                except Exception as e:
                    store.mas_submod_utils.submod_log.debug("[MTTS DEBUG] Failed to wake generation wait: {0}".format(e))

            task.add_done_callback(wake_generation_wait)

            while True:
                if task.is_finished:
                    break
                elapsed = time.time() - wait_started_at
                if elapsed >= generate_timeout:
                    generation_timed_out = True
                    self._generation_wait_id += 1
                    self._active_generation_wait_id = None
                    store.mas_submod_utils.submod_log.info("[MTTS TIMEOUT] Generation wait exceeded {0}s; continuing dialogue silently. Label: {1}".format(generate_timeout, store.mtts._current_label))
                    break
                remaining_wait = max(0.1, generate_timeout - elapsed)
                self._active_generation_wait_id = generation_wait_id
                if task.is_finished:
                    self._active_generation_wait_id = None
                    break
                restore_afm_scope = self.begin_generation_wait_afm_scope()
                try:
                    self.call_old_say(who, self.build_generation_wait_text(is_extend, remaining_wait), interact, args, kwargs)
                finally:
                    self.end_generation_wait_afm_scope(restore_afm_scope)
                self._active_generation_wait_id = None
                _history_list.pop()

            self._active_generation_wait_id = None
            if task.is_finished and self._generation_wait_id == generation_wait_id:
                self._generation_wait_id += 1

            if generation_timed_out:
                mtts.mtts_instance.set_error(
                    "client_response_timeout",
                    "Speech generation timed out after {0} seconds".format(generate_timeout),
                    fallback=mtts.mtts_instance.MttsStatus.CONNECT_PROBLEM,
                )
                store.mtts_status = mtts_failure_status_text()
                renpy.notify(renpy.substitute(_("MTTS: Generation failed -- ")) + store.mtts_status)
            elif task.is_success:
                res = task.result
                if res.is_success():
                    store.mtts_status = renpy.substitute(_("Playing"))
                    renpy.music.set_volume(persistent.mtts["volume"], channel="voice")
                    audio_data = store.MASAudioData(res.data, name)
                    if is_extend:
                        renpy.music.queue(
                            audio_data,
                            channel="voice",
                            clear_queue=False
                        )
                    else:
                        renpy.music.play(
                            audio_data,#os.path.join(mtts.mtts.cache_path, "test.ogg"),
                            channel="voice",
                        )
                else:
                    # renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + "{}".format(res.reason() if getattr(res, 'reason', None) else 'Unknown'))
                    error_msg = res.reason() if getattr(res, 'reason', None) else 'Unknown'
                    renpy.notify(renpy.substitute(_("MTTS: Generation failed -- ")) + self.escape_brackets_in_exceptions_and_ellipsis(error_msg))
                    # 添加详细日志：输出错误内容和输入文本
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Input text: {0}".format(repr(text)))
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Error reason: {0}".format(repr(error_msg)))
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Label: {0}".format(store.mtts._current_label))
                    store.mas_submod_utils.submod_log.info("[MTTS ERROR] Target language: {0}".format(target_lang))
                    if not mtts.mtts_instance.has_error():
                        mtts.mtts_instance.set_error("client_generation_failed", error_msg)
                    store.mtts_status = mtts_failure_status_text()
            else:
                # renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + "{}".format(task.exception))
                exception_msg = str(task.exception)
                renpy.notify(renpy.substitute(_("MTTS: Generation failed -- ")) + self.escape_brackets_in_exceptions_and_ellipsis(exception_msg))
                # 添加详细日志：输出错误内容和输入文本
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Input text: {0}".format(repr(text)))
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Exception: {0}".format(repr(exception_msg)))
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Label: {0}".format(store.mtts._current_label))
                store.mas_submod_utils.submod_log.info("[MTTS EXCEPTION] Target language: {0}".format(target_lang))
                if not mtts.mtts_instance.has_error():
                    mtts.mtts_instance.set_error("client_generation_failed", exception_msg)
                store.mtts_status = mtts_failure_status_text()

            if not generation_timed_out and task.is_success and task.result.is_success():
                store.mtts_status = renpy.substitute(_("Standing by"))

            self._history.append(text)
            self._last_raw_text = what
            display_what = self.strip_no_wait_tags(what) if self.should_wait_for_voice_before_extend(what, is_extend, interact) else what
            self.call_old_say(who, display_what, interact, args, kwargs)

    def mtts_refresh_status_once():
        # 一次性刷新，开关手动调用
        if not renpy.seen_label("mtts_greeting_end"):
            store.mtts_status = renpy.substitute(_("Not revealed"))
            return

        if not persistent.mtts.get("enabled", False):
            store.mtts_status = renpy.substitute(_("Not enabled"))
            return

        if persistent.mtts.get("_outdated", False):
            store.mtts_status = renpy.substitute(_("Outdated"))
            return

        instance = store.mtts.mtts_instance
        if instance.has_error() or not instance.is_accessable:
            store.mtts_status = mtts_failure_status_text()
        else:
            store.mtts_status = renpy.substitute(_("Standing by"))

    mtts_say = MttsSay()
    renpy.say = mtts_say
    renpy.exports.say = mtts_say

    _mtts_original_extend = extend
    def mtts_extend(what, interact=True, *args, **kwargs):
        store.mtts_say.begin_extend(what)
        kw = dict(kwargs)
        kw["interact"] = interact
        return _mtts_original_extend(what, *args, **kw)
    mtts_extend.record_say = False
    extend = mtts_extend
