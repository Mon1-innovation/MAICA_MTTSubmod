init -990 python:
    mtts_defaultsettings = {
        "enabled": False,
        "_chat_installed": False,
        "volume": 1.0,
        "acs_enabled": True
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
    mtts = MTTS.MTTS(
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    matcher = MTTS.CacheRuleMatcher(os.path.join(basedir, "cache_rules.json"))
    AsyncTask = MTTS.AsyncTask
    MTTS.logger = store.mas_submod_utils.submod_log

    def apply_settings():
        pass
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
    if PY2:
        import datapy2_mtts
        pattern_content = datapy2_mtts.pattern_content
    else:
        pattern_content = r'[A-Za-z一-龥0-9]'
    def mtts_say(who, what, interact=True, *args, **kwargs):
        def process_str(srt):
            import re
            # \{fast\}.*?\{fast\} , \{.*?\} 将匹配的str替换为空字符串
            srt = re.sub(r"\{fast\}.*?\{fast\}", "", srt)
            srt = re.sub(r"\{.*?\}", "", srt)
            return srt
        if not persistent.mtts["enabled"]:
            return old_renpysay(who, what, interact, *args, **kwargs)
        text = process_str(renpy.substitute(what))
        rule = store.mtts.matcher.match_rule(text, store.mas_submod_utils.current_label)
        if not rule['action']:
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