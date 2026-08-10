
init python:
    persistent.mtts_advance_params = {}
    def mtts_apply_advanced_setting():
        """Apply enabled settings to MTTS instance"""
        # Backup current state before applying
        persistent.mtts_advanced_setting_backup = persistent.mtts_advanced_setting.copy()
        persistent.mtts_advanced_setting_status_backup = persistent.mtts_advanced_setting_status.copy()

        # Build params dict with only enabled items
        persistent.mtts_advance_params = {}
        if persistent.mtts.get('use_custom_model_config', False):
            for key, is_enabled in persistent.mtts_advanced_setting_status.items():
                if is_enabled and key in persistent.mtts_advanced_setting:
                    persistent.mtts_advance_params[key] = persistent.mtts_advanced_setting[key]
        
        

    def mtts_discard_advanced_setting():
        """Restore settings from backup (created when screen was opened)"""
        # Restore from backup
        if persistent.mtts_advanced_setting_backup:
            persistent.mtts_advanced_setting = persistent.mtts_advanced_setting_backup.copy()
        if persistent.mtts_advanced_setting_status_backup:
            persistent.mtts_advanced_setting_status = persistent.mtts_advanced_setting_status_backup.copy()

    def mtts_reset_advanced_setting():
        """Reset all settings to server defaults"""
        persistent.mtts_advanced_setting = store.mtts_default_advanced_setting.copy()
        persistent.mtts_advanced_setting.update(store.mtts.mtts_instance.default_settings)
        # Reset all status to False
        persistent.mtts_advanced_setting_status = {
            key: False for key in persistent.mtts_advanced_setting.keys()
        }


