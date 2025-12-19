

init -1 python:
    if not hasattr(store, "mtts_status"):
        store.mtts_status = renpy.substitute(_("待机"))
    # default store.mtts_status = renpy.substitute(_("待机"))
    # quick functions to enable disable the mouse tracker
    def maicatts_enableWorkLoadScreen():
        if not maica_isWorkLoadScreenVisible():
            config.overlay_screens.append("maicatts_stat_lite")

    def maicatts_disableWorkLoadScreen():
        if maica_isWorkLoadScreenVisible():
            config.overlay_screens.remove("maicatts_stat_lite")
            renpy.hide_screen("maicatts_stat_lite")

    def maicatts_isWorkLoadScreenVisible():
        return "maicatts_stat_lite" in config.overlay_screens

screen maicatts_stat_lite():
    python:
        mtts_instance = store.mtts.mtts
    zorder 90
    fixed:
        frame:
            xsize 619
            xoffset 5 yoffset 450
            background "mod_assets/console/cn_frame_stats.png"
            has vbox
            hbox:
                text renpy.substitute(_("MTTS状态: [store.mtts_status]")):
                    size 15
                
                text _("当前label: [store.mas_submod_utils.current_label]")

