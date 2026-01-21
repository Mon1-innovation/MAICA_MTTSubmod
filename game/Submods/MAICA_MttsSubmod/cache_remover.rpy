init python:
    mtts_remove_cache_on_quit = False

    @store.mas_submod_utils.functionplugin("_quit", priority=-100)
    def rm_cache():
        if mtts_remove_cache_on_quit:
            store.mtts.mtts_instance.cache.clear_cache()