screen mtts_advance_setting():
    $ _tooltip = store._tooltip

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            hbox:
                style_prefix "maica_check"
                text _("For detailed explanations of these parameters, see "):
                    size 20
                textbutton _("{u}MTTS official documents{/u}"):
                    action OpenURL("https://github.com/Mon1-innovation/MAICA_MTTS/blob/main/document/API%20Document.txt")
                    text_size 20
                text _(" and "):
                    size 20
                textbutton _("{u}GPT-SoVITS documents{/u}"):
                    action OpenURL("https://github.com/RVC-Boss/GPT-SoVITS/blob/main/api_v2.py")
                    text_size 20
            hbox:
                text _("{size=-10}Only checked advanced parameters will be used; unchecked parameters use server defaults")
            hbox:
                if not persistent.mtts.get('use_custom_model_config'):
                    text _("{size=-10}You have not enabled 'Use advanced parameters'; none of the settings on this page will take effect!")

            # Basic Parameters (基础参数)
            #use divider_small(_("基础参数"))

            ## parallel_infer - Boolean toggle
            #hbox:
            #    spacing 10
            #    xpos 30
            #    style_prefix "generic_fancy_check"
            #    textbutton _("并行推理"):
            #        action ToggleDict(persistent.mtts_advanced_setting_status, "parallel_infer")
            #        hovered SetField(_tooltip, "value", _("启用并行推理以提高性能"))
            #        unhovered SetField(_tooltip, "value", _tooltip.default)

            # Sampling Parameters (采样参数)
            use divider_small(_("Basic performance"))

            # text_split_method - Dropdown selection
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "text_split_method":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "text_split_method")
                    hovered SetField(_tooltip, "value", _("Text pre-split method, normally only affects long text"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("text_split_method", False):
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("Change: currently [persistent.mtts_advanced_setting.get('text_split_method', 'cut2')]"):
                            action Show("mtts_text_split_selector")
                            hovered SetField(_tooltip, "value", _("Text pre-split method, normally only affects long text"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            # speed_factor - Float slider 0.5-2
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "speed_factor":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "speed_factor")
                    hovered SetField(_tooltip, "value", _("Speed factor, affects speaking speed in inference phrase.\n* Is not linear correlative with actual speaking speed"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("speed_factor", False):
                    use prog_bar("speed_factor", 400, _("Speed factor, affects speaking speed in inference phrase.\n* Is not linear correlative with actual speaking speed"), "speed_factor", 0.5, 2.0, sdict="mtts_advanced_setting")

            use divider_small(_("Hyperparameters"))

            # temperature - Float slider 0-2
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "temperature":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "temperature")
                    hovered SetField(_tooltip, "value", _("Token sampling randomness. Higher values make the model output less like the generally optimal result"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("temperature", False):
                    use prog_bar("temperature", 400, _("Token sampling randomness. Higher values make the model output less like the generally optimal result"), "temperature", 0.0, 2.0, sdict="mtts_advanced_setting")

            # top_k - Integer slider 1-20
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "top_k":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "top_k")
                    hovered SetField(_tooltip, "value", _("Token weight filter count. Seriously do not touch this"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("top_k", False):
                    use prog_bar("top_k", 400, _("Token weight filter count. Seriously do not touch this"), "top_k", 1, 20, sdict="mtts_advanced_setting")

            # top_p - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "top_p":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "top_p")
                    hovered SetField(_tooltip, "value", _("Token weight filter range. Seriously do not touch this"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("top_p", False):
                    use prog_bar("top_p", 400, _("Token weight filter range. Seriously do not touch this"), "top_p", 0.0, 1.0, sdict="mtts_advanced_setting")

            # repetition_penalty - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "repetition_penalty":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "repetition_penalty")
                    hovered SetField(_tooltip, "value", _("Token repetition penalty. Higher this value, less likely tokens appear repeatedly"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("repetition_penalty", False):
                    use prog_bar("repetition_penalty", 400, _("Token repetition penalty. Higher this value, less likely tokens appear repeatedly"), "repetition_penalty", 0.0, 1.0, sdict="mtts_advanced_setting")

            # seed - Integer input
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "seed":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "seed")
                    hovered SetField(_tooltip, "value", _("Generation seed. Usually has little and random impact"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("seed", False):
                    use num_bar("seed", 200, _("Generation seed. Usually has little and random impact"), "seed", -2147483648, 2147483647, sdict="mtts_advanced_setting")


        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("Save settings"):
                action [
                    Function(mtts_apply_advanced_setting),
                    Hide("mtts_advance_setting"),
                    Function(renpy.notify, _("MTTS: Advanced settings saved"))
                ]
            textbutton _("Reset settings"):
                action [
                    Function(mtts_reset_advanced_setting),
                    Hide("mtts_advance_setting"),
                    Function(renpy.notify, _("MTTS: Advanced settings reset"))
                ]
            textbutton _("Cancel"):
                action [
                    Function(mtts_discard_advanced_setting),
                    Hide("mtts_advance_setting")
                ]

    if _tooltip.value:
        frame:
            xalign 0.5 yalign 1.0
            yoffset -25
            text _tooltip.value:
                style "main_menu_version"

screen mtts_text_split_selector():
    $ _tooltip = store._tooltip
    modal True
    zorder 95

    use maica_setter_small_frame(title=_("Choose text pre-split method"), ok_action=Hide("mtts_text_split_selector")):
        vbox:
            spacing 5
            style_prefix "generic_fancy_check"

            # for method in ["cut0", "cut1", "cut2", "cut3", "cut4", "cut5"]:
            #     textbutton method:
            #         action [
            #             SetDict(persistent.mtts_advanced_setting, "text_split_method", method),
            #             Hide("mtts_text_split_selector")
            #         ]

            textbutton "cut0":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut0"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("No pre-splitting at all"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut1":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut1"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("Split every 4 complete sentences"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut2":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut2"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("Split complete sentences when reaches 50 characters"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut3":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut3"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("Split only respecting em periods"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut4":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut4"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("Split only respecting en periods"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut5":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut5"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("Automatically respect all symbols.\n* Usually does not perform well in actual usage"))
                unhovered SetField(_tooltip, "value", _tooltip.default)
