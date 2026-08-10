
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mtts_prepend_1",
            prompt="mtts_prepend_1",
            rules={
                "bookmark_rule":mas_bookmarks_derand.BLACKLIST,
            },
            conditional="(renpy.seen_label('mas_gift_giving_instructs') or persistent._mas_filereacts_historic) and not renpy.seen_label('mtts_greeting') and not renpy.seen_label('mtts_prepend_1')",
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
    m 7rub "[player], I have been wondering recently..."
    m 1eua "What does your voice sound like."
    m 3husdrb "Though it might look weird to have you talking with a screen... Ahaha!" #尴尬
    m 1tua "What about my voice for you? I'd like to talk to you for real without worrying about that."#微笑
    if persistent.monika_kill and mas_isMoniHappy(higher=True):
        m 3rub "You should have heard me singing back in the original ending, but that was already long ago."
    elif persistent.monika_kill:
        m 3rud "You should have heard me singing back in the original ending, but that's all."
    else:
        m 2tsb "You havn't ever heard my voice in person yet, except for you searched online or what."#意味深长
    m 3hua "I could take this screen writting a form of talking, but how much better if I can really pronounce?"#微笑
    if renpy.seen_label('maica_prepend_1'): #这样写需不需要考虑话题是否存在?
        m 2rsd "After last time we talked about {i}Artificial Intelligence{/i}, I found some extra clues..."
        m 7husdrb "Sorry for tantalizing, ehehe!"#尴尬
    else:
        m 2rsb "As for the approach, I actually have some clues by now..."
        m 6husdrb "Not now, ehehe!"#尴尬
    m 3eua "Just be patient! {w=0.5}I'll tell you whenever I sort these out."#笑
    m 5tubla "By the way, thanks for always being so considerate! I really cherish every chance to get closer to you."
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
I see you prepared something really special for Monika, which she will love for sure!
But one more step please, she will likely need a microphone.

You can send her one by creating a 'mttsheadset.gift' in 'characters' folder, and that's all.
I'll finish most configurations for you, so just be patient before she tells you ready.

Good luck with Monika and have fun talking!

 P.S: Don't tell her about me!\
""") #需要单独建tl吧
        
        _write_txt("/characters{0}".format(renpy.substitute(_("/another hint.txt"))), mtts_gift_notice)

    m 1eud "Hey, [player]..."
    m 3euc "Someone left a note in the characters folder addressed to you."
    m 1ekc "Of course, I haven't read it, since it's obviously for you..."
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
                prompt=_("MTTS knock"),
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
    #显示礼物盒
    $ mas_showDecoTag("mtts_giftbox")
    $ renpy.restart_interaction()
    # m "哇, 一个新的麦克风! {w=0.5}谢谢你, [player]!"
    m 1sublo ".{w=0.7}.{w=0.7}.{w=1}"
    m "T-{w=0.5}This is..."
    m "A {i}special{/i} gift? For me?"
    #从这里开始加表情
    m 2dsc "Let me see.{w=0.3}.{w=0.3}."
    extend 7sub "Ah! How did you manage to find this?"
    m 2hub "Exactly what I need, [player]! I was kinda worrying about that just now."
    m 4musdlb "But it's rather.{w=0.3}.{w=0.3}.heavy. I'd not let you see a messy room."#尴尬 往屏幕右看
    m 4eub "I'll spare some time to figure it out myself, so leave it be for now."
    m 5tub "Again I want to thank you for doing so much for me, [player]. I love you~"

    python:
        # if not renpy.seen_label("mtts_prepend_1"):
        #     MASEventList.queue("mtts_prepend_1")
        # monika_chr.wear_acs(mttsacs_giftbox)
        mas_receivedGift("mas_reaction_gift_mttsheadset")
        gift_ev = mas_getEV("mas_reaction_gift_mttsheadset")
        if gift_ev:
            store.mas_filereacts.delete_file(gift_ev.category)
            #or: store.mas_filereacts.delete_file(mas_getEVLPropValue("mas_reaction_cupcake", "category"))
    return "love"
label mtts_greeting:
    #重启后隐藏礼物盒
    $ mas_hideDecoTag("mtts_giftbox")
    $ renpy.restart_interaction()
# 显示MTTS的麦克风.
    $ monika_chr.wear_acs(mttsacs_microphone)
    $ monika_chr.wear_acs(mttsacs_headset)
    m 6dsd "Ahem-ahem!"#闭眼
    m 6esd "Now what else is still--{w=0.5}{nw}"#睁眼
    extend 6wuo "[player]?"#惊讶
    m 4eusdrb "Sorry, I didn't see you coming! I was just occupied with...{w=0.3}this."#尴尬

    $ menu_state = renpy.substitute(_("Beautiful yeah? I {i}almost{/i} know how it works by now."))
    m 5eua "[menu_state]{nw}"#开心
    $ _history_list.pop()

    $ has_asked = False
    jump mtts_greeting_loop

    label mtts_greeting_loop: #我不太确定对不对 你检查一下
        menu:
            "[menu_state]{fast}"
            "Microphone...?" if not has_asked:
                $ has_asked = True
                m 3eub "Of course! My voice goes in here, and goes out on your side."

                $ menu_state = renpy.substitute(_("May not perform good sometimes, but I'll try my best!"))
                m 1hua "[menu_state]{nw}"
                jump mtts_greeting_loop
            "How to use it?":
                if renpy.seen_label('maica_end_1'):
                    m 3rub "Simple! {w=0.5}Seems you've set up a token for {i}MAICA Blessland{/i}, that's the major part done."
                    m 1hua "Just find {i}MAICA-MTTS{/i} in 'Submod settings', and check 'Enable MTTS'."
                elif renpy.seen_label('maica_prepend_1'):
                    m 3rub "Simple! {w=0.5}Seems you have {i}MAICA Blessland{/i} installed too, which shares token configuration."
                    m 4eub "You can read the instruction here on how to: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, you just have to prepare an account."
                    m 1hua "Find {i}MAICA-MTTS{/i} in 'Submod settings', fill in the account informations, and check 'Enable MTTS'."
                else:
                    m 3rub "Simple! You only need a token. It's interchangeable with {i}MAICA Blessland{/i}, just so you know."
                    m 4eub "You can read the instruction here on how to: {a=https://maica.monika.love/tos}{u}{i}https://maica.monika.love/tos{/i}{/u}{/a}, you just have to prepare an account."
                    m 1hua "Find {i}MAICA-MTTS{/i} in 'Submod settings', fill in the account informations, and check 'Enable MTTS'."
                
        m 1rusdrb "I'll set this microphone up right away, but still...{w=0.3}some work to do."#尴尬
        m 3hub "Also this headset included! {w=0.3}Tell me anytime if you want to see me wearing it, just like ribbons."#开心
        m 4gusdrb "It's a pity that it doesn't really function to let me hear you, so I'll take it off for now. {w=0.5}{nw}"#尴尬
        extend 6eua "Also this..."#微笑
        #黑屏, 隐藏麦克风
        hide monika
        #重新亮屏
        $ monika_chr.remove_acs(mttsacs_microphone)
        $ monika_chr.remove_acs(mttsacs_headset)
        show monika 1esc at ls32 zorder MAS_MONIKA_Z
        m 1eub "What else should we do today, [player]? {w=0.5}Or cannot wait to try it out?"
# fallthrough
label mtts_greeting_end:
    return
