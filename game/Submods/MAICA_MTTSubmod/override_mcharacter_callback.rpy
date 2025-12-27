init python:
    # 条件显示的角色回调
    # 这个回调会在显示对话前检查条件，如果条件不满足则暂停直到条件满足
    import MTTS
    def cb_mtts_monika(event, interact=True, what=None, **kwargs):
        """
        条件显示回调函数

        参数：
        - event: 回调事件类型
        - interact: 是否发生交互
        - condition_check: 一个返回布尔值的可调用对象，检查是否应该显示对话
        - **kwargs: 其他回调参数
        """
        if not interact:
            return
        #log所有入参：
        store.mas_submod_utils.submod_log.debug("event: {}, interact: {}, what: {}, kwargs: {}".format(event, interact, what, kwargs))
        # 在"show"事件时检查条件
        if event == "show":
            if what == None:
                what = renpy.last_say().what
            # 如果条件不满足，暂停直到条件满足
            if what and mtts_available():
                store.mtts_saying_what = what
                sound_thread = mtts.AsyncTask(mtts_generate_sound, what)
                while not sound_thread.is_finished:
                    renpy.pause(0.1)
                if sound_thread.exception:
                    raise sound_thread.exception
                

    monika_callbacks_list = []
    monika_callbacks_list.append(cb_mtts_monika)

    def cb_monika(*args, **kwargs):
        for cb in monika_callbacks_list:
            cb(*args, **kwargs)


init 1 python:
    monika_callbacks_list.append(slow_nodismiss)

    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=900)
    def override_mcb():
        m.display_args['callback'] = cb_monika

    #m2 = DynamicCharacter('m_name', image='monika', what_prefix='', what_suffix='', ctc="ctc", ctc_position="fixed", show_function=store.mas_core.show_display_say, callback=cb_mtts_monika)
    #config.all_character_callbacks.append(cb_mtts_monika)
    #m.display_args['callback'] = cb_mtts_monika
#init 1 python:
#    m = m2