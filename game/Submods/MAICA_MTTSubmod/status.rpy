

init -1 python:
    if not hasattr(store, "mtts_status"):
        store.mtts_status = renpy.substitute(_("待机"))
    if not hasattr(store, "mtts_match_rule"):
        store.mtts_match_rule = "Unknown"
    # default store.mtts_status = renpy.substitute(_("待机"))
    # quick functions to enable disable the mouse tracker
    def maicatts_enableWorkLoadScreen():
        if not maicatts_isWorkLoadScreenVisible():
            config.overlay_screens.append("maicatts_stat_lite")

    def maicatts_disableWorkLoadScreen():
        if maicatts_isWorkLoadScreenVisible():
            config.overlay_screens.remove("maicatts_stat_lite")
            renpy.hide_screen("maicatts_stat_lite")

    def maicatts_isWorkLoadScreenVisible():
        return "maicatts_stat_lite" in config.overlay_screens
    
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=1000)
    def auto_show_statlite():
        if persistent.mtts['ministathud']:
            maicatts_enableWorkLoadScreen()

    def maicatts_syncWorkLoadScreenStatus():
        # if persistent.mtts.get("ministathud", False):
        #     maicatts_enableWorkLoadScreen()
        # else:
        #     maicatts_disableWorkLoadScreen()

        maicatts_enableWorkLoadScreen()
        renpy.restart_interaction()

screen maicatts_stat_lite():
    zorder 90
    if not persistent.mtts.get("ministathud", False):
        null
    else:    
        python:
            mtts_instance = store.mtts.mtts
            bg = "mod_assets/console/cn_frame_tts_on.png" if persistent.mtts.get("enabled", False) and store.mtts_say.conditions else "mod_assets/console/cn_frame_tts_off.png"
        fixed:
            frame:
                xsize 309
                xoffset 5 yoffset 450
                # background "mod_assets/console/cn_frame_stats.png"
                background bg
                has vbox
                hbox:
                    text renpy.substitute(_("MTTS状态: [store.mtts_status]")):
                        size 15

                    if renpy.seen_label("mtts_greeting"):
                        text "  ":
                            size 15
                        textbutton _("启用MTTS: [persistent.mtts.get('enabled')]"):
                            style "hkb_button"
                            action [ToggleDict(persistent.mtts, "enabled", True, False), Function(mtts_autoacs)]

                hbox:
                    text "CURR: [store.mas_submod_utils.current_label]":
                        size 14
                        font maica_confont

                hbox:
                    text "RULE: [store.mtts_match_rule]":
                        size 14
                        font maica_confont


