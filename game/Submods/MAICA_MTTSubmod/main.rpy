init 10 python in mtts:
    import MTTS, store
    basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MTTSubmod"))
    mtts = MTTS.MTTS(
        token = store.mas_getAPIKey("Maica_Token"),
        cache_path = basedir + "/cache",
    )
    MTTS.logger = store.mas_submod_utils.submod_log