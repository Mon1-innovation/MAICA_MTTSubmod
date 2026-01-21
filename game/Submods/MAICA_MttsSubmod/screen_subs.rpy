default use_email = True

screen mtts_login():
    modal True
    zorder 92
    $ ok_action = [
                    Function(store.mtts.mtts_instance._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
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
            text _("※ 使用MAICA-MTTS Synbrace, 即认为你同意 "):
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
    $ _tooltip = store._tooltip
    # python:
    #     def set_provider(id):
    #         persistent.maica_setting_dict["provider_id"] = id

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            for provider in store.mtts.provider_manager._servers:
                use maica_l2_subframe():
                    text str(provider.get('id')) + ' | ' + provider.get('name')
                    

                    hbox:
                        text renpy.substitute(_("说明: ")) + provider.get('description', 'Device not provided')
                    hbox:
                        text renpy.substitute(_("当前模型: ")) + provider.get('servingModel', 'No model provided')


                hbox:
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("使用该节点"):
                            action [
                                # Function(set_provider, provider.get('id')),
                                Function(store.mtts.sync_provider_id, provider.get('id')),
                                Hide("mtts_node_setting")
                            ]
                            selected persistent.mtts["provider_id"] == provider.get('id')
                    hbox:
                        style_prefix "maica_check"
                        textbutton renpy.substitute(_("> 打开官网")) + "(" + provider.get('portalPage') + ")":
                            action OpenURL(provider.get('portalPage'))

                    if provider.get("isOfficial", False):
                        hbox:
                            style_prefix "maica_check_nohover"
                            textbutton _(" <官方服务>")
                        
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("刷新节点列表"):
                action Function(store.mtts.provider_manager.get_provider)

            textbutton _("关闭"):
                action Hide("mtts_node_setting")
            
            textbutton _("测试当前节点可用性"):
                action Function(store.mtts.mtts_instance.accessable)

screen mtts_support():

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("向 MAICA 捐赠"), ok_action=Hide("mtts_support")):
        hbox:
            text _("首先很感谢你有心捐赠.\n我们收到的捐赠基本上不可能回本, 但你不必有任何压力."):
                size 20
        hbox:
            style_prefix "maica_check_nohover"
            text _("请注意, 向MAICA捐赠不会提供任何特权, 除了论坛捐赠页名单和捐赠徽章."):
                size 15
            text "\n":
                size 15
        hbox:
            xalign 0.5
            if config.language == 'chinese':
                imagebutton:
                    idle "mod_assets/mtts_img/aifadian.png"
                    insensitive "mod_assets/mtts_img/aifadian.png"
                    hover "mod_assets/mtts_img/aifadian.png"
                    selected_idle "mod_assets/mtts_img/aifadian.png"
                    selected_hover "mod_assets/mtts_img/aifadian.png"
                    action OpenURL("https://forum.monika.love/iframe/redir_donation.php?lang=zh")
            else:
                imagebutton:
                    idle "mod_assets/mtts_img/unifans.png"
                    insensitive "mod_assets/mtts_img/unifans.png"
                    hover "mod_assets/mtts_img/unifans.png"
                    selected_idle "mod_assets/mtts_img/unifans.png"
                    selected_hover "mod_assets/mtts_img/unifans.png"
                    action OpenURL("https://forum.monika.love/iframe/redir_donation.php?lang=en")