init -990 python:
    store._maica_LoginAcc = ""
    store._maica_LoginPw = ""
    store._maica_LoginEmail = ""
    mtts_version = "1.0.4"
    store.mas_submod_utils.Submod(
        author="P",
        name="MTTS Synbrace",
        description=_("MAICA-MTTS官方前端子模组"),
        version=mtts_version,
        settings_pane="mtts_settingpane"
    )

default persistent._mtts_last_version = "0.0.1"

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


init python:
    def _maica_clear():
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = ""
        store.mas_api_keys.api_keys.update({"Maica_Token":store.mtts.mtts_instance.token})
        store.mas_api_keys.save_keys()

    def _is_str(x):
        try:
            return isinstance(x, basestring)  # py2
        except Exception:
            return isinstance(x, str)

    def _maica_verify_token():
        res = store.mtts.mtts_instance._verify_token()
        if res.get("success"):
            c = res.get("content", None)
            if _is_str(c) and c:
                store.mtts.mtts_instance.user_acc = c

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

        m = store.mtts.mtts_instance

        # 拉取Chat侧的 user_acc (如有)
        acc = getattr(store.maica.maica_instance, "user_acc", "")
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
    from mtts_package import PY2, PY3
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
screen mtts_workload_stat():
    python:
        stat = {k: v for k, v in iterize(store.mtts.mtts_instance.workload_raw) if k != "onliners"}
    python:
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.mtts.mtts_instance.update_workload()

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

