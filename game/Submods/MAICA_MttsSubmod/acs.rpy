image mtts_giftbox = MASFilterSwitch("mod_assets/location/spaceroom/mtts/gift.png")

init -1 python:
    hs_kwargs = {
        "priority": 11,
        "stay_on_start": False,
        "acs_type": "ribbon",
        "keep_on_desk": True,
        "use_folders": False
    }
    mph_kwargs = {
        "priority": 11,
        "stay_on_start": False,
        "acs_type": "flowers",
        "keep_on_desk": True,
        "use_folders": False
    }

    load_success = None
    while not load_success:
        try:
            mttsacs_headset = MASAccessory(
                "mttsheadset",
                "mttsheadset",
                MASPoseMap(
                    default="0",
                    l_default="5"
                ),
                **hs_kwargs
            )
            mttsacs_microphone = MASAccessory(
                "mttsmicrophone",
                "mttsmicrophone",
                MASPoseMap(
                    default="0",
                    use_reg_for_l=True
                ),
                **mph_kwargs
            )
            load_success = True
        except Exception as e:
            for kwargs in (hs_kwargs, mph_kwargs):
                if "use_folders" in kwargs:
                    kwargs.pop("use_folders")
                else:
                    raise e

    #mttsacs_giftbox = MASAccessory(
    #    "mttsgiftbox",
    #    "mttsgiftbox",
    #    MASPoseMap(
    #        default="0",
    #        use_reg_for_l=True
    #    ),
    #    priority=11,
    #    stay_on_start=False,
    #    acs_type="flowers",
    #    keep_on_desk=True,
    #    use_folders=False
    #)
    store.mas_sprites.init_acs(mttsacs_headset)
    store.mas_sprites.init_acs(mttsacs_microphone)
    #store.mas_sprites.init_acs(mttsacs_giftbox)

    #monika_chr.wear_acs(mas_acs_roses)
    #monika_chr.remove_acs(mas_acs_flowers)

    def mtts_autoacs():
        if store.mtts_say.conditions and persistent.mtts.get("acs_enabled"):
            # monika_chr.wear_acs(mttsacs_headset)
            monika_chr.wear_acs(mttsacs_microphone)
        else:
            # monika_chr.remove_acs(mttsacs_headset)
            monika_chr.remove_acs(mttsacs_microphone)

    @store.mas_submod_utils.functionplugin("ch30_loop", priority=-100)
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def mtts_firstloadacs():
        if store.mtts_say.conditions:
            store.mas_selspr.unlock_acs(mttsacs_headset)
            store.mas_selspr.unlock_acs(mttsacs_headset)

        mtts_autoacs()
    #def mtts_autoacs():
    #    if persistent.mtts.get("acs_enabled") and persistent.mtts.get("enabled"):
    #        monika_chr.wear_acs(mttsacs_headset)
    #        monika_chr.wear_acs(mttsacs_microphone)
    #    else:
    #        monika_chr.remove_acs(mttsacs_headset)
    #        monika_chr.remove_acs(mttsacs_microphone)


init 501 python:
    for bg_id in store.mas_background.BACKGROUND_MAP:
        if isinstance(bg_id, basestring) and "spaceroom" in bg_id.lower():
            MASImageTagDecoDefinition.register_img(
                "mtts_giftbox",
                bg_id,
                MASAdvancedDecoFrame(zorder=6) #21 to be in front of all cgs
            )
