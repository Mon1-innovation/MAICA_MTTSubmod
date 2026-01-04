init -990 python:
    store._maica_LoginAcc = ""
    store._maica_LoginPw = ""
    store._maica_LoginEmail = ""
    mtts_version = "0.1.0"
    store.mas_submod_utils.Submod(
        author="P",
        name="MTTS Synbrace",
        description=_("MAICA-MTTS官方前端子模组"),
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

    if not persistent.mtts["_chat_installed"]:
        textbutton _("> 登录 (未安装Blessland, 使用独立模式)"):
            action Show("mtts_login")
    else:
        textbutton _("> 使用 MAICA Blessland 完成登录"):
            action Show("maica_login")
    textbutton _("> MTTS设置"):
        action Show("mtts_settings")


screen mtts_settings():
    default tooltip = Tooltip("")
    default nvw_folded = False
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")
        if submods_screen:
            store._tooltip = submods_screen.scope.get("tooltip", None)
        else:
            store._tooltip = None

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
                use divider(_("行为与表现"))

            if renpy.seen_label("mtts_greeting"):
                hbox:
                    style_prefix "generic_fancy_check"
                    textbutton _("启用MTTS: [persistent.mtts.get('enabled')]"):
                        action ToggleDict(persistent.mtts, "enabled", True, False)
                        hovered SetField(_tooltip, "value", _("启用以生成和播放TTS."))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            else:
                hbox:
                    text _("! MTTS未解锁, 启用不会生效"):
                        color "#FF0000"
                hbox:
                    textbutton _("启用MTTS: [persistent.mtts.get('enabled')]"):
                        style "generic_fancy_check_button_disabled"
                        action ToggleDict(persistent.mtts, "enabled", True, False)
                        hovered SetField(_tooltip, "value", _("启用以生成和播放TTS.\n! MTTS未解锁, 启用不会生效"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
            
            $ tooltip_volume = _("TTS的语音音量")
            use prog_bar(_("语音音量"), 200 if config.language == "chinese" else 350, tooltip_volume, "volume", 0.0, 1.0, sdict="mtts")

            hbox:
                use divider(_("工具与功能"))
            
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("显示状态小窗: [persistent.mtts.get('ministathud')]"):
                    action [ToggleDict(persistent.mtts, "ministathud", True, False), Function(maicatts_syncWorkLoadScreenStatus)]
                    hovered SetField(_tooltip, "value", _("是否在屏幕右上角显示MTTS状态小窗"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("启用时显示饰品: [persistent.mtts.get('acs_enabled')]"):
                    action [ToggleDict(persistent.mtts, "acs_enabled", True, False), Function(mtts_autoacs)]
                    hovered SetField(_tooltip, "value", _("是否在MTTS启用时自动穿戴对应饰品.\n* 可能有一定延迟"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            hbox:
                use divider(_("统计与信息"))

            hbox:
                style_prefix "maica_check"
                textbutton (_("展开性能监控") if nvw_folded else _("收起性能监控")):
                    action SetScreenVariable("nvw_folded", not nvw_folded)
                    hovered SetField(_tooltip, "value", _("显示/收起服务器的性能状态指标"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

            if not nvw_folded:
                hbox:
                    xpos 30
                    use maica_workload_stat()

                    
    # hbox:
    #     textbutton _("关闭"):
    #         action [Function(store.mtts.apply_settings), Hide("mtts_settings")]
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("保存设置"):
                action [
                        Function(store.mtts.apply_settings),
                        Function(renpy.notify, _("MTTS: 已保存修改")),
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
                        Function(renpy.notify, _("MTTS: 已重置设置")),
                        Hide("mtts_settings")
                    ]


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
        store.mas_api_keys.api_keys.update({"Maica_Token":store.mtts.mtts.token})
        store.mas_api_keys.save_keys()

    def _maica_verify_token():
        res = store.mtts.mtts._verify_token()
        if res.get("success"):
            renpy.show_screen("maica_message", message=_("验证成功"))
        else:
            store.mas_api_keys.api_keys.update({"Maica_Token":""})
            renpy.show_screen("maica_message", message=renpy.substitute(_("验证失败, 请检查账号密码")) + "\n" + renpy.substitute(_("失败原因: ")) + res.get("exception"))
init python:
    from bot_interface import PY2, PY3
    def iterize(dict):
        if PY2:
            return dict.iteritems()
        elif PY3:
            return dict.items()
    
    import time
    class ThrottleReturnNone(object):
        """This is a wrapper."""
        
        def __init__(self, wait):
            self.wait = wait
            self.last_called = 0.0
            self.remain = 0
            self.result = None
        
        def __call__(self, func):
            def wrapper(*args, **kwargs):
                now = time.time()
                elapsed = now - self.last_called
                
                if elapsed < self.wait:
                    pass
                else:
                    self.last_called = now
                    self.result = func(*args, **kwargs)

                self.remain = self.wait - elapsed
                if self.remain < 0.0:
                    self.remain = 0.0

                return None
            
            return wrapper

    store.workload_throttle = ThrottleReturnNone(15.0)

    def common_can_add(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        return min <= s_dict[var] < max

    def common_add(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        if common_can_add(var, min, max, sdict):
            s_dict[var] += unit
            if s_dict[var] > max:
                s_dict[var] = max

    def common_can_sub(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        return min < s_dict[var] <= max

    def common_sub(var, min, max, sdict):
        if isinstance(max, float):
            unit = 0.01
        else:
            unit = 1
        s_dict = getattr(persistent, sdict)
        if common_can_sub(var, min, max, sdict):
            s_dict[var] -= unit
            if s_dict[var] < min:
                s_dict[var] = min

    def toggle_var(var):
        if getattr(store, var, None):
            setattr(store, var, False)
        else:
            setattr(store, var, True)


define maica_confont = mas_ui.MONO_FONT
screen maica_workload_stat():
    python:
        stat = {k: v for k, v in iterize(store.mtts.mtts.workload_raw) if k != "onliners"}
    python:
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.mtts.mtts.update_workload()

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
                text store.mtts.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 78, total=store.update_interval, unit="s"):
                    size 15
                    font maica_confont
                timer 1.0 repeat True action Function(check_and_update)
