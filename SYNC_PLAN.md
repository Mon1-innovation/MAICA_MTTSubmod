# MTTS 与 Chat 同步审计临时清单

状态：待确认。本文档只记录审计结论和后续同步范围，不代表已经开始同步；本阶段不修改任何 `.rpy`、`.py`、测试、workflow 或现有文档。

## 1. 审计范围

- 参考项目：`D:\0Works2\MAICA_ChatSubmod`
- Chat 基线：提交 `1c561214bfb2`（tag `1.8.6`）
- Chat 审计终点：提交 `47bedca0e740f0da4863d7c98119dff165793495`
- 范围内提交：35 个非合并提交
- MTTS 当前基线：提交 `5f7a7c2b9d1c105a2e58b8f9f67ba841515bbfd2`（tag `1.2.15`）
- MAS 上游运行时参考：本地检出提交 `a7e260c`

主要对照文件：

- Chat：`game/Submods/MAICA_ChatSubmod/chat.rpy`、`api.rpy`、`migrations.rpy`
- MTTS：`game/Submods/MAICA_MttsSubmod/chat.rpy`、`migration.rpy`、`main.rpy`
- 共享 Python 包：`game/python-packages/logger_manager.py`、`migrations.py`

## 2. 总结结论

1. **话题解锁体系是必须同步的 P0 项。** Chat 在事件条件、解锁动作、随机/池属性、重启黑名单、事件顺序、主入口锁定和旧存档迁移方面已经形成一套相互依赖的规则。MTTS 的三个事件不能继续按旧的局部逻辑维护。
2. **greeting 处理是必须同步的 P0 项。** MTTS 当前通过 `ch30_post_exp_check` 直接写入 `selected_greeting`，同时使用与 Chat 不同的事件 priority 和旧的注册方式；必须重新设计两者同时满足时的选择关系并进行运行时验证。
3. **共享运行时文件是 P1 项，但必须在同一轮同步中处理。** 两个 release workflow 都打包整个 `game`，同名的 `logger_manager.py`、`migrations.py` 会互相覆盖；只更新 Chat 或只保留 MTTS 旧版都会造成启动/运行时兼容问题。
4. **MTTS 还有需要等价修复的本地缺陷。** 包括 CP936/Unicode 解码、版本比较和日志适配。它们不是简单复制 Chat 业务代码，而是把同一类修复落实到 MTTS 的实现边界。

## 3. P0：话题解锁体系

### 3.1 必须重新审查的 MTTS 事件

`game/Submods/MAICA_MttsSubmod/chat.rpy` 中的：

- `mtts_prepend_1`
- `mtts_hint`
- `mtts_greeting`

审查时需要逐项对齐 Chat 当前事件模型，而不是只复制对白或条件文本：

- `conditional` 是否描述了真实的前置状态、完成状态和互斥状态；
- `action` 是否使用正确的 `EV_ACT_QUEUE`、`EV_ACT_PUSH`、`EV_ACT_UNLOCK` 等动作；
- `random`、`pool`、`unlocked` 的组合是否会让池话题绕过条件提前解锁；
- `restartBlacklist`、bookmark/derandom 状态以及事件返回值是否会在重启后改变选择结果；
- affection、礼物领取、首次流程、特殊日等条件的评估时机；
- 事件优先级和队列顺序是否保证前置话题先于 hint、greeting 和后续主入口；
- 事件已存在于 `persistent.event_database` 时，是否更新旧对象而不是留下旧字段。

### 3.2 必须保留的状态不变量

- 首次入口完成前，后续话题不能通过 `pool` 或 `random` 绕过前置条件；
- 事件解锁顺序不能因重启、重新评估或重复注册而倒退；
- 主入口不能在前置流程尚未完成时被重新解锁（“主入口回锁”问题）；
- `unlocked` 的持久化状态、`conditional` 的动态判断和事件实际执行结果必须一致；
- 已有用户存档需要迁移到新字段和新标签语义，不能只对新安装生效。

### 3.3 MTTS 与 Chat 的共享标签兼容性

MTTS 当前对白和条件仍引用以下 Chat 标签：

