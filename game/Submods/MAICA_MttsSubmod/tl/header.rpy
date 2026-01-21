# TODO: Translation updated at 2026-01-08 22:58

translate english strings:

    # game/Submods/MAICA_MTTSubmod/header.rpy:6
    old "MAICA-MTTS官方前端子模组"
    new "MAICA-MTTS Official Submod Frontend"

    # game/Submods/MAICA_MTTSubmod/header.rpy:30
    old "> 使用账号生成令牌 (独立模式)"
    new "> Generate token from account (Standalone)"

    # game/Submods/MAICA_MTTSubmod/header.rpy:33
    old "> 使用账号生成令牌 (Blessland)"
    new "> Generate token from account (Blessland)"

    # game/Submods/MAICA_MTTSubmod/header.rpy:35
    old "> MTTS参数与设置"
    new "> MTTS params and settings"

    # game/Submods/MAICA_MTTSubmod/header.rpy:76
    old "服务提供节点: [_node_name]"
    new "Current provider: [_node_name]"

    # game/Submods/MAICA_MTTSubmod/header.rpy:92
    old "当前用户: [_user_name]"
    new "Current user: [_user_name]"

    # game/Submods/MAICA_MTTSubmod/header.rpy:104
    old "启用MTTS: [persistent.mtts.get('enabled')]"
    new "Enable MTTS: [persistent.mtts.get('enabled')]"

    # game/Submods/MAICA_MTTSubmod/header.rpy:106
    old "启用以生成和播放TTS."
    new "Enable to generate and play TTS audio."

    # game/Submods/MAICA_MTTSubmod/header.rpy:111
    old "! MTTS未解锁, 启用不会生效"
    new "! MTTS not unlocked, enabling will not take effect"

    # game/Submods/MAICA_MTTSubmod/header.rpy:117
    old "启用以生成和播放TTS.\n! MTTS未解锁, 启用不会生效"
    new "Enable to generate and play TTS audio.\n! MTTS not unlocked, enabling will not take effect"

    # game/Submods/MAICA_MTTSubmod/header.rpy:120
    old "TTS的语音音量"
    new "TTS audio volume"

    # game/Submods/MAICA_MTTSubmod/header.rpy:121
    old "语音音量"
    new "TTS volume"

    # game/Submods/MAICA_MTTSubmod/header.rpy:128
    old "显示状态小窗: [persistent.mtts.get('ministathud')]"
    new "Show status HUD: [persistent.mtts.get('ministathud')]"

    # game/Submods/MAICA_MTTSubmod/header.rpy:130
    old "是否在游戏内显示MTTS状态小窗"
    new "Enable or disable MTTS status widget"

    # game/Submods/MAICA_MTTSubmod/header.rpy:135
    old "启用时显示道具: [persistent.mtts.get('acs_enabled')]"
    new "Display props when enabled: [persistent.mtts.get('acs_enabled')]"

    # game/Submods/MAICA_MTTSubmod/header.rpy:137
    old "是否在MTTS启用时展示麦克风.\n* MTTS耳机属于普通饰品, 请以常规方式穿戴或取下"
    new "Enable or disable MTTS microphone when using TTS.\n* MTTS headset not included since it's normal acs"

    # game/Submods/MAICA_MTTSubmod/header.rpy:163
    old "MTTS: 设置已保存"
    new "MTTS: Settings saved"

    # game/Submods/MAICA_MTTSubmod/header.rpy:169
    old "MTTS: 已放弃设置修改"
    new "MTTS: Settings discarded"

    # game/Submods/MAICA_MTTSubmod/header.rpy:175
    old "MTTS: 设置已重置"
    new "MTTS: Settings reset"

# TODO: Translation updated at 2026-01-10 00:36

translate english strings:

    # game/Submods/MAICA_MttsSubmod/header.rpy:75
    old "服务提供节点: [store.mtts.provider_manager.get_server_info().get('name', 'Unknown')]"
    new "Current provider: [store.mtts.provider_manager.get_server_info().get('name', 'Unknown')]"

# TODO: Translation updated at 2026-01-11 20:21

translate english strings:

    # game/Submods/MAICA_MttsSubmod/header.rpy:138
    old "MTTS本地缓存, 用以降低资源开销和响应延迟.\n* 若模型更换, 需要清除缓存以采用新的表现\n! 请{color=#FF0000}不要{/color}随意清除缓存, 这会产生大量额外开销"
    new "MTTS local cache to reduce resource consumption and latency.\n* Flush cache to apply new performance on model change\n! Do {color=#FF0000}NOT{/color} flush unless you know what you're doing"

    # game/Submods/MAICA_MttsSubmod/header.rpy:143
    old "当前缓存占用：[store.mtts.mtts_instance.cache.cache_size]MB"
    new "Current cache size: [store.mtts.mtts_instance.cache.cache_size]MB"

    # game/Submods/MAICA_MttsSubmod/header.rpy:150
    old "{color=#FF0000}清除缓存{/color}"
    new "{color=#FF0000}Flush cache{/color}"

# TODO: Translation updated at 2026-01-14 22:04

translate english strings:

    # game/Submods/MAICA_MttsSubmod/header.rpy:46
    old "> 警告: 未检测到MTTS库版本信息. 请从Release下载安装MTTS, 而不是源代码"
    new "> Warning: MTTS Libs version not found. Please install from Release, not source code"

    # game/Submods/MAICA_MttsSubmod/header.rpy:50
    old "> 警告: MTTS库版本[libv]与UI版本[uiv]不符. 请从Release完整地更新MTTS"
    new "> Warning: MTTS Libs v[libv] mismatch with UI v[uiv]. Please fully update from Release"

# TODO: Translation updated at 2026-01-20 16:32

translate english strings:

    # game/Submods/MAICA_MttsSubmod/header.rpy:168
    old "左侧屏幕空间避让: [persistent.mtts.get('drift_statshud_l')]"
    new "Compatible position left: [persistent.mtts.get('drift_statshud_l')]"

    # game/Submods/MAICA_MttsSubmod/header.rpy:170
    old "是否向Y轴中心偏移小窗以避免子模组冲突.\n* 在默认情况下, MTTS状态小窗显示在屏幕左下\n* 如果启用, MTTS小窗会更靠近屏幕左侧中心"
    new "Enable or disable offseting status HUD to avoid possible conflict with other submods.\n* MTTS status HUD occupies bottom left of screen space by default\n* MTTS status HUD will be closer to central Y on left side if enabled"

    # game/Submods/MAICA_MttsSubmod/header.rpy:174
    old "右侧屏幕空间避让: [persistent.mtts.get('drift_statshud_r')]"
    new "Compatible position right: [persistent.mtts.get('drift_statshud_r')]"

    # game/Submods/MAICA_MttsSubmod/header.rpy:176
    old "是否向Y轴中心偏移小窗以避免子模组冲突.\n* 在控制台显示(如MAICA)的情况下, MTTS状态小窗显示在屏幕右上\n* 如果启用, MTTS小窗会更靠近屏幕右侧中心"
    new "Enable or disable offseting status HUD to avoid possible conflict with other submods.\n* MTTS status HUD occupies top right of screen space if console (like MAICA) displayed\n* MTTS status HUD will be closer to central Y on right side if enabled"

