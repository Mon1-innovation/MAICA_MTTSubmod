# MTTS 与 Chat 同步实施记录

状态：已实施并验证（2026-08-16）。

本文最初是“待确认、尚未修改代码”的审计清单。该状态已经过时；本轮同步已经完成，本文改为记录实际实现、证据、验证结果和仍未处理的发布风险。

## 1. 基线与范围

- 参考项目：`D:\0Works2\MAICA_ChatSubmod`
- Chat 审计终点：`47bedca0e740f0da4863d7c98119dff165793495`
- MTTS 同步前基线：`5f7a7c2b9d1c105a2e58b8f9f67ba841515bbfd2`（`1.2.15`）
- MAS 运行时参考：本地检出 `a7e260c308000e2e21c173d5f751bce81e19b7ba`

本轮只修改 MTTS 工作树。Chat 参考仓库保持干净；Chat 专属后端、WebSocket/tasker、Vista/MPostal/背景等没有机械移植。

## 2. 已修正的审计结论

1. 原文“本阶段不修改代码”的边界已失效，代码和测试已经按下文实施。
2. MAS 的 `mas_buildEventLists()`/`Event.filterEvents(random=True)` 只按 `random` 字段筛选，不评估 `conditional`。启动阶段还会把 `EV_ACT_QUEUE` 事件排除在 `startup_events` 外；条件队列事件由后续 `Event.checkEvents()` 处理。因此 MTTS 的前置和 hint 事件必须保持 `random=False`、`pool=False`、`unlocked=False`、`action=EV_ACT_QUEUE`，并在条件中检查 `seen` 与 `mas_inEVL()`。这能阻止条件事件泄漏到随机话题列表，但不能声称它能强制排在 Chat 的随机前置话题之前。
3. MAS greeting priority 数字越小越优先。Chat recovery 使用 `0`，MAS 自带 `monikaroom_will_change` 使用 `10`，Chat 普通 intro 使用 `20`；MTTS 使用 `11`，所以不会与 MAS 的 priority-10 greeting 进入同一随机池，同时仍先于 Chat 普通 intro。
4. greeting 必须注册到 `persistent.greeting_database`，由 MAS 的 `selectGreeting()` 选择；直接写 `selected_greeting` 的 MTTS 插件已删除。`skip_visual=False` 是有意保留的，因为该对白依赖 MAS 正常初始化 spaceroom。
5. MTTS 现在沿用 Chat 的 `maica_is_dev` 开发版标志：设置页显示开发版警告，迁移通过 `force_current` 重跑当前版本，release workflow 跳过正式发布。该标志与 Chat 共用全局名称，不再引入另一套开发版变量。
6. Chat release 仍会覆盖共享路径 `game/python-packages/cp936_decode`，而 Chat 当前不再依赖该模块。MTTS 的运行入口已经改为私有 `mtts_cp936_decode.py`；公共包同时保留修正版，但不能把 release 的同名文件覆盖风险当作已消除。

## 3. 分阶段实施结果

### 阶段 A：共享运行时接口（完成）

- `logger_manager.py` 使用隔离的 `maica_logger_manager`，`propagate=False`，以 marker 去重 fallback handler，不修改 Python root logger。
- 注入的标准 logger 只同步 level，不复制 handler；默认 `LoggerWrapper` 在每次调用时解析当前 MAS logger，module reload 后仍能跟随新 manager，显式注入的 manager 则保持固定引用。
- `mtts_package.py` 与 `mtts_provider_manager.py` 删除 root-handler/`print()` fallback，接入动态 logger，并在普通格式化、字典/序列和 `logger.log()` 路径统一脱敏 `access_token`。
- `migrations.py` 默认 queue 为空，支持 `force_current=False`，版本段按数字比较并补零；unchanged、upgrade、rollback、非法版本和迁移异常均返回明确的 `(success, message)`。非法版本的旧错误文本 `Version schemas incompatable` 保留，以免破坏已有调用方的字符串契约。
- Chat 当前共享 `migrations.py` 的升级成功路径仍返回 `None`；MTTS 迁移脚本已把 `None` 视为成功，避免两个整包按不同顺序覆盖时崩溃。

### 阶段 B：事件与 greeting（完成）

- `mtts_prepend_1` 和 `mtts_hint` 按 MAS 条件队列模型重注册；完成对白返回 `no_unlock|derandom|rebuild_ev`，避免旧随机/池字段继续生效。
- hint 条件同时排除已收到或已在磁盘中待处理的礼物、已完成 greeting 和已在事件列表中的项；礼物反应标签、hint 标签入口的礼物发现短路以及 `ch30_preloop` 清理钩子会移除同一分钟或旧存档中残留的 hint 队列项。
- greeting 条件要求 generic startup、prepend 完成、礼物反应完成、AFFECTIONATE+、非特殊日、非玩家生日且 `mtts_greeting_end` 未完成。旧 Event 对象会显式更新字段和规则，避免 MAS `addEvent()` 的 `setdefault` 保留旧数据。
- greeting priority 为 `11`，使用 MAS 正式 greeting 选择流程；不再使用 `ch30_post_exp_check` 插件或直接写 `selected_greeting`。
- `unlock_progress.rpy` 与真实条件保持一致。

### 阶段 C：旧存档迁移（完成）

