init 10 python in mtts:
    import MTTS, store
    basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MTTSubmod"))
    if not store.mas_hasAPIKey("Maica_Token"):
        store.mas_registerAPIKey("Maica_Token", "Maica Token")
    mtts = MTTS.MTTS(
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    MTTS.logger = store.mas_submod_utils.submod_log
    
init 20 python:
    old_renpysay = renpy.say
    store.mtts = mtts
    def mtts_say(who, what, interact=True, *args, **kwargs):
        mtts.mtts.generate(what)
        mtts.mtts.save_audio("test.wav")
        renpy.play("test.wav", channel="voice")
        old_renpysay(who, what, interact, *args, **kwargs)

    store.renpy_say = mtts_say