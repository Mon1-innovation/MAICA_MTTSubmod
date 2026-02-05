
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
        persistent.mtts_advanced_setting = {
            "parallel_infer": False,
            "repetition_penalty": 0.5,
            "seed": 0,
            "speed_factor": 1.0,
            "temperature": 0.8,
            "text_split_method": "cut2",
            "top_k": 15,
            "top_p": 0.9,
        }
        persistent.mtts_advanced_setting.update(defaults)
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
            use divider_small(_("MTTS高级参数"))

            hbox:
                style_prefix "maica_check_nohover"
                text _("注意: 只有被勾选的参数才会被使用, 未勾选的参数将使用服务端默认设置"):
                    size 14

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
            use divider_small(_("采样参数"))

            # temperature - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("temperature"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "temperature")
                    hovered SetField(_tooltip, "value", _("温度参数，范围0-1。值越小越稳定"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("temperature", False):
                    use prog_bar(_("temperature"), 400, _("温度参数，范围0-1"), "temperature", 0.0, 1.0, sdict="mtts_advanced_setting")

            # top_k - Integer slider 1-20
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("top_k"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "top_k")
                    hovered SetField(_tooltip, "value", _("Top-K采样，范围1-20"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("top_k", False):
                    use prog_bar(_("top_k"), 400, _("Top-K采样，范围1-20"), "top_k", 1, 20, sdict="mtts_advanced_setting")

            # top_p - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("top_p"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "top_p")
                    hovered SetField(_tooltip, "value", _("Top-P采样，范围0-1"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("top_p", False):
                    use prog_bar(_("top_p"), 400, _("Top-P采样，范围0-1"), "top_p", 0.0, 1.0, sdict="mtts_advanced_setting")

            # Text Processing (文本处理)
            use divider_small(_("文本处理"))

            # text_split_method - Dropdown selection
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("text_split_method"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "text_split_method")
                    hovered SetField(_tooltip, "value", _("文本分割方法，选择cut0-cut5"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("text_split_method", False):
                    style_prefix "generic_fancy_check"
                    textbutton _("当前为 [persistent.mtts_advanced_setting.get('text_split_method', 'cut2')]"):
                        action Show("mtts_text_split_selector")
                        hovered SetField(_tooltip, "value", _("点击选择文本分割方法"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)

            # repetition_penalty - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("repetition_penalty"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "repetition_penalty")
                    hovered SetField(_tooltip, "value", _("重复惩罚系数，范围0-1。值越小越容易重复"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("repetition_penalty", False):
                    use prog_bar(_("repetition_penalty"), 400, _("重复惩罚系数，范围0-1"), "repetition_penalty", 0.0, 1.0, sdict="mtts_advanced_setting")
            # Performance Tuning (性能调整)
            use divider_small(_("性能调整"))

            # speed_factor - Float slider 0.5-2
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("speed_factor"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "speed_factor")
                    hovered SetField(_tooltip, "value", _("语速调整，范围0.5-2倍"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("speed_factor", False):
                    use prog_bar(_("speed_factor"), 400, _("语速调整，范围0.5-2倍"), "speed_factor", 0.5, 2.0, sdict="mtts_advanced_setting")

            # seed - Integer input
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton _("seed"):
                    action ToggleDict(persistent.mtts_advanced_setting_status, "seed")
                    hovered SetField(_tooltip, "value", _("随机种子，用于复现结果"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("seed", False):
                    use num_bar("seed", 200, _("生成种子. 一般而言影响很小且随机"), "seed", -2147483648, 2147483647, sdict="mtts_advanced_setting")


        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("保存设置"):
                action [
                    Function(mtts_apply_advanced_setting),
                    Hide("mtts_advance_setting"),
                    Function(renpy.notify, _("MTTS: 已保存高级设置"))
                ]
            textbutton _("重置设置"):
                action [
                    Function(mtts_reset_advanced_setting),
                    Hide("mtts_advance_setting"),
                    Function(renpy.notify, _("MTTS: 已重置高级设置"))
                ]
            textbutton _("取消"):
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
    modal True
    zorder 95

    use maica_setter_small_frame(title=_("选择文本分割方法"), ok_action=Hide("mtts_text_split_selector"), cancel_action=Hide("mtts_text_split_selector")):
        vbox:
            spacing 5
            style_prefix "generic_fancy_check"

            for method in ["cut0", "cut1", "cut2", "cut3", "cut4", "cut5"]:
                textbutton method:
                    action [
                        SetDict(persistent.mtts_advanced_setting, "text_split_method", method),
                        Hide("mtts_text_split_selector")
                    ]