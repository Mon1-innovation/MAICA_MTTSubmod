default use_email = True

screen mtts_login():
    modal True
    zorder 92
    $ ok_action = [
                    Function(store.mtts.mtts._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
                    Function(_maica_verify_token),
                    Function(_maica_clear),
                    Hide("mtts_login")
                    ]
    $ cancel_action = [Function(_maica_clear), Hide("mtts_login")]

    use maica_setter_medium_frame(ok_action=ok_action, cancel_action=cancel_action):

        hbox:
            if use_email:
                textbutton _("输入DCC账号邮箱"):
                    style "confirm_button"
                    action Show("mtts_login_input",message = _("请输入DCC账号邮箱"),returnto = "_maica_LoginEmail")
            else:
                textbutton _("输入DCC账号用户名"):
                    style "confirm_button"
                    action Show("mtts_login_input",message = _("请输入DCC账号用户名") ,returnto = "_maica_LoginAcc")

        hbox:
            style_prefix "maica_check"
            if use_email:
                textbutton _("> 改为用户名登录"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_maica_clear)]
                    selected False

            else:
                textbutton _("> 改为邮箱登录"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_maica_clear)]
                    selected False

        hbox:
            textbutton _("输入密码"):
                style "confirm_button"
                action Show("mtts_login_input",message = _("请输入密码"),returnto = "_maica_LoginPw")
        hbox:
            text ""

        hbox:
            style_prefix "small_expl"
            text _("※ 使用MAICA Blessland, 即认为你同意 "):
                size 15
            textbutton _("{u}MAICA服务条款{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0

        hbox:
            style_prefix "small_expl"
            text _("※ 还没有DCC账号? "):
                size 15
            textbutton _("{u}注册一个{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0


screen mtts_login_input(message, returnto, ok_action = Hide("mtts_login_input")):
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 92

    use maica_setter_medium_frame(message, ok_action):
        input default "" value VariableInputValue(returnto) length 64


screen mtts_node_setting():
    ## Service provider node picker (ported from MAICA_CHAT)
    modal True
    zorder 92

    $ w = 1100
    $ h = 640
    $ x = 0.5
    $ y = 0.5

    style_prefix "maica_check"

    use maica_common_outer_frame(w, h, x, y):
        use maica_common_inner_frame(w, h, x, y):

            hbox:
                use divider(_("服务提供节点"))

            viewport:
                draggable True
                mousewheel True
                scrollbars "vertical"
                ysize 510

                vbox:
                    spacing 10

                    for provider in store.mtts.provider_manager._servers:
                        use maica_l2_subframe():
                            vbox:
                                spacing 4

                                $ _pid = provider.get("id")
                                $ _pname = provider.get("name") or ""
                                $ _desc = provider.get("description")
                                $ _model = provider.get("servingModel")
                                $ _portal = provider.get("portalPage")

                                text _pname:
                                    size 30

                                text _("ID: [_pid]"):
                                    size 15

                                if _desc:
                                    text _("说明: [_desc]"):
                                        size 15

                                if _model:
                                    text _("服务模型: [_model]"):
                                        size 15

                                if _portal:
                                    textbutton _("门户页面"):
                                        text_size 15
                                        action OpenURL(_portal)

                                $ _tts_url = provider.get("ttsInterface")
                                if not _tts_url:
                                    $ _tts_url = store.mtts.provider_manager._derive_tts_from_http(provider.get("httpInterface"))
                                $ _tts_url = store.mtts.provider_manager._ensure_trailing_slash(_tts_url)

                                if _tts_url:
                                    text _("TTS接口: [_tts_url]"):
                                        size 15

                                hbox:
                                    style_prefix "confirm"

                                    textbutton _("使用该节点"):
                                        action [Function(store.mtts.sync_provider_id, _pid), Hide("mtts_node_setting")]

                                    if persistent.mtts.get("provider_id") == _pid:
                                        text _("(当前)"):
                                            size 15
                                            yalign 0.5

            hbox:
                xpos 10
                style_prefix "confirm"

                textbutton _("刷新节点列表"):
                    action Function(store.mtts.provider_manager.get_provider)

                textbutton _("测试当前节点可用性"):
                    action Function(store.mtts.mtts.accessable)

                textbutton _("关闭"):
                    action Hide("mtts_node_setting")