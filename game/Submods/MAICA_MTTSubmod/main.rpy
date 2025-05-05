init -100 python in mtts:
    import MTTS, store, os
    basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MTTSubmod"))
    if not store.mas_hasAPIKey("Maica_Token"):
        store.mas_registerAPIKey("Maica_Token", "Maica Token")
    mtts = MTTS.MTTS(
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    MTTS.logger = store.mas_submod_utils.submod_log
    
init python:
    old_renpysay = renpy.say
    store.mtts = mtts
    def mtts_say(who, what, interact=True, *args, **kwargs):
        renpy.notify("正在生成语音，请稍等...")
        res = mtts.mtts.generate(what)
        mtts.mtts.save_audio(res, "test.wav")
        renpy.play("test.wav", channel="voice")
        old_renpysay(who, what, interact, *args, **kwargs)

    renpy.say = mtts_say