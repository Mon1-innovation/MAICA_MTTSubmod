init -990 python:
    mtts_defaultsettings = {
        "enabled": True,
        "_chat_installed": False,
        "volume": 1.0,
        "conversion": True
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
    AsyncTask = MTTS.AsyncTask
    MTTS.logger = store.mas_submod_utils.submod_log

    def apply_settings():
        mtts.conversion = store.persistent.mtts["conversion"]

init -100 python:
    try:
        import json_exporter
        persistent.mtts["_chat_installed"] = True
        def get_emote_mood(emote, emotion_selector = json_exporter.emotion_selector):  # 获取情绪
            try:
                for mood, keywords in emotion_selector.items():  # 遍历情绪和关键词字典
                    for key in keywords:  # 遍历当前情绪的所有关键词
                        if emote in key:  # 检查关键词是否存在于输入字符串
                            return mood
            except Exception as e:
                pass
            return "微笑"  # 无匹配时返回 None
    except ImportError:
        persistent.mtts["_chat_installed"] = False
init python:
    
    old_renpysay = renpy.say
    store.mtts = mtts
    def mtts_say(who, what, interact=True, *args, **kwargs):
        def process_str(srt):
            import re
            # \{fast\}.*?\{fast\} , \{.*?\} 将匹配的str替换为空字符串
            srt = re.sub(r"\{fast\}.*?\{fast\}", "", srt)
            srt = re.sub(r"\{.*?\}", "", srt)
            return srt
        if not persistent.mtts["enabled"] or not persistent.mtts["_chat_installed"]:
            return old_renpysay(who, what, interact, *args, **kwargs)
        renpy.notify("正在生成语音，请稍等...")
        #res = mtts.mtts.generate(what)
        exp = store.get_emote_mood(store.mas_getCurrentMoniExp())
        has_player = "[player]" in what
        text = process_str(renpy.substitute(what))
        _old_remote_cache = mtts.mtts.remote_cache
        if has_player:
            mtts.mtts.remote_cache = False
        res = mtts.AsyncTask(mtts.mtts.generate, text=text, label_name=store.mas_submod_utils.current_label, emotion=exp)
        name = mtts.mtts.cache.get_cachename(text = text, label_name=store.mas_submod_utils.current_label)
        if has_player:
            mtts.mtts.remote_cache = _old_remote_cache
        while not res.is_finished:
            old_renpysay(who, "...{w=0.3}{nw}", interact, *args, **kwargs)
            _history_list.pop()
        if res.is_success:
            res = res.result
            if res.is_success():
                renpy.music.set_volume(persistent.mtts["volume"], channel="voice")
                renpy.music.play(
                    store.AudioData(res.data, name),#os.path.join(mtts.mtts.cache_path, "test.ogg"),
                    channel="voice",
                )
            else:
                renpy.notify("语音生成失败, 可能是服务器返回错误")
        else:
            renpy.notify("语音生成失败 {}".format(res.exception))

        old_renpysay(who, what, interact, *args, **kwargs)

    renpy.say = mtts_say