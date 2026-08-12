init -990 python:
    store._maica_LoginAcc = ""
    store._maica_LoginPw = ""
    store._maica_LoginEmail = ""
    mtts_version = "1.2.14"
    # dependencies - dictionary in the following structure: {"name": ("minimum_version", "maximum_version")}
    store.mas_submod_utils.Submod(
        author="P",
        name="MTTS Synbrace",
        description=_("MAICA-MTTS Official Submod Frontend"),
        version=mtts_version,
        dependencies={"Ignore Translation Conflicts": (None, None)},
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
    on "show" action Function(store.mtts.refresh_setting_pane_cache)

    python:
        pane_cache = store.mtts.mtts_setting_pane_cache
        version_check = pane_cache.get("version_check", None)

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
                    text _("> Support for this version has ended, please update to the latest version"):
                        style "main_menu_version_l"

            if version_check is not None:
                $ res, libv, uiv = version_check
                if res is None:
                    hbox:
                        text _("> Warning: MTTS Libs version not found. Please install from Release, {color=#ff0000}NOT source code{/color}"):
                            style "main_menu_version_l"
                elif res != 0:
                    hbox:
                        text _("> Warning: MTTS Libs v[libv] mismatch with UI v[uiv]. Please fully update {color=#ff0000}from Release{/color}"):
                            style "main_menu_version_l"

            text "":
                size 0

        vbox:
            xmaximum 800
            xfill True
            style_prefix "check"

            if mtts_can_use_blessland_login():
                textbutton _("> Generate token from account (Blessland)"):
                    action Show("maica_login")
            else:
                textbutton _("> Generate token from account (Standalone)"):
                    action Show("mtts_login")
            textbutton _("> MTTS params and settings"):
                action Show("mtts_settings")

            if pane_cache.get("donation_exists", False):
                textbutton _("> Donate to MAICA"):
                    action Show("mtts_support")


init python:
    def _mtts_clear(save_token=False):
        store._maica_LoginAcc = ""
        store._maica_LoginPw = ""
        store._maica_LoginEmail = ""
        if save_token:
            store.mas_api_keys.api_keys.update({"Maica_Token":store.mtts.mtts_instance.token})
            store.mas_api_keys.save_keys()

    def _is_str(x):
        try:
            return isinstance(x, basestring)  # py2
        except Exception:
            return isinstance(x, str)

    def mtts_has_maica_instance():
        if not persistent.mtts.get("_chat_installed", False):
            return False
        return hasattr(store, "maica") and hasattr(store.maica, "maica_instance")

    def mtts_can_use_blessland_login():
        if not mtts_has_maica_instance():
            return False
        try:
            return store.maica.maica_instance.is_accessable()
        except Exception:
            return False

    def _mtts_verify_token(result=None):
        instance = store.mtts.mtts_instance
        res = result if result is not None else instance._verify_token()
        if res.get("success"):
            c = res.get("content", None)
            if _is_str(c) and c:
                instance.user_acc = c

            store.mtts_status = renpy.substitute(_("Standing by"))
            renpy.show_screen("maica_message", message=_("Verification successful"))
            return True
        else:
            if instance.status in (
                instance.MttsStatus.TOKEN_CORRUPTED,
                instance.MttsStatus.TOKEN_INVALID,
            ):
                store.mas_api_keys.api_keys.update({"Maica_Token":""})
                instance.token = ""
                store.mas_api_keys.save_keys()
            store.mtts_status = mtts_failure_status_text()
            message = renpy.substitute(_("Verification failed: ")) + store.mtts_status
            detail = u"{}".format(res.get("exception") or "")
            if detail:
                detail = detail.replace(u"[", u"[[").replace(u"]", u"]]")
                message += "\n" + renpy.substitute(_("Reason: ")) + detail
            renpy.show_screen("maica_message", message=message)
            return False

    def _mtts_submit_login():
        instance = store.mtts.mtts_instance
        previous_token = instance.token
        instance._gen_token(
            store._maica_LoginAcc,
            store._maica_LoginPw,
            "",
            store._maica_LoginEmail if store._maica_LoginEmail != "" else None,
        )
        if instance.has_error():
            result = instance.get_error_result()
            instance.token = previous_token
            success = _mtts_verify_token(result)
        else:
            success = _mtts_verify_token()
            if not success and instance.status not in (
                instance.MttsStatus.TOKEN_CORRUPTED,
                instance.MttsStatus.TOKEN_INVALID,
            ):
                instance.token = previous_token
        _mtts_clear(save_token=success)
    
    def mtts_try_sync_user_acc_from_blessland():
        """
        Blessland 登录模式下 (已通过验证): 先尝试从Chat侧拉取用户名, 失败则从 mas_api_keys 同步 token, 手动发一次请求从后端拉取用户名填充 user_acc.
        """
        
        if not persistent.mtts.get("_chat_installed", False):
            return
        if not mtts_has_maica_instance():
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
                        text renpy.substitute(_("Average power consumption: ")) + str(stat[server][card]["mean_consumption"]) + "W":
                            size 10
                text ""

            hbox:
                text renpy.substitute(_("Next data update")):
                    size 15
                text store.mtts.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 78, total=store.update_interval, unit="s"):
                    size 15
                    font maica_confont
                timer 1.0 repeat True action Function(check_and_update)
