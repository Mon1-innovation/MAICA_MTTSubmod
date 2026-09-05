init 999 python:
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def mtts_logprogress():
        # A queued hint can outlive the condition that created it (for
        # example, when the gift reaction is processed in the same startup).
        # Remove stale or duplicate MTTS queue entries before the idle loop.
        if mtts_headset_gift_available() or renpy.seen_label("mtts_greeting_end"):
            mas_rmallEVL("mtts_hint")
        if renpy.seen_label("mtts_prepend_1") or renpy.seen_label("mtts_greeting_end"):
            mas_rmallEVL("mtts_prepend_1")

        # Log unlock condition status
        debug_log = store.mas_submod_utils.submod_log.debug

        # Log key label status
        debug_log("mas_reaction_gift_mttsheadset label seen: {}".format(renpy.seen_label('mas_reaction_gift_mttsheadset')))
        cond1_seen_gift = renpy.seen_label('mas_gift_giving_instructs')
        cond1_has_filereacts = bool(persistent._mas_filereacts_historic)
        cond1_seen_prepend = renpy.seen_label('mtts_prepend_1')
        cond1_seen_end = renpy.seen_label('mtts_greeting_end')
        cond1 = (
            (cond1_seen_gift or cond1_has_filereacts)
            and not cond1_seen_prepend
            and not cond1_seen_end
        )

        debug_log("mtts_prepend_1 condition: gift instructions seen={}, file reacts history present={}, prepend seen={}, greeting end seen={}, total condition={}".format(cond1_seen_gift, cond1_has_filereacts, cond1_seen_prepend, cond1_seen_end, cond1))

        # Condition 2: mtts_hint
        cond2_seen_prepend = renpy.seen_label('mtts_prepend_1')
        cond2_seen_hint = renpy.seen_label('mtts_hint')
        cond2_seen_gift = renpy.seen_label('mas_reaction_gift_mttsheadset')
        cond2_gift_available = mtts_headset_gift_available()
        cond2_seen_end = renpy.seen_label('mtts_greeting_end')
        cond2 = (
            cond2_seen_prepend
            and not cond2_seen_hint
            and not cond2_gift_available
            and not cond2_seen_end
        )
        debug_log("mtts_hint condition: prepend seen={}, hint seen={}, gift reaction seen={}, gift available={}, greeting end seen={}, total condition={}".format(cond2_seen_prepend, cond2_seen_hint, cond2_seen_gift, cond2_gift_available, cond2_seen_end, cond2))

        # Condition 3: keep this in lockstep with mtts_greeting_conditional.
        cond3_seen_gift = renpy.seen_label('mas_reaction_gift_mttsheadset')
        cond3_seen_prepend = renpy.seen_label('mtts_prepend_1')
        cond3_seen_end = renpy.seen_label('mtts_greeting_end')
        cond3_greeting_type_allows_override = mtts_greeting_type_allows_override()
        cond3_special_day = mas_isSpecialDay()
        cond3_player_bday = mas_isplayer_bday()
        cond3_affectionate = mas_isMoniAff(higher=True)
        cond3 = (
            cond3_greeting_type_allows_override
            and cond3_seen_prepend
            and cond3_seen_gift
            and not cond3_special_day
            and not cond3_player_bday
            and not cond3_seen_end
            and cond3_affectionate
        )
        debug_log("mtts_greeting condition: greeting type allows override={}, prepend seen={}, gift reaction seen={}, special day={}, player birthday={}, affection threshold={}, greeting end seen={}, total condition={}".format(cond3_greeting_type_allows_override, cond3_seen_prepend, cond3_seen_gift, cond3_special_day, cond3_player_bday, cond3_affectionate, cond3_seen_end, cond3))