- 新增 `1.2.16` 迁移，修复两个事件的 conditional/action/random/pool/unlocked/rules 字段，清除旧 `bookmark_rule`、重复队列项、已完成队列项，以及 `_mas_player_bookmarked`、`_mas_player_derandomed`、`flagged_monikatopic` 中的旧标签。
- 新迁移不把“进入 `mtts_greeting`”推断为完成；新存档以真实的 `mtts_greeting_end` 为完成标记。极旧的 `0.1.10` 历史迁移只在旧 Event 的 `shown_count > 0`（MAS 已完整返回事件）时补写 end 标记，保存中断的旧 greeting 不会被永久锁死。
- MTTS 优先识别增强版 migration 的成功 tuple；为兼容 Chat release 覆盖旧版 `migrations.py` 时的升级路径，也接受其历史成功返回值 `None`。明确失败 tuple 不会推进 `persistent._mtts_last_version`，失败会记录错误并在下次启动重试。

### 阶段 D：本地等价修复（完成）

- `main.rpy` 的 `decode_str` 对字节同时计算严格 UTF-8 与完整 CP936 候选：通常采用 UTF-8；当两者均可解码且 UTF-8 候选只有非文字符号、CP936 候选包含 CJK 时，保留历史 CP936 解释（例如 `"隆".encode("gbk") == b"\xC2\xA1"`），避免歧义字节误读。Unicode、空 bytes、bytearray、非法/截断字节均返回 Unicode，不再依赖 `chardet` 的 `encoding=None` 结果。
- `cp936_decode` 修复 Python 2/3 字节处理、`0x80 -> U+20AC`、CP936 扩展 pair 和非法 pair；MTTS 实际运行使用新增的私有 `mtts_cp936_decode.py`，避免 Chat 整包覆盖共享模块。
- 版本检查改为数字段比较，修复 `1.2.10` 与 `1.2.9` 的顺序错误；成功检查和失败检查都会清除陈旧的 `_outdated` 标志。
- 版本升至 `1.2.16`。
- 迁移 Chat 的 `maica_is_dev` 职能：Mtts 设置页显示开发版警告，开发版 workflow 不创建 release，且当前迁移会在每次启动执行。

## 4. 验证

- `C:\Users\Edge\Documents\teaching\Scripts\python.exe -m pytest -q tests`：`70 passed`。
- `tests/test_mtts_sync_contract.py`：事件契约、迁移修复、迁移结果、logger 注入/脱敏/root handler 和 reload 去重。
- `tests/test_mtts_text_and_version.py`：CP936/GBK/UTF-8 边界、数字版本比较、当前/失败检查清除 `_outdated`。
- `tests/test_mtts_dev_contract.py`：`maica_is_dev`、设置页警告、强制迁移和 release workflow 门控。
- 参考 Chat 的 Unicode/version/backend 兼容测试：`163 passed`（其余 Chat 测试未作为 MTTS 工作树的全套入口运行）。
- 本轮修改的 Python 文件已逐文件通过 `py_compile`；仓库全量 `compileall` 仍会被原有的 Python 2 专用 `datapy2_mtts.py` 拦截。`git diff --check` 无空白错误（仅报告 autocrlf 行尾提示）。
- 修改的 Ren'Py `init ... python` 块已用 Python AST 做语法解析；当前环境没有完整 Ren'Py/MAS 图形运行时，因此未执行 GUI 启动回归。
- 已按 MAICA-MTTS 后端文档及提交 `c0e5f3c` 核对 `GET /version` 的 `content.fe_synbrace_version` 字段；对 `success=True` 但 `content` 为 `None`、列表或缺字段的响应均安全返回“不判定过期”。
- 本轮新增了 Mtts 设置页开发版警告及其 `tl/header.rpy` 中文翻译；没有改动 `tl/chat.rpy`。

仓库根目录直接运行无参数 `pytest` 会额外收集既有的 `game/python-packages/mtts_test.py`，该手工脚本会读取开发者本地 `token.txt`，因此不是可重复的项目测试入口；正式结果以 `pytest tests` 为准。

## 5. 范围外风险

- 两个 release workflow 都打包完整 `game`。MTTS workflow 已加入开发版跳过发布，但 Chat 当前携带 `urllib3 1.26.9`，MTTS 携带 `urllib3 1.26.20`；本轮没有擅自统一依赖，后续应在发布流程中解决同名文件覆盖和依赖版本治理。
- MTTS/Chat 的前置事件跨子模组执行顺序仍由 MAS 的随机话题选择和分钟检查决定；本轮保证的是 MTTS 自身条件不绕过，不是跨子模组的绝对先后。
- logger reload 修复只覆盖默认动态 wrapper；外部显式注入旧 manager 的调用方仍按设计固定，且 Chat 未来覆盖共享 logger 文件时需保持同一实现才能保留该行为。
- 当前工作树的 `maica_is_dev=True` 是开发构建状态，正式发布前必须改为 `False`；若 Chat 与 MTTS 同时加载，两者应保持同一全局值。若两个子模组版本配置不一致，后加载的 header 会覆盖该共享标志，属于发布配置风险。本轮没有在完整 MAS 图形运行时中启动旧存档回归；上游行为依据上述 MAS commit 的源码核验，真实安装包仍应覆盖特殊日、生日、typed/reload/crash greeting、礼物同分钟到达和重启场景。
