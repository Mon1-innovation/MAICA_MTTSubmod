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
        
    def discard_settings():
        store.persistent.mtts["enabled"] = store.mtts.mtts_instance.enabled
        store.persistent.mtts["volume"] = store.mtts.mtts_instance.volume
        store.persistent.mtts["acs_enabled"] = store.mtts.mtts_instance.acs_enabled
        store.persistent.mtts["ministathud"] = store.mtts.mtts_instance.ministathud
        store.persistent.mtts["provider_id"] = store.mtts.mtts_instance.provider_manager._provider_id
        store.persistent.mtts["drift_statshud_l"] = store.mtts.mtts_instance.drift_statshud_l
        store.persistent.mtts["drift_statshud_r"] = store.mtts.mtts_instance.drift_statshud_r
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
                use divider(_("连接与安全"))

            hbox:
                style_prefix "maica_check"
                textbutton _("服务提供节点: [store.mtts.provider_manager.get_server_info().get('name', 'Unknown')]"):
                    action Show("mtts_node_setting")
                    hovered SetField(_tooltip, "value", _("设置服务器节点"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
            hbox:
                style_prefix "maica_check_nohover"
                $ user_disp = store.mtts.mtts_instance.user_acc or renpy.substitute(_("未登录"))
                textbutton _("当前用户: [user_disp]"):
                    action NullAction()
                    hovered SetField(_tooltip, "value", _("如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往注册网站"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)


            hbox:
                use divider(_("行为与表现"))

            if renpy.seen_label("mtts_greeting_end"):
                hbox:
                    style_prefix "generic_fancy_check"
                    textbutton _("启用MTTS: [persistent.mtts.get('enabled')]"):
                        action [ToggleDict(persistent.mtts, "enabled", True, False), Function(mtts_autoacs), Function(mtts_refresh_status_once)]
                        hovered SetField(_tooltip, "value", _("启用以生成和播放TTS."))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            else:
                hbox:
                    style_prefix "maica_check_nohover"
                    text _("! MTTS未解锁, 启用不会生效"):
                        color "#FF0000"
                hbox:
                    textbutton _("启用MTTS: [persistent.mtts.get('enabled')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.mtts, "enabled", True, False)
                        hovered SetField(_tooltip, "value", _("启用以生成和播放TTS.\n! MTTS未解锁, 启用不会生效"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
            
            $ tooltip_volume = _("TTS的语音音量")
            use prog_bar(_("语音音量"), 400, tooltip_volume, "volume", 0.0, 1.0, sdict="mtts")

            hbox:
                use divider(_("工具与功能"))

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("启用时显示道具: [persistent.mtts.get('acs_enabled')]"):
                    action [ToggleDict(persistent.mtts, "acs_enabled", True, False), Function(mtts_autoacs)]
                    hovered SetField(_tooltip, "value", _("是否在MTTS启用时展示麦克风.\n* MTTS耳机属于普通饰品, 请以常规方式穿戴或取下"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True

                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("替换玩家名称: [persistent.mtts.get('replace_playername')]"):
                            action ToggleDict(persistent.mtts, "replace_playername", True, False)
                            hovered SetField(_tooltip, "value", _("是否在MTTS生成中替换玩家名称.\n! 该替换直接通过正则实现, 若你的游戏内名称容易在正常词句中出现, 则不要使用"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("替换为: [persistent.mtts.get('playername_replacement') or 'Empty']"):
                            action Show("mtts_playername_replace_input")
                            hovered SetField(_tooltip, "value", _("配置你希望使用的配音名称.\n* 设为空以不读名称, 但这更容易引发表现问题"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("显示状态小窗: [persistent.mtts.get('ministathud')]"):
                            action [ToggleDict(persistent.mtts, "ministathud", True, False), Function(maicatts_syncWorkLoadScreenStatus)]
                            hovered SetField(_tooltip, "value", _("是否在游戏内显示MTTS状态小窗"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("左侧屏幕空间避让: [persistent.mtts.get('drift_statshud_l')]"):
                            action [ToggleDict(persistent.mtts, "drift_statshud_l", True, False), Function(renpy.restart_interaction)]
                            hovered SetField(_tooltip, "value", _("是否向Y轴中心偏移小窗以避免子模组冲突.\n* 在默认情况下, MTTS状态小窗显示在屏幕左下\n* 如果启用, MTTS小窗会更靠近屏幕左侧中心"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("右侧屏幕空间避让: [persistent.mtts.get('drift_statshud_r')]"):
                            action [ToggleDict(persistent.mtts, "drift_statshud_r", True, False), Function(renpy.restart_interaction)]
                            hovered SetField(_tooltip, "value", _("是否向Y轴中心偏移小窗以避免子模组冲突.\n* 在控制台显示(如MAICA)的情况下, MTTS状态小窗显示在屏幕右上\n* 如果启用, MTTS小窗会更靠近屏幕右侧中心"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    $ tooltip_tts_cache = _("MTTS本地缓存, 用以降低资源开销和响应延迟.\n* 若模型更换, 需要清除缓存以采用新的表现\n! 请{color=#FF0000}不要{/color}随意清除缓存, 这会产生大量额外开销")

                    hbox:
                        style_prefix "maica_check_nohover"
                        if not mtts_remove_cache_on_quit:
                            textbutton _("当前缓存占用：[store.mtts.mtts_instance.cache.cache_size]MB"):
                                action NullAction()
                                hovered SetField(_tooltip, "value", tooltip_tts_cache)
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("{color=#FF0000}清除缓存{/color}"):
                            action Show("mtts_purge_cache")
                            hovered SetField(_tooltip, "value", tooltip_tts_cache)
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                frame:
                    xmaximum 950
                    xpos 30
                    xfill True
                    has vbox:
                        xmaximum 950
                        xfill True
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("使用自定义高级参数: [persistent.mtts.get('use_custom_model_config', False)]"):
                            action ToggleDict(persistent.mtts, "use_custom_model_config", True, False)
                            hovered SetField(_tooltip, "value", _("高级参数可能大幅影响MTTS的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)
                    if persistent.mtts.get('use_custom_model_config', False):
                        hbox:
                            style_prefix "maica_check"
                            textbutton _("设置高级参数"):
                                style "maica_check_button"
                                action [Function(mtts_backup_advanced_setting), Show("mtts_advance_setting")]
                        hbox:
                            text _("! 如果启用并调整了高级参数, 生成结果将无法被远程缓存, 每个请求都需要推理和传输\n! 这可能对服务器和你的数据流量造成大量额外开销, 请慎重考虑\n* 清除你的本地缓存以采用新的表现"):
                                color "#FF0000"
                    else:
                        hbox:
                            textbutton _("设置高级参数"):
                                style "maica_check_button_disabled"
                                action [Function(mtts_backup_advanced_setting), Show("mtts_advance_setting")]



            hbox:
                style_prefix "maica_check"
                textbutton (_("展开性能监控") if nvw_folded else _("收起性能监控")):
                    action SetScreenVariable("nvw_folded", not nvw_folded)
                    hovered SetField(_tooltip, "value", _("显示/收起服务器的性能状态指标"))
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
            textbutton _("保存设置"):
                action [
                        Function(store.mtts.apply_settings),
                        Function(renpy.notify, _("MTTS: 设置已保存")),
                        Hide("mtts_settings")
                        ]
            textbutton _("放弃修改"):
                action [
                        Function(store.mtts.discard_settings),
                        Function(renpy.notify, _("MTTS: 已放弃设置修改")),
                        Hide("mtts_settings")
                        ]
            textbutton _("重置设置"):
                action [
                        Function(store.mtts.reset_settings),
                        Function(store.mtts.apply_settings),
                        Function(renpy.notify, _("MTTS: 设置已重置")),
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

    use maica_setter_small_frame(title=_("清除缓存"), ok_action=[Function(store.mtts.mtts_instance.cache.clear_cache), Hide("mtts_purge_cache")], cancel_action=Hide("mtts_purge_cache")):
        hbox:
            text _("请{color=#FF0000}不要{/color}随意清除缓存, 这可能对服务器和你的数据流量造成大量额外开销"):
                size 20
        hbox:
            text _("请确认你明白自己在做什么, 或者已得到有资质的技术人员的指导"):
                size 20
