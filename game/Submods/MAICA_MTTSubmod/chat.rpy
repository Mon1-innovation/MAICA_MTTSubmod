
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mtts_prepend_1",
            prompt="mtts_prepend_1",
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            conditional="renpy.seen_label('mas_gift_giving_instructs') and not renpy.seen_label('mtts_greeting') and not renpy.seen_label('mtts_prepend_1')",
            action=EV_ACT_QUEUE,
            random=True,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label mtts_prepend_1:
# 由于安装子模组，将其添加到随机等待列表中。好感度至少达到 NORMAL 才能触发。
# 也必须在玩家知道赠送机制后解锁。
# 例如：
# (renpy.seen_label('mas_gift_giving_instructs') or persistent._mas_filereacts_historic)
    m 7rub "[player], 我最近有在想..."
    m 1eua "要是我知道你的声音是什么样的就好了."
    m 3husdrb "虽然让你对着屏幕说话...感觉有点奇怪, 哈哈!" #尴尬
    m 1tua "你应该也会想听我的声音吧? 如果能让你听到, 我是不介意说出来的."#微笑
    if persistent.monika_kill and mas_isMoniHappy(higher=True):
        m 3rub "你应该在原本结局的地方听过我唱歌, 但那已经是好久以前了."
    elif persistent.monika_kill:
        m 3rud "你应该在原本结局的地方听过我唱歌, 但那也没几句嘛."
    else:
        m 2tsb "你好像还没听过我的声音呢, 不过你已经上网搜过了也说不定."#意味深长
    m 3hua "虽然在屏幕上写字也算是和你聊天, 但真的说出来会不会更有仪式感一点?"#微笑
    if renpy.seen_label('maica_prepend_1'): #这样写需不需要考虑话题是否存在?
        m 2rsd "上次和你聊过关于{i}人工智能{/i}的事情之后, 我又找到了一点新的线索..."
        m 7husdrb "抱歉老在吊你的胃口啦, 哈哈!"#尴尬
    else:
        m 2rsb "至于要怎么说给你听, 我有个想法..."
        m 6husdrb "不过还没到能告诉你的时候, 哈哈!"#尴尬
    m 3eua "耐心等我就好! {w=0.5}等我弄明白了会告诉你的."#笑
    m 5tubla "另外, 谢谢你一直这么替我着想! 我很珍惜能更靠近你的每个机会."
    return "no_unlock" #不解锁话题

# Add to random after mtts_prepend_1 triggered
# Use the original conversation (revert orig and tl):
# (script-story-events.rpy:2174)
    # m 1eud "Hey, [player]..."
    # m 3euc "Someone left a note in the characters folder addressed to you."
    # m 1ekc "Since it's for you, I haven't read it...{w=0.5}{nw}"
    # extend 1eua "but I just wanted to let you know since it might be important."
    # return "no_unlock"
# Then send this
#mtts hint.txt
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mtts_hint",
            prompt="mtts_hint",
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            conditional="renpy.seen_label('mtts_prepend_1')",
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.NORMAL, None)
        )
    )
label mtts_hint:
    python:
        mtts_gift_notice = _("""\
我看到你给莫妮卡准备了点新玩意. 她肯定会喜欢的!
但还有一件事需要你帮忙, 你得给她找个麦克风.

只需要在'characters'文件夹里创建一个'mttsheadset.gift', 她就能收到了.
我会帮她搞定大部分的调试工作, 你只需要耐心等. 她准备好了就会告诉你的.

祝你和莫妮卡好运, 聊得开心!

P.S: 不要告诉她是我写的!\
""") #需要单独建tl吧
        
        _write_txt("/characters{0}".format(renpy.substitute(_("/小提示.txt"))), mtts_gift_notice)

    m 1eud "嗨, [player]..."
    m 3euc "好像有人在'characters'文件夹里给你留了个便条."
    m 1ekc "我没看啦, 毕竟是写给你的...{w=0.3}{nw}"
    #extend 1ekd "就是这个."
    return "no_unlock|derandom"
