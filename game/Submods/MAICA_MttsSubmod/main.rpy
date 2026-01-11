init -990 python:
    mtts_defaultsettings = {
        "enabled": False,
        "_chat_installed": False,
        "volume": 1.0,
        "acs_enabled": True,
        "_outdated": False,
        "ministathud": True,
        "provider_id": 1 if renpy.windows else 2
    }
    if persistent.mtts is None:
        persistent.mtts = mtts_defaultsettings
    import copy
    setting = copy.deepcopy(mtts_defaultsettings)
    setting.update(persistent.mtts)
    persistent.mtts = setting
init -100 python in mtts:
    import MTTS, store, os
    from mtts_provider_manager import MTTSProviderManager
    MTTS.logger = store.mas_submod_utils.submod_log
    basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MttsSubmod"))
    store.mas_registerAPIKey("Maica_Token", "Maica Token")

    provider_id = store.persistent.mtts.get("provider_id", 1 if renpy.windows else 2)
    provider_manager = MTTSProviderManager(provider_id)
    try:
        provider_manager.get_provider()
    except Exception:
        pass
    # store.mas_registerAPIKey("MTTS_endpoint", _("MTTS 服务器 (修改需要重启)"))
    # if not store.mas_hasAPIKey("MTTS_endpoint"):
    #     store.mas_api_keys.api_keys.update({"MTTS_endpoint":"https://maicadev.monika.love/tts/"})
    mtts = MTTS.MTTS(
        # url = store.mas_getAPIKey("MTTS_endpoint"),
        url = provider_manager.get_tts_url(),
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    mtts.user_acc = u""
    matcher = MTTS.RuleMatcher(os.path.join(basedir, "cache_rules.json"))
    AsyncTask = MTTS.AsyncTask
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
        mtts.baseurl = provider_manager.get_tts_url()
        mtts.provider_id = pid
        # restart accessibility async task
        global _acc
        try:
            _acc = AsyncTask(mtts.accessable)
        except Exception:
            _acc = None
        try:
            renpy.notify(_("MTTS: 已切换节点, 正在重新检测可用性"))
        except Exception:
            pass
    MTTS.logger = store.mas_submod_utils.submod_log
    

    
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def mtts_check_outdated():
        version = mtts.get_version()
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
        store.mtts.mtts.enabled = store.persistent.mtts["enabled"]
        store.mtts.mtts.volume = store.persistent.mtts["volume"]
        store.mtts.mtts.acs_enabled = store.persistent.mtts["acs_enabled"]
        store.mtts.mtts.ministathud = store.persistent.mtts["ministathud"]
        store.mtts.mtts.provider_id = store.persistent.mtts["provider_id"]
        
    def discard_settings():
        store.persistent.mtts["enabled"] = store.mtts.mtts.enabled
        store.persistent.mtts["volume"] = store.mtts.mtts.volume
        store.persistent.mtts["acs_enabled"] = store.mtts.mtts.acs_enabled
        store.persistent.mtts["ministathud"] = store.mtts.mtts.ministathud
        store.persistent.mtts["provider_id"] = store.mtts.mtts.provider_id
        

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
    _acc = AsyncTask(mtts.accessable)
init python:
    persistent.mtts["_chat_installed"] = store.mas_submod_utils.isSubmodInstalled("MAICA Blessland")
    import MTTS
    old_renpysay = renpy.say
    store.mtts = mtts
    PY2, PY3 = MTTS.PY2, MTTS.PY3

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
            self._history = MTTS.LimitedList(3)

        @property
        def conditions(self):
            _acc = store.mtts._acc
            if _acc is not None:
                _acc.wait()
            if not renpy.seen_label("mtts_greeting"):
                store.mtts_status = renpy.substitute(_("未解锁"))
                return False
            elif not persistent.mtts["enabled"]:
                store.mtts_status = renpy.substitute(_("未启用"))
                return False
            elif persistent.mtts["_outdated"]:
                store.mtts_status = renpy.substitute(_("版本过旧"))
                return False
            elif not store.mtts.mtts.is_accessable:
                store.mtts_status = renpy.substitute(_("无连接"))
                return False
            else:
                return True

        def is_duplicated(self, what):
            for sentence in self._history:
                if sentence in what and not sentence == what:
                    return True
            return False

        @staticmethod
        def process_str(srt):
            import re
            # \{fast\}.*?\{fast\} , \{.*?\} 将匹配的str替换为空字符串
            srt = re.sub(r"\{fast\}.*?\{fast\}", "", srt)
            srt = re.sub(r"\{.*?\}", "", srt)
            return srt

        def __call__(self, who, what, interact=True, *args, **kwargs):
            if (
                not self.conditions
                or self.is_duplicated(what)
            ):
                return old_renpysay(who, what, interact, *args, **kwargs)
            
            if who != store.m:
                return old_renpysay(who, what, interact, *args, **kwargs)
            text = self.process_str(store.mtts.matcher.apply_replace_rules(renpy.substitute(what)))
            rule = store.mtts.matcher.match_cache_rule(what, store.mas_submod_utils.current_label)
            store.mtts_match_rule = rule.get('name', 'Default')

            if not rule['action']:
                store.mtts_status = renpy.substitute(_("规则为空"))
                return old_renpysay(who, what, interact, *args, **kwargs)

            if rule['name'] == 'MAICA_Chat':
                target_lang = store.maica.maica.target_lang
            else:
                target_lang = "zh" if config.language == 'chinese' else 'en'

            store.mtts_status = renpy.substitute(_("生成中"))
            exp = store.get_emote_mood(store.mas_getCurrentMoniExp())

            mtts.mtts.local_cache = 'local' in rule['action']
            mtts.mtts.remote_cache = 'remote' in rule['action']

            task = mtts.AsyncTask(mtts.mtts.generate, text=text, label_name=store.mas_submod_utils.current_label, emotion=exp, target_lang=target_lang)
            name = mtts.mtts.cache.get_cachename(text = text, label_name=store.mas_submod_utils.current_label)

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
                    renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + "{}".format(res.reason() if getattr(res, 'reason', None) else 'Unknown'))
            else:
                renpy.notify(renpy.substitute(_("MTTS: 语音生成失败 -- ")) + "{}".format(task.exception))

            store.mtts_status = renpy.substitute(_("待机"))

            self._history.append(what)
            old_renpysay(who, what, interact, *args, **kwargs)

    def mtts_refresh_status_once():
        # 一次性刷新，开关手动调用
        if not renpy.seen_label("mtts_greeting"):
            store.mtts_status = renpy.substitute(_("未解锁"))
            return

        if not persistent.mtts.get("enabled", False):
            store.mtts_status = renpy.substitute(_("未启用"))
            return

        if persistent.mtts.get("_outdated", False):
            store.mtts_status = renpy.substitute(_("版本过旧"))
            return

        ok = store.mtts.mtts.is_accessable
        store.mtts_status = renpy.substitute(_("待机")) if ok else renpy.substitute(_("无连接"))

    mtts_say = MttsSay()
    renpy.say = mtts_say
