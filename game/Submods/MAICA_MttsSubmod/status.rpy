

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
            alter_pos = (
                renpy.get_screen("mas_py_console_teaching") is not None
                or renpy.get_screen("mas_extramenu_area") is not None
            )
            xoff, yoff = (960, 5) if alter_pos else (5, 450)
        fixed:
            frame:
                xsize 309
                # xoffset 5 yoffset 450
                xoffset xoff yoffset yoff

                background bg
                vbox:
                    xoffset 5
                    hbox:
                        text renpy.substitute(_("MTTS状态: [store.mtts_status]")):
                            size 15

                    hbox:
                        text "CURR: [store.mas_submod_utils.current_label]":
                            size 14
                            font maica_confont

                    hbox:
                        text "RULE: [store.mtts_match_rule]":
                            size 14
                            font maica_confont


                if renpy.seen_label("mtts_greeting"):
                    fixed:
                        xysize (89, 24)
                        xalign 1.0
                        yalign 0.0
                        xoffset -3
                        yoffset 3

                        python:
                            if persistent.mtts.get("enabled", False) and store.mtts_say.conditions:
                                beacon = "{color=#00FF00}"
                            elif persistent.mtts.get("enabled", False):
                                beacon = "{color=#FFFF00}"
                            else:
                                beacon = "{color=#FF0000}"

                        button:
                            xfill True
                            yfill True
                            background "mod_assets/console/cn_frame_tts_button.png"
                            hover_background "mod_assets/console/cn_frame_tts_button_hover.png"
                            action [ToggleDict(persistent.mtts, "enabled", True, False), Function(mtts_autoacs), Function(mtts_refresh_status_once)]
                            add Text(
                                "{0}●{{/color}} I / O".format(beacon),
                                font=maica_confont,
                                size=14
                            ): 
                                xpos 34 
                                ypos 10 
                                xanchor 0.5 
                                yanchor 0.5


