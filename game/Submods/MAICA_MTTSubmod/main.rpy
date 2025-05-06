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
    
init python:
    old_renpysay = renpy.say
    store.mtts = mtts
    def mtts_say(who, what, interact=True, *args, **kwargs):
        renpy.notify("正在生成语音，请稍等...")
        #res = mtts.mtts.generate(what)
        res = mtts.AsyncTask(mtts.mtts.generate, text=renpy.substitute(what))
        while not res.is_finished:
            old_renpysay(who, "...{w=0.3}{nw}", interact, *args, **kwargs)
        if res.is_success:
            res = res.result
            if res.is_success():
                mtts.mtts.save_audio(res.data, "test.ogg")
                renpy.music.play(
                    store.AudioData(res.data, "test.ogg"),#os.path.join(mtts.mtts.cache_path, "test.ogg"),
                    channel="voice",
                )
            else:
                renpy.notify("语音生成失败2")
        else:
            renpy.notify("语音生成失败 {}".format(res.exception))

        old_renpysay(who, what, interact, *args, **kwargs)

    renpy.say = mtts_say