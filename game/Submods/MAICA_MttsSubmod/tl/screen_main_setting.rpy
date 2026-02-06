# TODO: Translation updated at 2026-02-05 20:28

translate english strings:

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:177
    old "使用自定义高级参数: [persistent.mtts.get('use_custom_model_config', False)]"
    new "Enable customized advanced parameters: [persistent.mtts.get('use_custom_model_config', False)]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:179
    old "高级参数可能大幅影响MTTS的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"
    new "Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"

# TODO: Translation updated at 2026-02-06 13:24

translate english strings:

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:187
    old "! 如果启用并调整了高级参数, 生成结果将无法被远程缓存, 每个请求都需要推理和传输\n! 这可能对服务器和你的数据流量造成大量额外开销, 请慎重考虑\n* 清除你的本地缓存以采用新的表现"
    new "! Active advanced parameters will disable remote cache, demanding per-request inference and transferring\n! This could cause massive extra cost on both server and client side, do consider carefully\n* Flush local cache to apply new performance"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:247
    old "清除缓存"
    new "Flush cache"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:249
    old "请{color=#FF0000}不要{/color}随意清除缓存, 这可能对服务器和你的数据流量造成大量额外开销"
    new "Do {color=#FF0000}NOT{/color} flush unless you know what you're doing, which could cause massive extra cost on both server and client side"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:251
    old "请确认你明白自己在做什么, 或者已得到有资质的技术人员的指导"
    new "Please confirm you understand what this means, or instructed by a MAICA technician"