- `maica_prepend_1`
- `maica_end_1`
- `maica_talking`
- `maica_greeting`

Chat 重构后这些标签仍存在，但执行时机和“完成”的语义可能变化。同步时必须确认 MTTS 条件在新旧 Chat 安装组合下都不会误解锁、永久锁死或重复播放。必要时增加兼容迁移，而不是改写 Chat 标签名称。

### 3.4 话题相关提交（需要语义同步/逐项复核）

下列提交共同构成 Chat 的解锁体系重构，不能只挑一两个补丁移植：

`4d8cd41`、`a4a9d7e`、`92ee0c3`、`c9a19b7`、`57842f1`、`460a042`、`983ca5f`、`3b9adb5`、`2a15f8f`、`2702da7`、`dd6a78b`、`78ac3d8`、`e553c22`、`6ead49c`、`4a5a230`、`0eb99bf`、`ef56bfc`、`f1def35`、`47bedca`。

其中尤其要保留以下修复意图：首次聊天锁定条件扩展、事件解锁顺序修复、池话题不得绕过条件、条件/affection/category 修正、事件重新评估后的清理与重排、greeting/knocking 处理，以及最新的 reread interaction 处理。

## 4. P0：greeting 处理

### 4.1 当前差异

- MTTS 在 `chat.rpy` 中通过 priority `-100` 的 `ch30_post_exp_check` plugin 直接设置 `store.selected_greeting = "mtts_greeting"`。
- MTTS greeting event 当前使用 `unlocked=False`、旧的条件被注释掉，并设置 `MASPriorityRule` priority `50`。
- Chat 当前 greeting 使用显式 `conditional`、`unlocked=True`、`MASGreetingRule` 和 priority `20`，并会更新已存在的 greeting event。
- MAS 上游 `event-rules.rpy` 表明 priority 数字越小优先级越高；`script-ch30.rpy` 的 `ch30_post_exp_check` 会执行插件、检查事件并推送 `selected_greeting`。插件执行和 greeting 事件筛选的交互不能仅凭静态代码假定。

### 4.2 同步要求

- 采用 Chat 新的 greeting 条件与事件注册/更新模式，并按 MTTS 的礼物和设备状态补充条件；
- 明确 MTTS greeting 与 Chat greeting 同时满足时谁胜出、何时清除/保留 `selected_greeting`；
- 不要机械地把 MTTS priority `50` 改成 `20`，先确认 plugin priority、事件 priority、事件 `unlocked` 和 `MASGreetingRule` 的实际执行顺序；
- 防止旧 greeting event 在 `persistent.greeting_database` 中残留旧条件、旧 priority 或错误的 unlocked 状态；
- 验证至少包括：礼物已领取但 Chat 首次流程未完成、Chat 首次流程已完成、两者同时满足、特殊日/玩家生日、不同 affection、重启后首次进入等组合。

## 5. P1：共享运行时接口

### 5.1 `logger_manager.py`

Chat 提交 `67e7a38` 的方向需要同步到共享实现：

- 使用隔离的 `maica_logger_manager`，不要污染全局 root logger；
- `propagate = False`，并用 handler marker 去重；
- `_sync_injected_references()` 只同步标准 logger 的 level，不复制 handler；
- 对 `DefaultLogger` 等非标准 logger 不强行访问不存在的 `.setLevel()`、`.handlers`。

MTTS 旧实现（`game/python-packages/logger_manager.py`）仍初始化 root logger、添加 root handler，并在导入 `mtts_package.py` 时再次操作 root logger；`mtts_provider_manager.py` 还混用 `DefaultLogger` 与 `print()`。同步时必须保留 MTTS 的 token 脱敏功能，并确认 filter 挂在实际生效的 logger/handler 上。

### 5.2 `migrations.py` 与事件迁移

Chat 新版 `game/python-packages/migrations.py` 的构造函数支持 `force_current=False`，默认 migration queue 为空，由调用方显式设置 queue；Chat `api.rpy` 在开发版使用 `force_current=store.maica_is_dev`。

