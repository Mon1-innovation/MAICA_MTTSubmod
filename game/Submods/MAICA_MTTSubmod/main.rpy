init -990 python:
    mtts_defaultsettings = {
        "enabled": False,
        "_chat_installed": False,
        "volume": 1.0,
        "acs_enabled": True,
        "_outdated": False,
        "ministathud": True,
    }
    if persistent.mtts is None:
        persistent.mtts = mtts_defaultsettings
    import copy
    setting = copy.deepcopy(mtts_defaultsettings)
    setting.update(persistent.mtts)
    persistent.mtts = setting
init -100 python in mtts:
    import MTTS, store, os
    basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MTTSubmod"))
    if not store.mas_hasAPIKey("Maica_Token"):
        store.mas_registerAPIKey("Maica_Token", "Maica Token")
    store.mas_registerAPIKey("MTTS_endpoint", _("MTTS 服务器 (修改需要重启)"))
    if not store.mas_hasAPIKey("MTTS_endpoint"):
        store.mas_api_keys.api_keys.update({"MTTS_endpoint":"https://maicadev.monika.love/tts/"})
    mtts = MTTS.MTTS(
        url = store.mas_getAPIKey("MTTS_endpoint"),
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    matcher = MTTS.CacheRuleMatcher(os.path.join(basedir, "cache_rules.json"))
    AsyncTask = MTTS.AsyncTask
    MTTS.logger = store.mas_submod_utils.submod_log
    _acc = AsyncTask(mtts.accessable)

    def apply_settings():
        pass
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def mtts_check_outdated():
        version = mtts.get_version()
        if version.get("success"):
            min_version = version['content']['fe_synbrace_version']
            if store.mas_utils.compareVersionLists(mtts_version.strip().split('.'), min_version.strip().split('.')) < 0:
                persistent.mtts["_outdated"] = True
        else:
            store.mas_submod_utils.submod_log.error("Failed to check MaicaTTS version.")

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
init python:
    persistent.mtts["_chat_installed"] = store.mas_submod_utils.isSubmodInstalled("MAICA Blessland")
init python:
    
    import MTTS
    old_renpysay = renpy.say
    store.mtts = mtts
    PY2, PY3 = MTTS.PY2, MTTS.PY3
    def mtts_say(who, what, interact=True, *args, **kwargs):
        if not renpy.seen_label("mtts_greeting"):
            store.mtts_status = renpy.substitute(_("未解锁"))
            return old_renpysay(who, what, interact, *args, **kwargs)
        if not persistent.mtts["enabled"]:
            store.mtts_status = renpy.substitute(_("未启用"))
            return old_renpysay(who, what, interact, *args, **kwargs)
        if persistent.mtts["_outdated"]:
            store.mtts_status = renpy.substitute(_("版本过旧"))
            return old_renpysay(who, what, interact, *args, **kwargs)
        if not store.mtts.mtts.is_accessable:
            store.mtts_status = renpy.substitute(_("无连接"))
            return old_renpysay(who, what, interact, *args, **kwargs)
        def process_str(srt):
            import re
            # \{fast\}.*?\{fast\} , \{.*?\} 将匹配的str替换为空字符串
            srt = re.sub(r"\{fast\}.*?\{fast\}", "", srt)
            srt = re.sub(r"\{.*?\}", "", srt)
            return srt

        text = process_str(renpy.substitute(what))
        rule = store.mtts.matcher.match_rule(what, store.mas_submod_utils.current_label)
        store.mtts_match_rule = rule.get('name', 'Default')
        if not rule['action']:
            store.mtts_status = renpy.substitute(_("未匹配任何规则/规则为空action"))
            return old_renpysay(who, what, interact, *args, **kwargs)
        if rule['name'] == 'MAICA_Chat':
            target_lang = store.maica.maica.target_lang
        else:
            target_lang = "zh" if config.language == 'chinese' else 'en'
        store.mtts_status = renpy.substitute(_("生成中"))
        exp = store.get_emote_mood(store.mas_getCurrentMoniExp())
        mtts.mtts.local_cache = 'local' in rule['action']
        mtts.mtts.remote_cache = 'remote' in rule['action']
        res = mtts.AsyncTask(mtts.mtts.generate, text=text, label_name=store.mas_submod_utils.current_label, emotion=exp, target_lang=target_lang)
        name = mtts.mtts.cache.get_cachename(text = text, label_name=store.mas_submod_utils.current_label)
        while not res.is_finished:
            old_renpysay(who, "...{w=0.3}{nw}", interact, *args, **kwargs)
            _history_list.pop()
        if res.is_success:
            res = res.result
            if res.is_success():
                store.mtts_status = renpy.substitute(_("播放中"))
                renpy.music.set_volume(persistent.mtts["volume"], channel="voice")
                renpy.music.play(
                    store.AudioData(res.data, name),#os.path.join(mtts.mtts.cache_path, "test.ogg"),
                    channel="voice",
                )
            else:
                renpy.notify("语音生成失败, 可能是服务器返回错误")
        else:
            renpy.notify("语音生成失败 {}".format(res.exception))

        store.mtts_status = renpy.substitute(_("待机"))

        old_renpysay(who, what, interact, *args, **kwargs)

    renpy.say = mtts_say