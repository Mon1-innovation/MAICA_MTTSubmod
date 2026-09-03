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
                    action Show("mtts_login_input",message = _("Enter DCC account email{#maica_login_prompt}"),returnto = "_maica_LoginEmail")
            else:
                textbutton _("Enter DCC account username"):
                    style "confirm_button"
                    action Show("mtts_login_input",message = _("Enter DCC account username{#maica_login_prompt}") ,returnto = "_maica_LoginAcc")

        hbox:
            style_prefix "small_expl"
            if use_email:
                textbutton _("> Use username instead"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_mtts_clear)]
                    selected False

            else:
                textbutton _("> Use email instead"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_mtts_clear)]
                    selected False

        hbox:
            textbutton _("Enter password"):
                style "confirm_button"
                action Show("mtts_login_input",message = _("Enter password{#maica_login_prompt}"),returnto = "_maica_LoginPw")
        hbox:
            text ""

        hbox:
            style_prefix "small_expl"
            text _("※ By using MAICA-MTTS Synbrace, you agree to "):
                size 15
            textbutton _("{u}MAICA ToS{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0

        hbox:
            style_prefix "small_expl"
            text _("※ No DCC account yet? "):
                size 15
            textbutton _("{u}Register now{/u}"):
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
                $ provider_id = provider.get("id")
                $ provider_name = provider.get("name") or "Unknown"
                $ provider_description = provider.get("description") or "Device not provided"
                $ provider_model = provider.get("servingModel") or "No model provided"
                $ provider_url = provider.get("portalPage") or ""
                use maica_l2_subframe():
                    text mtts_escape_display_text(
                        "{} | {}".format(provider_id, provider_name)
                    )

                    hbox:
                        text mtts_escape_display_text(
                            renpy.substitute(_("Intro: ")) +
                            u"{}".format(provider_description)
                        )
                    hbox:
                        text mtts_escape_display_text(
                            renpy.substitute(_("Model: ")) +
                            u"{}".format(provider_model)
                        )


                hbox:
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("Use this server"):
                            action [
                                # Function(set_provider, provider.get('id')),
                                Function(store.mtts.sync_provider_id, provider.get('id')),
                                Hide("mtts_node_setting")
                            ]
                            selected persistent.mtts["provider_id"] == provider.get('id')
                    hbox:
                        style_prefix "maica_check"
                        textbutton mtts_escape_display_text(
                            renpy.substitute(_("> Go to portal page")) +
                            " (" + u"{}".format(provider_url) + ")"
                        ):
                            action OpenURL(provider_url)

                    if provider.get("isOfficial", False):
                        hbox:
                            style_prefix "maica_check_nohover"
                            textbutton _(" <Official>")
                        
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Refresh servers list"):
                action Function(store.mtts.provider_manager.get_provider)

            textbutton _("Close"):
                action Hide("mtts_node_setting")
            
            textbutton _("Test current node avaliability"):
                action Function(store.mtts.mtts_instance.accessable)

screen mtts_support():

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("Donate to MAICA"), ok_action=Hide("mtts_support")):
        hbox:
            text _("We're grateful for your being willing to donate.\nThe donate will likely never cover our cost, but that's okay anyway."):
                size 20
        hbox:
            style_prefix "maica_check_nohover"
            text _("Please note that donating to MAICA doesn't give you any actual privilege. It's simply donation."):
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