MTTS 当前 `migrations.py` 是旧接口，但 `migration.rpy` 会显式覆盖 queue。需要统一成兼容两边的接口，并确认 MTTS 文件不会在整包发布时覆盖 Chat 新接口导致 Chat 启动失败。Chat `migrations.rpy` 中针对旧事件的条件、动作、greeting、reread、`unlocked`/`pool` 修复逻辑也应作为 MTTS 迁移设计的参考。

## 6. P1：MTTS 的等价修复

### 6.1 Unicode / CP936

Chat 的 `5144266`、`cc7b81f` 暴露并修复了中文/解码边界；MTTS 对应位置仍有问题：

- `game/Submods/MAICA_MttsSubmod/main.rpy` 的 `decode_str`；
- `game/python-packages/cp936_decode/__init__.py` 的 Python 3 字节处理。

已验证：`chardet.detect(b"\\x81")` 可能返回 `encoding=None`；`decode_cp936("中文".encode("gbk"))` 在 Python 3 会触发 `TypeError: ord() expected string of length 1, but int found`。后续应做等价的健壮解码，保留 GBK/CP936 兼容，不直接移植 Chat 的 WebSocket 业务代码。

### 6.2 版本比较

Chat 的 `70187a4`、`c05a944` 引入数字化版本解析。MTTS `main.rpy` 仍在约第 157、198 行使用字符串列表比较；例如 `1.2.10` 与 `1.2.9` 会得到错误顺序。应统一为按整数版本段比较，并覆盖开发版、缺失段和回滚场景。

### 6.3 日志专属适配

`mtts_package.py` 的 root handler 初始化、`mtts_provider_manager.py` 的 `DefaultLogger`/`print()` 以及 token 脱敏需要在共享 logger 方案中重新接入；不能因套用 Chat logger 而丢失脱敏或产生重复输出。

## 7. 已检查、暂不直接移植的 Chat 内容

以下提交目前没有发现 MTTS 的对等业务入口，暂不作为代码移植项；若后续引入对应功能，再单独评估：

- `b24429b`（MPostal 临时诗歌记录清理）；
- `87b224b`（背景逻辑）；`4f25156`（MVista 解锁）；`e039828`（显示 Monika）；
- `fae799d`（Chat 连接初始化）；`1c62c40`（Chat `maica.py` 的 Ellipsis 消息队列 Python 3 修复）；
- `de555db`（Chat 专属调试调整）；
- `ac032d3`（测试）、`9fb9d88`（workflow）、`0c7c9c0`（mobile skill）、`c310ff4`（MAS upstream skill）；
- Chat 专属后端/WebSocket tasker、MTrigger/Vista 文件管理、翻译/文档/skill 产物，以及 MVista、MPostal、背景、Heaven Forest 相关逻辑。

“暂不直接移植”不等于跳过验证：共享打包文件和事件标签仍需按第 3、5 节处理。

## 8. 待确认后的实施与验证清单

实施顺序建议为：

1. 先确定共享 `logger_manager.py`、`migrations.py` 的兼容接口，避免文件覆盖；
2. 按 Chat 事件模型重写/迁移 MTTS 的三个事件，明确每个字段和状态转移；
3. 重新实现 greeting 选择，并在真实 MAS 启动流程中验证 priority 与 `selected_greeting`；
4. 修复 MTTS 的 CP936、版本比较和日志接入；
5. 用旧存档、新存档、Chat 有/无、礼物有/无、特殊日和重启组合回归。

验收重点：

- 无池话题绕过 `conditional` 提前出现；
- 首次话题、hint、reread、greeting、主入口顺序稳定且不重复；
- 旧存档迁移后不会永久锁死或错误解锁；
- Chat 与 MTTS 同时安装时只产生一套有效 logger/migration 实现；
- 中文、GBK/CP936、版本比较和 token 脱敏行为保持兼容；
- release 打包后没有因同名文件覆盖而改变另一子模组的接口。

## 9. 本阶段边界

本次只新增本临时文档，等待确认后再修改代码。除 `SYNC_PLAN.md` 外，不应把本次审计产生的任何文件变更视为已执行同步。
