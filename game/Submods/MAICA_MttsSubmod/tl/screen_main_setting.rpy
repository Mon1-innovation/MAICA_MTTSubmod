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

# TODO: Translation updated at 2026-02-14 21:24

translate english strings:

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:126
    old "替换玩家名称: [persistent.mtts.get('replace_playername')]"
    new "Replace player name: [persistent.mtts.get('replace_playername')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:128
    old "是否在MTTS生成中替换玩家名称.\n! 该替换直接通过正则实现, 若你的游戏内名称容易在正常词句中出现, 则不要使用"
    new "Enable or disable player name replacement in speech generation.\n! Implemented directly through regex. Do not use if your in-game name commonly appears in unrelated context"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:133
    old "替换为: [persistent.mtts.get('playername_replacement') or 'Empty']"
    new "Replace to: [persistent.mtts.get('playername_replacement') or 'Empty']"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:135
    old "配置你希望使用的配音名称.\n* 设为空以不读名称, 但这更容易引发表现问题"
    new "Configure your spoken name.\n* Leave empty to not pronounce, but may lead to behaviour issue"

