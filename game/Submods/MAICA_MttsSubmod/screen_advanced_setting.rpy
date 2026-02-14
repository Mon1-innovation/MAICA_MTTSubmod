
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
                text _("关于这些参数的详细解释, 参见 "):
                    size 20
                textbutton _("{u}MTTS 官方文档{/u}"):
                    action OpenURL("https://github.com/Mon1-innovation/MAICA_MTTS/blob/main/document/API%20Document.txt")
                    text_size 20
                text _(" 和 "):
                    size 20
                textbutton _("{u}GPT-SoVITS 文档{/u}"):
                    action OpenURL("https://github.com/RVC-Boss/GPT-SoVITS/blob/main/api_v2.py")
                    text_size 20
            hbox:
                text _("{size=-10}注意: 只有被勾选的高级参数才会被使用, 未勾选的参数将使用服务端默认设置")
            hbox:
                if not persistent.mtts.get('use_custom_model_config'):
                    text _("{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!")

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
            use divider_small(_("基础表现"))

            # text_split_method - Dropdown selection
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "text_split_method":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "text_split_method")
                    hovered SetField(_tooltip, "value", _("文本预切分模式, 一般只影响较长文本"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("text_split_method", False):
                    hbox:
                        style_prefix "maica_check"
                        textbutton _("切换: 当前为 [persistent.mtts_advanced_setting.get('text_split_method', 'cut2')]"):
                            action Show("mtts_text_split_selector")
                            hovered SetField(_tooltip, "value", _("文本预切分模式, 一般只影响较长文本"))
                            unhovered SetField(_tooltip, "value", _tooltip.default)

            # speed_factor - Float slider 0.5-2
            hbox:
                spacing 10
                xpos 0
                style_prefix "generic_fancy_check"
                textbutton "speed_factor":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "speed_factor")
                    hovered SetField(_tooltip, "value", _("速度因子, 在推理过程中控制生成的语速.\n* 该数值与实际语速并非线性相关"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("speed_factor", False):
                    use prog_bar("speed_factor", 400, _("速度因子, 在推理过程中控制生成的语速.\n* 该数值与实际语速并非线性相关"), "speed_factor", 0.5, 2.0, sdict="mtts_advanced_setting")

            use divider_small(_("超参数"))

            # temperature - Float slider 0-2
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "temperature":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "temperature")
                    hovered SetField(_tooltip, "value", _("token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("temperature", False):
                    use prog_bar("temperature", 400, _("token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"), "temperature", 0.0, 2.0, sdict="mtts_advanced_setting")

            # top_k - Integer slider 1-20
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "top_k":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "top_k")
                    hovered SetField(_tooltip, "value", _("token权重过滤数量. 非常不建议动这个"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("top_k", False):
                    use prog_bar("top_k", 400, _("token权重过滤数量. 非常不建议动这个"), "top_k", 1, 20, sdict="mtts_advanced_setting")

            # top_p - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "top_p":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "top_p")
                    hovered SetField(_tooltip, "value", _("token权重过滤范围. 非常不建议动这个"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("top_p", False):
                    use prog_bar("top_p", 400, _("token权重过滤范围. 非常不建议动这个"), "top_p", 0.0, 1.0, sdict="mtts_advanced_setting")

            # repetition_penalty - Float slider 0-1
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "repetition_penalty":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "repetition_penalty")
                    hovered SetField(_tooltip, "value", _("token重复惩罚. 数值越高, token越不可能反复出现"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.mtts_advanced_setting_status.get("repetition_penalty", False):
                    use prog_bar("repetition_penalty", 400, _("token重复惩罚. 数值越高, token越不可能反复出现"), "repetition_penalty", 0.0, 1.0, sdict="mtts_advanced_setting")

            # seed - Integer input
            hbox:
                spacing 10
                xpos 30
                style_prefix "generic_fancy_check"
                textbutton "seed":
                    action ToggleDict(persistent.mtts_advanced_setting_status, "seed")
                    hovered SetField(_tooltip, "value", _("生成种子. 一般而言影响很小且随机"))
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
    $ _tooltip = store._tooltip
    modal True
    zorder 95

    use maica_setter_small_frame(title=_("选择文本预切分模式"), ok_action=Hide("mtts_text_split_selector")):
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
                hovered SetField(_tooltip, "value", _("完全不进行预切分"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut1":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut1"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("每4个完整句子切分一次"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut2":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut2"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("每满50字的完整句子切分一次"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut3":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut3"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("只按中文句号进行切分"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut4":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut4"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("只按英文句号进行切分"))
                unhovered SetField(_tooltip, "value", _tooltip.default)

            textbutton "cut5":
                action [
                    SetDict(persistent.mtts_advanced_setting, "text_split_method", "cut5"),
                    Hide("mtts_text_split_selector")
                ]
                hovered SetField(_tooltip, "value", _("按所有标点智能切分.\n* 实战表现往往并不好"))
                unhovered SetField(_tooltip, "value", _tooltip.default)