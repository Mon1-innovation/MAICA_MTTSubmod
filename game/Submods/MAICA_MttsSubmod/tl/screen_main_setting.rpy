
translate chinese strings:

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:64
    old "Connection and security"
    new "连接与安全"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:68
    old "Current provider: [provider_name]"
    new "服务提供节点: [provider_name]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:70
    old "Set server node"
    new "设置服务器节点"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:74
    old "Not logged in"
    new "未登录"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:75
    old "Current user: [user_disp]"
    new "当前用户: [user_disp]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:77
    old "To change or log out of your account, log out from the Submods screen.\n* To change account information or password, visit the registration website"
    new "如需更换或退出账号, 请在Submods界面退出登录.\n* 要修改账号信息或密码, 请前往注册网站"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:82
    old "Behavior and performance"
    new "行为与表现"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:87
    old "Enable MTTS: [persistent.mtts.get('enabled')]"
    new "启用MTTS: [persistent.mtts.get('enabled')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:89
    old "Enable to generate and play TTS audio."
    new "启用以生成和播放TTS."

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:95
    old "! MTTS not unlocked, enabling will not take effect"
    new "! MTTS未解锁, 启用不会生效"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:101
    old "Enable to generate and play TTS audio.\n! MTTS not unlocked, enabling will not take effect"
    new "启用以生成和播放TTS.\n! MTTS未解锁, 启用不会生效"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:104
    old "TTS audio volume"
    new "TTS的语音音量"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:105
    old "TTS volume"
    new "语音音量"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:107
    old "Skip current sentence if response time exceeds.\n* Do not set this too low"
    new "若超过指定时间仍未收到响应, 则跳过本句语音.\n* 请不要设置得太短"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:108
    old "Generation timeout (s)"
    new "等待限制(秒)"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:111
    old "Tools and features"
    new "工具与功能"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:115
    old "Display props when enabled: [persistent.mtts.get('acs_enabled')]"
    new "启用时显示道具: [persistent.mtts.get('acs_enabled')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:117
    old "Enable or disable MTTS microphone when using TTS.\n* MTTS headset not included since it's normal acs"
    new "是否在MTTS启用时展示麦克风.\n* MTTS耳机属于普通饰品, 请以常规方式穿戴或取下"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:131
    old "Replace player name: [persistent.mtts.get('replace_playername')]"
    new "替换玩家名称: [persistent.mtts.get('replace_playername')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:133
    old "Enable or disable player name replacement in speech generation.\n! Implemented directly through regex. Do not use if your in-game name commonly appears in unrelated context"
    new "是否在MTTS生成中替换玩家名称.\n! 该替换直接通过正则实现, 若你的游戏内名称容易在正常词句中出现, 则不要使用"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:138
    old "Replace to: [replacement]"
    new "替换为: [replacement]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:140
    old "Configure your spoken name.\n* Leave empty to not pronounce, but may lead to behaviour issue"
    new "配置你希望使用的配音名称.\n* 设为空以不读名称, 但这更容易引发表现问题"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:153
    old "Show status HUD: [persistent.mtts.get('ministathud')]"
    new "显示状态小窗: [persistent.mtts.get('ministathud')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:155
    old "Enable or disable MTTS status widget"
    new "是否在游戏内显示MTTS状态小窗"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:159
    old "Compatible position left: [persistent.mtts.get('drift_statshud_l')]"
    new "左侧屏幕空间避让: [persistent.mtts.get('drift_statshud_l')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:161
    old "Enable or disable offseting status HUD to avoid possible conflict with other submods.\n* MTTS status HUD occupies bottom left of screen space by default\n* MTTS status HUD will be closer to central Y on left side if enabled"
    new "是否向Y轴中心偏移小窗以避免子模组冲突.\n* 在默认情况下, MTTS状态小窗显示在屏幕左下\n* 如果启用, MTTS小窗会更靠近屏幕左侧中心"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:165
    old "Compatible position right: [persistent.mtts.get('drift_statshud_r')]"
    new "右侧屏幕空间避让: [persistent.mtts.get('drift_statshud_r')]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:167
    old "Enable or disable offseting status HUD to avoid possible conflict with other submods.\n* MTTS status HUD occupies top right of screen space if console (like MAICA) displayed\n* MTTS status HUD will be closer to central Y on right side if enabled"
    new "是否向Y轴中心偏移小窗以避免子模组冲突.\n* 在控制台显示(如MAICA)的情况下, MTTS状态小窗显示在屏幕右上\n* 如果启用, MTTS小窗会更靠近屏幕右侧中心"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:178
    old "MTTS local cache to reduce resource consumption and latency.\n* Flush cache to apply new performance on model change\n! Do {color=#FF0000}NOT{/color} flush unless you know what you're doing"
    new "MTTS本地缓存, 用以降低资源开销和响应延迟.\n* 若模型更换, 需要清除缓存以采用新的表现\n! 请{color=#FF0000}不要{/color}随意清除缓存, 这会产生大量额外开销"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:183
    old "Current cache size: [store.mtts.mtts_instance.cache.cache_size]MB"
    new "当前缓存占用：[store.mtts.mtts_instance.cache.cache_size]MB"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:190
    old "{color=#FF0000}Flush cache{/color}"
    new "{color=#FF0000}清除缓存{/color}"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:205
    old "Enable customized advanced parameters: [persistent.mtts.get('use_custom_model_config', False)]"
    new "使用自定义高级参数: [persistent.mtts.get('use_custom_model_config', False)]"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:207
    old "Advanced parameters could significantly affect the model's performance.\n* The default is already the best field-tested config, so it's not suggested to enable this"
    new "高级参数可能大幅影响MTTS的表现.\n* 默认的高级参数已经是实践中的普遍最优配置, 不建议启用"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:212
    old "Set advanced parameters"
    new "设置高级参数"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:216
    old "! Active advanced parameters will disable remote cache, demanding per-request inference and transferring\n! This could cause massive extra cost on both server and client side, do consider carefully\n* Flush local cache to apply new performance"
    new "! 如果启用并调整了高级参数, 生成结果将无法被远程缓存, 每个请求都需要推理和传输\n! 这可能对服务器和你的数据流量造成大量额外开销, 请慎重考虑\n* 清除你的本地缓存以采用新的表现"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:228
    old "Expand performance monitor"
    new "展开性能监控"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:228
    old "Collapse performance monitor"
    new "收起性能监控"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:230
    old "Show/hide server performance metrics"
    new "显示/收起服务器的性能状态指标"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:246
    old "MTTS: Settings saved"
    new "MTTS: 设置已保存"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:251
    old "Discard changes"
    new "放弃修改"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:252
    old "MTTS: Settings discarded"
    new "MTTS: 已放弃设置修改"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:258
    old "MTTS: Settings reset"
    new "MTTS: 设置已重置"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:277
    old "Flush cache"
    new "清除缓存"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:279
    old "Do {color=#FF0000}NOT{/color} flush unless you know what you're doing, which could cause massive extra cost on both server and client side"
    new "请{color=#FF0000}不要{/color}随意清除缓存, 这可能对服务器和你的数据流量造成大量额外开销"

    # game/Submods/MAICA_MttsSubmod/screen_main_setting.rpy:282
    old "Please confirm you understand what this means, or instructed by a MAICA technician"
    new "请确认你明白自己在做什么, 或者已得到有资质的技术人员的指导"

