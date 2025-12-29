default use_email = True

screen mtts_login():
    modal True
    zorder 92
    python:
        def none_gentoken(*args, **kwargs):
            store.mtts.mtts._gen_token(*args, **kwargs)
    $ ok_action = [
                    Function(none_gentoken, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
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
