init 999 python:
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def mtts_logprogress():
        # Log unlock condition status
        debug_log = store.mas_submod_utils.submod_log.debug

        # Log key label status
        debug_log("mas_reaction_gift_mttsheadset label seen: {}".format(renpy.seen_label('mas_reaction_gift_mttsheadset')))
        cond1_seen_gift = renpy.seen_label('mas_gift_giving_instructs')
        cond1_filereacts = persistent._mas_filereacts_historic
        cond1_seen_greeting = renpy.seen_label('mtts_greeting')
        cond1_seen_prepend = renpy.seen_label('mtts_prepend_1')
        cond1 = (cond1_seen_gift or cond1_filereacts) and not cond1_seen_greeting and not cond1_seen_prepend

        debug_log("mtts_prepend_1 condition: gift instructions seen={}, file reacts history={}, greeting seen={}, prepend seen={}, total condition={}".format(cond1_seen_gift, cond1_filereacts, cond1_seen_greeting, cond1_seen_prepend, cond1))

        # Condition 2: mtts_hint
        cond2_seen_prepend = renpy.seen_label('mtts_prepend_1')
        cond2 = cond2_seen_prepend
        debug_log("mtts_hint condition: prepend seen={}, total condition={}".format(cond2_seen_prepend, cond2))

        # Condition 3: mtts_greeting unlock condition (from chat.rpy lines 91-93)
        cond3_seen_gift = renpy.seen_label('mas_reaction_gift_mttsheadset')
        cond3_seen_greeting = renpy.seen_label('mtts_greeting')
        cond3_special_day = mas_isSpecialDay()
        cond3 = cond3_seen_gift and not cond3_seen_greeting and not cond3_special_day
        debug_log("mtts_greeting condition: gift reaction seen={}, greeting seen={}, special day={}, total condition={}".format(cond3_seen_gift, cond3_seen_greeting, cond3_special_day, cond3))