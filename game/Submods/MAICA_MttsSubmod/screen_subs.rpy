default use_email = True

screen mtts_login():
    modal True
    zorder 92
    $ ok_action = [
                    Function(_mtts_submit_login),
                    Hide("mtts_login")
                    ]
    $ cancel_action = [Function(_mtts_clear), Hide("mtts_login")]

    use maica_setter_medium_frame(ok_action=ok_action, cancel_action=cancel_action):

        hbox:
            if use_email:
                textbutton _("Enter DCC account email"):
                    style "confirm_button"
                    action Show("mtts_login_input",message = _("Please enter DCC account email"),returnto = "_maica_LoginEmail")
            else:
                textbutton _("Enter DCC account username"):
                    style "confirm_button"
                    action Show("mtts_login_input",message = _("Please enter DCC account username") ,returnto = "_maica_LoginAcc")

        hbox:
            style_prefix "maica_check"
            if use_email:
                textbutton _("> Switch to username login"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_mtts_clear)]
                    selected False

            else:
                textbutton _("> Switch to email login"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_mtts_clear)]
                    selected False

        hbox:
            textbutton _("Enter password"):
                style "confirm_button"
                action Show("mtts_login_input",message = _("Please enter password"),returnto = "_maica_LoginPw")
        hbox:
            text ""

        hbox:
            style_prefix "small_expl"
            text _("※ By using MAICA-MTTS Synbrace, you agree to "):
                size 15
            textbutton _("{u}MAICA Terms of Service{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0

        hbox:
            style_prefix "small_expl"
            text _("※ Don't have a DCC account? "):
                size 15
            textbutton _("{u}Register one{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0


screen mtts_login_input(message, returnto, ok_action = Hide("mtts_login_input")):
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 92

    use maica_setter_medium_frame(message, ok_action):
        input default "" value VariableInputValue(returnto) length 64


screen mtts_playername_replace_input():
    modal True
    zorder 92

    use maica_setter_small_frame(_("Enter your spoken name"), ok_action=[Hide("mtts_playername_replace_input")]):
        input default persistent.mtts.get("playername_replacement", "") value DictInputValue(persistent.mtts, "playername_replacement") length 30


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
                        text renpy.substitute(_("Description: ")) + provider.get('description', 'Device not provided')
                    hbox:
                        text renpy.substitute(_("Current model: ")) + provider.get('servingModel', 'No model provided')


                hbox:
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Use this provider"):
                            action [
                                # Function(set_provider, provider.get('id')),
                                Function(store.mtts.sync_provider_id, provider.get('id')),
                                Hide("mtts_node_setting")
                            ]
                            selected persistent.mtts["provider_id"] == provider.get('id')
                    hbox:
                        style_prefix "maica_check"
                        textbutton renpy.substitute(_("> Open website")) + "(" + provider.get('portalPage') + ")":
                            action OpenURL(provider.get('portalPage'))

                    if provider.get("isOfficial", False):
                        hbox:
                            style_prefix "maica_check_nohover"
                            textbutton _(" <Official service>")
                        
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Refresh provider list"):
                action Function(store.mtts.provider_manager.get_provider)

            textbutton _("Close"):
                action Hide("mtts_node_setting")
            
            textbutton _("Test current provider availability"):
                action Function(store.mtts.mtts_instance.accessable)

screen mtts_support():

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("Donate to MAICA"), ok_action=Hide("mtts_support")):
        hbox:
            text _("First of all, thank you for considering a donation.\nWe are very unlikely to recover the costs of running MAICA, but please do not feel pressured."):
                size 20
        hbox:
            style_prefix "maica_check_nohover"
            text _("Please note that donating to MAICA provides no privileges, except for a name on the forum donation page and a donor badge."):
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


