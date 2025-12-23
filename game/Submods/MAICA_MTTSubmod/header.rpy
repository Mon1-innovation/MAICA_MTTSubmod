init -990 python:
    store._maica_LoginAcc = ""
    store._maica_LoginPw = ""
    store._maica_LoginEmail = ""
    mtts_version = "0.1.0"
    store.mas_submod_utils.Submod(
        author="P",
        name="MAICA MTTSubmod",
        description=_("MAICA官方TTS子模组"),
        version=mtts_version,
        settings_pane="mtts_settingpane"
    )


init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="MAICA MTTSubmod",
            user_name="Mon1-innovation",
            repository_name="MAICA_MTTSubmod",
            update_dir="",
            attachment_id=None
        )

screen mtts_settingpane():
    if persistent.mtts["_outdated"]:
        textbutton _("> 当前版本过旧, 请更新到最新版")

    if renpy.seen_label("mtts_greeting"):
        textbutton _(">登录"):
            action Show("mtts_login")
        textbutton _("> MTTS设置"):
            action Show("mtts_settings")
    else:
        textbutton _("> MTTS设置 (相关事件未解锁)")

screen mtts_settings():
    default tooltip = Tooltip("")
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
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
                textbutton _("MTTS 开关 [persistent.mtts.get('enabled')]"):
                    action ToggleDict(persistent.mtts, "enabled", True, False)
            
            hbox:
                textbutton _("语音音量: "):
                    action NullAction()

                bar:
                    value DictValue(persistent.mtts, "volume", 1.0, step=0.01,offset=0 ,style="slider")
                    xsize 200
                
                textbutton "[persistent.mtts.get('volume')]"
            
            hbox:
                textbutton _("展示状态小窗(需要重启)"):
                    action ToggleDict(persistent.mtts, "ministathud", True, False)
            
            hbox:
                textbutton _("是否装备饰品: [persistent.mtts.get('acs_enabled')]"):
                    action ToggleDict(persistent.mtts, "acs_enabled", True, False)
                    hovered SetField(_tooltip, "value", _("功能开关有延迟"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                        hbox:
                style_prefix "maica_check"
                textbutton (_("展开性能监控") if store.nvw_folded else _("收起性能监控")):
                    action [
                        Function(toggle_var, "nvw_folded")
                        ]
                    hovered SetField(_tooltip, "value", _("显示/收起服务器的性能状态指标"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not store.nvw_folded:
                hbox:
                    xpos 30
                    use maica_workload_stat()

                    
    hbox:
        textbutton _("关闭"):
            action [Function(store.mtts.apply_settings), Hide("mtts_settings")]
    if tooltip.value:
        frame:
            xalign 0.5 yalign 1.0
            yoffset -25
            text tooltip.value:
                style "main_menu_version"

init python:
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = ""
        store.mas_api_keys.api_keys.update({"Maica_Token":store.maica.maica.ciphertext})
        store.mas_api_keys.save_keys()

    def _maica_verify_token():
        res = store.maica.maica._verify_token()
        if res.get("success"):
            renpy.show_screen("maica_message", message=_("验证成功"))
        else:
            store.mas_api_keys.api_keys.update({"Maica_Token":""})
            store.maica.maica.ciphertext = ""
            renpy.show_screen("maica_message", message=renpy.substitute(_("验证失败, 请检查账号密码")) + "\n" + renpy.substitute(_("失败原因: ")) + res.get("exception"))


screen maica_workload_stat():
    $ _tooltip = store._tooltip
    python:
        stat = {k: v for k, v in iterize(store.mtts.mtts.workload_raw) if k != "onliners"}
    python:
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.maica.maica.update_workload()

    modal True
    zorder 90
    
    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            style_prefix "maica_default_small"
            xsize 942
            spacing 5


            for server in stat:

                use divider_small(server)

                for card in stat[server]:
                    hbox:
                        text stat[server][card]["name"]:
                            size 15
                        text store.mtts.progress_bar(stat[server][card]["mean_utilization"], total=int(stat[server][card]["tflops"]), unit="TFlops"):
                            size 10
                            font maica_confont

                        text "VRAM: " + str(stat[server][card]["mean_memory"]) + " / " + str(stat[server][card]["vram"]):
                            size 10
                        text renpy.substitute(_("平均功耗: ")) + str(stat[server][card]["mean_consumption"]) + "W":
                            size 10
                text ""

            hbox:
                text renpy.substitute(_("下次更新数据")):
                    size 15
                text store.maica.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 78, total=store.update_interval, unit="s"):
                    size 15
                    font maica_confont
                timer 1.0 repeat True action Function(check_and_update)
