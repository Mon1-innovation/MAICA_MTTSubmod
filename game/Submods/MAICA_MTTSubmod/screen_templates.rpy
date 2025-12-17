screen maica_setter_medium_frame(title=None, ok_action=None, cancel_action=None):
    frame:
        style_prefix "confirm"
        xalign 0.5
        yalign 0.5
        vbox:
            xsize 800
            ymaximum 350

            spacing 5
            if title:
                label title:
                    style "confirm_prompt"
                    xalign 0.5
            vbox:
                xsize 600
                xalign 0.5
                transclude
            hbox:
                xalign 0.5
                spacing 100
                if ok_action:
                    textbutton _("OK") action ok_action
                if cancel_action:
                    textbutton _("取消") action cancel_action

screen maica_common_outer_frame(w=1000, h=500, x=0.5, y=0.3):
    frame:
        xsize w
        xalign x
        yalign y
        vbox:
            xsize w
            spacing 5
            transclude

screen maica_common_inner_frame(w=1000, h=500, x=0.5, y=0.3):

    viewport:
        id "viewport"
        scrollbars "vertical"
        xsize w - 40
        ysize h

        mousewheel True
        draggable True

        has hbox

        vbox:
            xsize 30
        vbox:
            xsize w - 70
            spacing 5
            transclude

screen maica_l1_subframe():
    hbox:
        frame:
            xsize 950
            xpos 30
            has vbox:
                xsize 950
            transclude

screen maica_l2_subframe():
    hbox:
        frame:
            xsize 850
            xpos 30
            has vbox:
                xsize 850
            transclude

screen maica_message(message = "Non Message", ok_action = Hide("maica_message")):
    modal True
    zorder 100

    style_prefix "confirm"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            ymaximum 300
            xmaximum 800
            xfill True
            yfill False
            spacing 5

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action
