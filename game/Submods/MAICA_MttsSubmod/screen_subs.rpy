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


screen mtts_advance_setting():
    $ _tooltip = store._tooltip
    python:
        def reset_to_default():
            pass
            # for item in store.maica.maica_instance.default_setting:
            #     if item == 'seed':
            #         store.maica.maica_instance.default_setting[item] = 0
            #     if item in persistent.maica_advanced_setting:
            #         persistent.maica_advanced_setting[item] = store.maica.maica_instance.default_setting[item]
            #         persistent.maica_advanced_setting_status[item] = False

    modal True
    zorder 92
    
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            # hbox:
            #     style_prefix "maica_check"
            #     text _("关于这些参数的详细解释, 参见 "):
            #         size 20
            #     textbutton _("{u}MAICA 官方文档{/u}"):
            #         action OpenURL("https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt")
            #         text_size 20
            #     text _(" 和 "):
            #         size 20
            #     textbutton _("{u}OpenAI 中文文档{/u}"):
            #         action OpenURL("https://www.openaidoc.com.cn/api-reference/chat" if config.language == "chinese" else "https://platform.openai.com/docs/api-reference/completions/create#completions_create")
            #         text_size 20
            # hbox:
            #     text _("{size=-10}注意: 只有被勾选的高级参数才会被使用, 未勾选的参数将使用服务端默认设置")
            # hbox:
            #     if not persistent.maica_setting_dict.get('use_custom_model_config'):
            #         text _("{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!")

            use divider_small(_("超参数"))
            $ sdict = "mtts_advanced_setting"

            # hbox:
            #     spacing 5
            #     textbutton "top_p":
            #         action ToggleDict(persistent.maica_advanced_setting_status, "top_p")
            #         hovered SetField(_tooltip, "value", _("token权重过滤范围. 非常不建议动这个"))
            #         unhovered SetField(_tooltip, "value", _tooltip.default)
                
            #     if persistent.maica_advanced_setting_status.get("top_p", False):
            #         use prog_bar("top_p", 250, _("token权重过滤范围. 非常不建议动这个"), "top_p", 0.1, 1.0, sdict=sdict)

            use divider_small(_("高级设置"))

            # hbox:
            #     spacing 5
            #     textbutton "tnd_aggressive":
            #         action ToggleDict(persistent.maica_advanced_setting_status, "tnd_aggressive")
            #         hovered SetField(_tooltip, "value", _("即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"))
            #         unhovered SetField(_tooltip, "value", _tooltip.default)
            #     if persistent.maica_advanced_setting_status.get("tnd_aggressive", False):
            #         use num_bar("tnd_aggressive", 200, _("即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"), "tnd_aggressive", 0, 3, sdict=sdict)


        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("保存设置"):
                action [
                    Hide("mtts_advance_setting"),
                    Function(renpy.notify, _("MTTS: 已保存高级设置"))
                ]
            textbutton _("重置设置"):
                action [
                    Function(reset_to_default),
                    Hide("mtts_advance_setting"),
                    Function(renpy.notify, _("MTTS: 已重置高级设置") if store.mtts.mtts_instance.is_accessable() else _("MTTS: 已重置高级设置(缺省值)"))
                ]