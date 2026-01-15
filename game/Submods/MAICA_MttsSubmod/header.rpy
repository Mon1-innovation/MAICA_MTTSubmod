init -990 python:
    store._maica_LoginAcc = ""
    store._maica_LoginPw = ""
    store._maica_LoginEmail = ""
    mtts_version = "0.1.7"
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
    vbox:
        # background None
        # has vbox:
            # yfit True

        vbox:
            spacing 5
            xpos 45
            xsize 900

            text "":
                size 0
            if persistent.mtts["_outdated"]:
                hbox:
                    text _("> 当前版本支持已终止, 请更新至最新版"):
                        style "main_menu_version_l"

            $ res, libv, uiv = store.mtts.validate_version()
            if res is None:
                hbox:
                    text _("> 警告: 未检测到MTTS库版本信息. 请从Release下载安装MTTS, 而不是源代码"):
                        style "main_menu_version_l"
            elif res != 0:
                hbox:
                    text _("> 警告: MTTS库版本[libv]与UI版本[uiv]不符. 请从Release完整地更新MTTS"):
                        style "main_menu_version_l"

            text "":
                size 0

        vbox:
            xmaximum 800
            xfill True
            style_prefix "check"

            if not persistent.mtts["_chat_installed"]:
                textbutton _("> 使用账号生成令牌 (独立模式)"):
                    action Show("mtts_login")
            else:
                textbutton _("> 使用账号生成令牌 (Blessland)"):
                    action Show("maica_login")
            textbutton _("> MTTS参数与设置"):
                action Show("mtts_settings")

            if os.path.exists(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_MttsSubmod", "donation")):
                textbutton _("> 向 MAICA 捐赠"):
                    action Show("mtts_support")

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
                $ user_disp = store.mtts.mtts.user_acc or renpy.substitute(_("未登录"))
                textbutton _("当前用户: [user_disp]"):
                    action NullAction()
                    hovered SetField(_tooltip, "value", _("如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往注册网站"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)


            hbox:
                use divider(_("行为与表现"))

            if (renpy.seen_label("mtts_greeting") and not mas_inEVL("mtts_greeting")):
                hbox:
                    style_prefix "generic_fancy_check"
                    textbutton _("启用MTTS: [persistent.mtts.get('enabled')]"):
                        action [ToggleDict(persistent.mtts, "enabled", True, False), Function(mtts_autoacs), Function(mtts_refresh_status_once)]
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
            use prog_bar(_("语音音量"), 400, tooltip_volume, "volume", 0.0, 1.0, sdict="mtts")

            hbox:
                use divider(_("工具与功能"))
            
            hbox:
                style_prefix "generic_fancy_check"
                textbutton _("显示状态小窗: [persistent.mtts.get('ministathud')]"):
                    action [ToggleDict(persistent.mtts, "ministathud", True, False), Function(maicatts_syncWorkLoadScreenStatus)]
                    hovered SetField(_tooltip, "value", _("是否在游戏内显示MTTS状态小窗"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

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
                    $ tooltip_tts_cache = _("MTTS本地缓存, 用以降低资源开销和响应延迟.\n* 若模型更换, 需要清除缓存以采用新的表现\n! 请{color=#FF0000}不要{/color}随意清除缓存, 这会产生大量额外开销")

                    hbox:
                        style_prefix "maica_check_nohover"
                        if not mtts_remove_cache_on_quit:
                            textbutton _("当前缓存占用：[store.mtts.mtts.cache.cache_size]MB"):
                                action NullAction()
                                hovered SetField(_tooltip, "value", tooltip_tts_cache)
                                unhovered SetField(_tooltip, "value", _tooltip.default)

                    hbox:
                        style_prefix "maica_check"
                        textbutton _("{color=#FF0000}清除缓存{/color}"):
                            action Function(store.mtts.mtts.cache.clear_cache)
                            hovered SetField(_tooltip, "value", tooltip_tts_cache)
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

init python:
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = ""
        store.mas_api_keys.api_keys.update({"Maica_Token":store.mtts.mtts.token})
        store.mas_api_keys.save_keys()

    def _is_str(x):
        try:
            return isinstance(x, basestring)  # py2
        except Exception:
            return isinstance(x, str)

    def _maica_verify_token():
        res = store.mtts.mtts._verify_token()
        if res.get("success"):
            c = res.get("content", None)
            if _is_str(c) and c:
                store.mtts.mtts.user_acc = c

            renpy.show_screen("maica_message", message=_("验证成功"))
        else:
            store.mas_api_keys.api_keys.update({"Maica_Token":""})
            renpy.show_screen("maica_message", message=renpy.substitute(_("验证失败, 请检查账号密码")) + "\n" + renpy.substitute(_("失败原因: ")) + res.get("exception"))
    
    def mtts_try_sync_user_acc_from_blessland():
        """
        Blessland 登录模式下 (已通过验证): 先尝试从Chat侧拉取用户名, 失败则从 mas_api_keys 同步 token, 手动发一次请求从后端拉取用户名填充 user_acc.
        """
        
        if not persistent.mtts.get("_chat_installed", False):
            return

        m = store.mtts.mtts

        # 拉取Chat侧的 user_acc (如有)
        acc = getattr(store.maica.maica, "user_acc", "")
        if acc:
            if getattr(m, "user_acc", u"") != acc:
                m.user_acc = acc
                renpy.restart_interaction()
            return
        
        if getattr(m, "user_acc", u""):
            return

        try:
            token = store.mas_getAPIKey("Maica_Token") or ""
        except Exception:
            token = ""
        if not token:
            return
        if getattr(m, "token", "") != token:
            m.token = token
        res = m._verify_token()
        
        if not res.get("success", False):
            return
        
        c = res.get("content", None)
        if _is_str(c) and c:
            m.user_acc = c
            renpy.restart_interaction()
            return
    
init python:
    from MTTS import PY2, PY3
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


define maica_confont = "mod_assets/font/SarasaMonoTC-SemiBold.ttf"
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
