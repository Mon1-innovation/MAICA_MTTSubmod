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
        textbutton _("> MTTS设置"):
            action Show("mtts_settings")
    else:
        textbutton _("> MTTS设置 (相关事件未解锁)")

screen mtts_settings():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")

        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
    modal True
    zorder 215
    
    style_prefix "check"

    frame:
        vbox:
            xmaximum 1100
            spacing 5
            viewport:
                id "viewport"
                scrollbars "vertical"
                ymaximum 600
                xmaximum 1100
                xfill True
                yfill False
                mousewheel True
                draggable True
                
                vbox:
                    xmaximum 1100
                    xfill True
                    yfill False

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
                        textbutton _("是否装备饰品: [persistent.mtts.get('acs_enabled')]"):
                            action ToggleDict(persistent.mtts, "acs_enabled", True, False)
                            hovered SetField(_tooltip, "value", _("功能开关有延迟"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

                            
                
            textbutton _("关闭"):
                action [Function(store.mtts.apply_settings), Hide("mtts_settings")]

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