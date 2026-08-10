init 10 python in mtts:
    import store
    def apply_settings():
        store.mtts.mtts_instance.enabled = store.persistent.mtts["enabled"]
        store.mtts.mtts_instance.volume = store.persistent.mtts["volume"]
        store.mtts.mtts_instance.acs_enabled = store.persistent.mtts["acs_enabled"]
        store.mtts.mtts_instance.ministathud = store.persistent.mtts["ministathud"]
        store.mtts.mtts_instance.provider_id = store.persistent.mtts["provider_id"]
        store.mtts.mtts_instance.drift_statshud_l = store.persistent.mtts["drift_statshud_l"]
        store.mtts.mtts_instance.drift_statshud_r = store.persistent.mtts["drift_statshud_r"]
        store.mtts.mtts_instance.generate_timeout = store.persistent.mtts["generate_timeout"]
        
    def discard_settings():
        store.persistent.mtts["enabled"] = store.mtts.mtts_instance.enabled
        store.persistent.mtts["volume"] = store.mtts.mtts_instance.volume
        store.persistent.mtts["acs_enabled"] = store.mtts.mtts_instance.acs_enabled
        store.persistent.mtts["ministathud"] = store.mtts.mtts_instance.ministathud
        store.persistent.mtts["provider_id"] = store.mtts.mtts_instance.provider_manager._provider_id
        store.persistent.mtts["drift_statshud_l"] = store.mtts.mtts_instance.drift_statshud_l
        store.persistent.mtts["drift_statshud_r"] = store.mtts.mtts_instance.drift_statshud_r
        store.persistent.mtts["generate_timeout"] = store.mtts.mtts_instance.generate_timeout
        store.persistent.mtts["use_custom_model_config"] = bool(store.persistent.mtts_advance_params)
    def reset_settings():
        store.persistent.mtts = store.setting.copy()