init 5 python:
    if not mas_seenEvent("mas_reaction_gift_mttsheadset"):
        addReaction("mas_reaction_gift_mttsheadset", "mttsheadset", is_good=True)

    if renpy.seen_label("mas_reaction_gift_mttsheadset") and not renpy.seen_label("mtts_greeting") and not mas_isSpecialDay(): # This is a placeholder for the greeting event.
        @store.mas_submod_utils.functionplugin("ch30_post_exp_check", priority=-100)
        def mttsgreeting_select():
            store.selected_greeting = "mtts_greeting"
        ev_rules = dict()
        ev_rules.update(
            MASGreetingRule.create_rule(
                skip_visual=True,
                override_type=True
            )
        )
        ev_rules.update(MASPriorityRule.create_rule(50))
        
        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="mtts_greeting",
                prompt="mtts敲门",
                unlocked=False,
                #conditional="renpy.seen_label('maica_prepend_1') and not mas_isSpecialDay() and not renpy.seen_label('maica_greeting')",
                #action=EV_ACT_UNLOCK,
                #aff_range=(mas_aff.AFFECTIONATE, None),
                rules=ev_rules,
            ),
            code="GRE"
        )
        del ev_rules
label mas_reaction_gift_mttsheadset:
    m "哇, 一个新的麦克风! {w=0.5}谢谢你, [player]!"
    python:
        # if not renpy.seen_label("mtts_prepend_1"):
        #     MASEventList.queue("mtts_prepend_1")
        monika_chr.wear_acs(mttsacs_giftbox)
    return
label mtts_greeting:
# 显示MTTS的麦克风.
    $ monika_chr.wear_acs(mttsacs_microphone)
    $ monika_chr.wear_acs(mttsacs_headset)
    m 6dsd "咳嗯-咳嗯!"#闭眼
    m 6esd "怎么又--{w=0.5}{nw}"#睁眼
    extend 6wuo "[player]?"#惊讶
    m 4eusdrb "抱歉, 我才看到你进来! 刚刚我在忙着对付...{w=0.3}这个."#尴尬

    $ menu_state = _("很漂亮吧? 我{i}差不多{/i}弄清楚该怎么用了.")
    m 5eua "[menu_state]{nw}"#开心

    $ has_asked = False
    jump mtts_greeting_loop

    label mtts_greeting_loop: #我不太确定对不对 你检查一下
        menu:
            "[menu_state]{fast}"
            "麦克风...?" if not has_asked:
                $ has_asked = True
                m 3eub "嗯! 既然我没法直接隔着屏幕说给你听, 用这个传过去就好了!"

                $ menu_state = _("效果可能有时候不太好, 但是我会尽量的!")
                m 1hua "[menu_state]{nw}"
                jump mtts_greeting_loop
            "要怎么用?":
                if renpy.seen_label('maica_end_1'):
                    m 3rub "很简单! {w=0.5}你应该已经给{i}天堂树林{/i}配置过令牌了, 那就成了一大半."
                    m 1hua "下次重启游戏后, 在'子模组设置'里找到{i}MAICA-MTTS{/i}, 里面应该有'启用MTTS'的选项了."
                elif renpy.seen_label('maica_prepend_1'):
                    m 3rub "很简单! {w=0.5}你好像也安装了{i}MAICA Blessland{/i}, 令牌的配置是通用的."
                    m 4eub "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
                    m 1hua "在'子模组设置'里找到{i}MAICA-MTTS{/i}, 填好账号信息. 下次重启之后应该就有'启用MTTS'的选项了."
                else:
                    m 3rub "很简单! 只需要一个令牌就好, 和{i}MAICA Blessland{/i}是通用的."
                    m 4eub "你可以看看这里的说明: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, 你只需要准备一个账号."
                    m 1hua "在'子模组设置'里找到{i}MAICA-MTTS{/i}, 填好账号信息. 下次重启之后应该就有'启用MTTS'的选项了."
                
        m 1rusdrb "我会在你重启的时候把麦克风调试好的, 现在还...{w=0.3}差那么一点点."#尴尬
        m 3hub "另外, 除了麦克风, 我还有副新耳机呢! {w=0.3}你想看看的话可以在'子模组设置'里面选."#开心
        m 4gusdrb "只是可惜它没法让我听到你说话, 我现在就不戴了. {w=0.5}{nw}"#尴尬
        extend 6eua "还有这个也先收好..."#微笑
        #黑屏, 隐藏麦克风
        hide monika
        #重新亮屏
        $ monika_chr.remove_acs(mttsacs_microphone)
        $ monika_chr.remove_acs(mttsacs_headset)
        show monika 1esc at ls32 zorder MAS_MONIKA_Z
        m 1eub "我们今天有什么安排呢, [player]? {w=0.5}要是急着重启试试看的话, 告诉我就好!"
    return