screen mtts_settings():
    default tooltip = Tooltip("")
    default nvw_folded = False

    if persistent.mtts.get("_chat_installed", False):
        # 打开设置页时尝试从chat同步一次用户名
        timer 0.2 action Function(mtts_try_sync_user_acc_from_blessland)

    python:
        submods_screen = store.renpy.get_screen("mtts_settings", "screens")
        if submods_screen:
            store._tooltip = submods_screen.scope.get("tooltip", None)
        else:
            store._tooltip = None
        def mtts_backup_advanced_setting():
            """Backup current advanced settings state before opening the screen"""
            store.persistent.mtts_advanced_setting_backup = store.persistent.mtts_advanced_setting.copy()
            store.persistent.mtts_advanced_setting_status_backup = store.persistent.mtts_advanced_setting_status.copy()


    $ _tooltip = store._tooltip

    $ w = 1100
    $ h = 640
    $ x = 0.5
    $ y = 0.5

    modal True
    zorder 90

    style_prefix "maica_check"

    use maica_common_outer_frame(w, h, x, y):
        use maica_common_inner_frame(w, h, x, y):


            hbox:
                use divider(_("Connection and security"))

            hbox:
                style_prefix "maica_check"
                textbutton _("Current provider: [store.mtts.provider_manager.get_server_info().get('name', 'Unknown')]"):
                    action Show("mtts_node_setting")
                    hovered SetField(_tooltip, "value", _("Set server node"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "maica_check_nohover"
                $ user_disp = store.mtts.mtts_instance.user_acc or renpy.substitute(_("Not logged in"))
                textbutton _("Current user: [user_disp]"):
                    action NullAction()
                    hovered SetField(_tooltip, "value", _("To change or log out of your account, log out from the Submods screen.\n* To change account information or password, visit the registration website"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)


            hbox:
                use divider(_("Behavior and performance"))

            if renpy.seen_label("mtts_greeting_end"):
                hbox:
                    style_prefix "generic_fancy_check"
                    textbutton _("Enable MTTS: [persistent.mtts.get('enabled')]"):
                        action [ToggleDict(persistent.mtts, "enabled", True, False), Function(mtts_autoacs), Function(mtts_refresh_status_once)]
                        hovered SetField(_tooltip, "value", _("Enable to generate and play TTS audio."))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            else:
                hbox:
                    style_prefix "maica_check_nohover"
                    text _("! MTTS not unlocked, enabling will not take effect"):
                        color "#FF0000"
                hbox:
                    textbutton _("Enable MTTS: [persistent.mtts.get('enabled')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.mtts, "enabled", True, False)
                        hovered SetField(_tooltip, "value", _("Enable to generate and play TTS audio.\n! MTTS not unlocked, enabling will not take effect"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
            
            $ tooltip_volume = _("TTS audio volume")
            use prog_bar(_("TTS volume"), 400, tooltip_volume, "volume", 0.0, 1.0, sdict="mtts")

            $ tooltip_generate_timeout = _("Skip current sentence if response time exceeds.\n* Do not set this too low")
            use prog_bar(_("Generation timeout (s)"), 400, tooltip_generate_timeout, "generate_timeout", 1, 120, istime=True, sdict="mtts")

            hbox:
                use divider(_("Tools and features"))

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("Display props when enabled: [persistent.mtts.get('acs_enabled')]"):
                    action [ToggleDict(persistent.mtts, "acs_enabled", True, False), Function(mtts_autoacs)]
                    hovered SetField(_tooltip, "value", _("Enable or disable MTTS microphone when using TTS.\n* MTTS headset not included since it's normal acs"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True

                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Replace player name: [persistent.mtts.get('replace_playername')]"):
                            action ToggleDict(persistent.mtts, "replace_playername", True, False)
                            hovered SetField(_tooltip, "value", _("Enable or disable player name replacement in speech generation.\n! Implemented directly through regex. Do not use if your in-game name commonly appears in unrelated context"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("Replace to: [persistent.mtts.get('playername_replacement') or 'Empty']"):
                            action Show("mtts_playername_replace_input")
                            hovered SetField(_tooltip, "value", _("Configure your spoken name.\n* Leave empty to not pronounce, but may lead to behaviour issue"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Show status HUD: [persistent.mtts.get('ministathud')]"):
                            action [ToggleDict(persistent.mtts, "ministathud", True, False), Function(maicatts_syncWorkLoadScreenStatus)]
                            hovered SetField(_tooltip, "value", _("Enable or disable MTTS status widget"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Compatible position left: [persistent.mtts.get('drift_statshud_l')]"):
                            action [ToggleDict(persistent.mtts, "drift_statshud_l", True, False), Function(renpy.restart_interaction)]
                            hovered SetField(_tooltip, "value", _("Enable or disable offseting status HUD to avoid possible conflict with other submods.\n* MTTS status HUD occupies bottom left of screen space by default\n* MTTS status HUD will be closer to central Y on left side if enabled"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Compatible position right: [persistent.mtts.get('drift_statshud_r')]"):
                            action [ToggleDict(persistent.mtts, "drift_statshud_r", True, False), Function(renpy.restart_interaction)]
                            hovered SetField(_tooltip, "value", _("Enable or disable offseting status HUD to avoid possible conflict with other submods.\n* MTTS status HUD occupies top right of screen space if console (like MAICA) displayed\n* MTTS status HUD will be closer to central Y on right side if enabled"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    $ tooltip_tts_cache = _("MTTS local cache to reduce resource consumption and latency.\n* Flush cache to apply new performance on model change\n! Do {color=#FF0000}NOT{/color} flush unless you know what you're doing")

                    hbox:
                        style_prefix "maica_check_nohover"
                        if not mtts_remove_cache_on_quit:
                            textbutton _("Current cache size: [store.mtts.mtts_instance.cache.cache_size]MB"):
                                action NullAction()
                                hovered SetField(_tooltip, "value", tooltip_tts_cache)
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("{color=#FF0000}Flush cache{/color}"):
                            action Show("mtts_purge_cache")
                            hovered SetField(_tooltip, "value", tooltip_tts_cache)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 4
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Enable customized advanced parameters: [persistent.mtts.get('use_custom_model_config', False)]"):
                            action ToggleDict(persistent.mtts, "use_custom_model_config", True, False)
                            hovered SetField(_tooltip, "value", _("Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    if persistent.mtts.get('use_custom_model_config', False):
                        hbox:
                            style_prefix "maica_check"
                            textbutton _("Set advanced parameters"):
                                style "maica_check_button"
                                action [Function(mtts_backup_advanced_setting), Show("mtts_advance_setting")]
                        hbox:
                            text _("! Active advanced parameters will disable remote cache, demanding per-request inference and transferring\n! This could cause massive extra cost on both server and client side, do consider carefully\n* Flush local cache to apply new performance"):
                                color "#FF0000"
                    else:
                        hbox:
                            textbutton _("Set advanced parameters"):
                                style "maica_check_button_disabled"
                                action [Function(mtts_backup_advanced_setting), Show("mtts_advance_setting")]



            hbox:
                style_prefix "maica_check"
                textbutton (_("Expand performance monitor") if nvw_folded else _("Collapse performance monitor")):
                    action SetScreenVariable("nvw_folded", not nvw_folded)
                    hovered SetField(_tooltip, "value", _("Show/hide server performance metrics"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not nvw_folded:
                hbox:
                    xpos 30
                    use mtts_workload_stat()

                    
    # hbox:
    #     textbutton _("关闭"):
    #         action [Function(store.mtts.apply_settings), Hide("mtts_settings")]
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Save settings"):
                action [
                        Function(store.mtts.apply_settings),
                        Function(renpy.notify, _("MTTS: Settings saved")),
                        Hide("mtts_settings")
                        ]
            textbutton _("Discard changes"):
                action [
                        Function(store.mtts.discard_settings),
                        Function(renpy.notify, _("MTTS: Settings discarded")),
                        Hide("mtts_settings")
                        ]
            textbutton _("Reset settings"):
                action [
                        Function(store.mtts.reset_settings),
                        Function(store.mtts.apply_settings),
                        Function(renpy.notify, _("MTTS: Settings reset")),
                        Hide("mtts_settings")
                    ]

    if tooltip.value:
        frame:
            xalign 0.5 yalign 1.0
            yoffset -25
            text tooltip.value:
                style "main_menu_version"

screen mtts_purge_cache():
    $ _tooltip = store._tooltip
    modal True
    zorder 95

    use maica_setter_small_frame(title=_("Flush cache"), ok_action=[Function(store.mtts.mtts_instance.cache.clear_cache), Hide("mtts_purge_cache")], cancel_action=Hide("mtts_purge_cache")):
        hbox:
            text _("Do {color=#FF0000}NOT{/color} flush unless you know what you're doing, which could cause massive extra cost on both server and client side"):
                size 20
        hbox:
            text _("Please confirm you understand what this means, or instructed by a MAICA technician"):
                size 20
