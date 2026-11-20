"""Admiralty UI and SKY symbols on the shared 24-unit construction grid."""
import math

from symbols_engine import SymbolSpec
from symbols_phase1_a import _draw_bell
from symbols_phase1_b import _shield_outline
from symbols_phase2 import _bubble


def plus(c):
    c.line(4, 12, 20, 12)
    c.line(12, 4, 12, 20)


def minus(c):
    c.line(4, 12, 20, 12)


def disc(c, mark):
    c.fill_circle(12, 12, 9 + .25 * c.sw)
    gap = 1.7 + .16 * c.sw
    if mark == "plus":
        c.cut_line(7.5, 12, 16.5, 12, gap)
        c.cut_line(12, 7.5, 12, 16.5, gap)
    elif mark == "close":
        c.cut_line(8.6, 8.6, 15.4, 15.4, gap)
        c.cut_line(15.4, 8.6, 8.6, 15.4, gap)
    else:
        c.cut_polyline([(7.3, 12), (10.8, 15.5), (17.1, 8.7)], gap=gap)


def bell_off(c):
    _draw_bell(c)
    c.slash_off()


def chooser(c):
    c.polyline([(7.3, 8.8), (12, 4.1), (16.7, 8.8)])
    c.polyline([(7.3, 15.2), (12, 19.9), (16.7, 15.2)])


def chat_filled(c):
    c.fill_round_rect(2.5, 3, 19, 14.5, 3.5)
    c.fill_polygon([(6.8, 16), (6.8, 21.2), (13.3, 16)])


def whisper(c, filled=False):
    if filled:
        chat_filled(c)
        c.cut_round_rect(8.6, 9.3, 6.8, 4.9, .8)
        c.cut_round_rect(9.8, 5.6, 4.4, 6, 2)
        c.fill_round_rect(11.1, 7, 1.8, 2.3, .8)
    else:
        _bubble(c)
        c.arc(12, 8.3, 2.1, 180, 360, sw=1.5)
        c.line(9.9, 8.3, 9.9, 10, 1.5)
        c.line(14.1, 8.3, 14.1, 10, 1.5)
        c.fill_round_rect(8.6, 9.1, 6.8, 4.9, .9)


def takeover(c):
    # A hand reaching for the control, with a contact mark at the fingertip.
    c.arc(9.2, 7, 4.8, 185, 318)
    c.polyline([(9.1, 14.4), (9.1, 7), (10.5, 5.9), (12, 7), (12, 11),
                (14.2, 10.7), (19, 12.6), (19.6, 15.4), (18, 21),
                (10.1, 21), (4.9, 14.7), (5.5, 13.3), (7, 13.1), (9.1, 15)])


def device_cloud(c, phone):
    # The cloud sits inside the screen, so it cannot be mistaken for a second device.
    if phone:
        c.rect(5, 2, 14, 20, 2.2)
        c.line(10.5, 18.8, 13.5, 18.8)
    else:
        c.rect(2.4, 3.6, 19.2, 13.6, 1.4)
        c.line(12, 17.2, 12, 20.4)
        c.line(7.8, 20.4, 16.2, 20.4)
    w = 1.4
    c.cubic_stroke((9.2, 12.9), (6.8, 12.9), (6.7, 9), (9.4, 9), w)
    c.cubic_stroke((9.4, 9), (10.3, 5.6), (14.7, 5.7), (15.1, 9.4), w)
    c.cubic_stroke((15.1, 9.4), (17.4, 9.7), (17.2, 12.9), (14.9, 12.9), w)
    c.line(9.2, 12.9, 14.9, 12.9, w)


def toolbox(c):
    c.rect(2.5, 7.5, 19, 13, 1.9)
    c.polyline([(8.5, 7.5), (8.5, 4.2), (15.5, 4.2), (15.5, 7.5)])
    c.line(3, 13, 21, 13)
    c.line(7, 11.8, 7, 14.9)
    c.line(17, 11.8, 17, 14.9)


def sent(c):
    c.polygon([(2.8, 9.9), (18.6, 3), (12, 18.7), (9, 12.7)])
    c.line(9, 12.7, 17.8, 3.8)
    c.polyline([(15, 17.8), (17.5, 20.4), (22, 15.2)])


def gear_filled(c):
    points = []
    for k in range(8):
        for delta, radius in [(-14, 7.1), (-8.5, 9.6), (8.5, 9.6), (14, 7.1)]:
            a = math.radians(k * 45 + delta)
            points.append((12 + radius * math.cos(a), 12 + radius * math.sin(a)))
    c.fill_polygon(points)
    c.cut_circle(12, 12, 3.3 - .16 * c.sw)


def lock_filled(c):
    c.arc(12, 8, 4.1, 180, 360)
    c.line(7.9, 8, 7.9, 11)
    c.line(16.1, 8, 16.1, 11)
    c.fill_round_rect(4, 10, 16, 11, 2.3)
    c.cut_circle(12, 15.4, 1.45)


def shield_filled(c):
    c.fill_polygon([(12, 2.2), (20.6, 5.6), (20.6, 11.7), (20, 14.7),
                    (18.3, 17.6), (15.6, 20.1), (12, 22), (8.4, 20.1),
                    (5.7, 17.6), (4, 14.7), (3.4, 11.7), (3.4, 5.6)])
    c.cut_polyline([(7.7, 11.5), (10.7, 14.5), (16.7, 8.5)], gap=2.2)


def shield_off(c):
    _shield_outline(c)
    c.slash_off()


def end_call(c):
    c.cubic_stroke((3, 13), (4, 6.6), (20, 6.6), (21, 13))
    c.polyline([(21, 13), (21, 15.5), (16.8, 15.5), (15.9, 12)])
    c.cubic_stroke((15.9, 12), (14.3, 10.8), (9.7, 10.8), (8.1, 12))
    c.polyline([(8.1, 12), (7.2, 15.5), (3, 15.5), (3, 13)])


def video_call(c):
    c.rect(2.5, 5.5, 12.7, 13, 2)
    c.polygon([(15.2, 10), (21.5, 6.8), (21.5, 17.2), (15.2, 14)])


def flight(c):
    c.fill_polygon([(10.7, 8.5), (11, 3.6), (12, 2.1), (13, 3.6), (13.3, 8.5),
                    (21.2, 14), (21.2, 16.2), (13.4, 13.1), (13.2, 18.4),
                    (16.2, 20.1), (16.2, 21.7), (12, 20.6), (7.8, 21.7),
                    (7.8, 20.1), (10.8, 18.4), (10.6, 13.1), (2.8, 16.2), (2.8, 14)])


def train(c):
    c.rect(5, 2.6, 14, 15, 3)
    c.line(5.3, 10.6, 18.7, 10.6)
    c.dot(8.8, 14.1)
    c.dot(15.2, 14.1)
    c.line(8.5, 17.6, 5.5, 21.4)
    c.line(15.5, 17.6, 18.5, 21.4)


def hotel(c):
    c.line(3, 5.5, 3, 19.5)
    c.line(3, 15.5, 21, 15.5)
    c.line(21, 11, 21, 19.5)
    c.fill_circle(6.7, 10.4, 2)
    c.fill_round_rect(10.2, 8.4, 10.8, 5.1, 1.4)


def dining(c):
    for x in (4.2, 7.3, 10.4):
        c.line(x, 3, x, 8.4)
    c.arc(7.3, 8.4, 3.1, 0, 180)
    c.line(7.3, 11.5, 7.3, 21.3)
    c.polyline([(18.8, 3), (16, 6.9), (15.2, 11.8), (18.8, 11.8)])
    c.line(18.8, 3, 18.8, 21.3)


def walk(c):
    c.fill_circle(14, 4.3, 1.8)
    c.polyline([(6, 13.3), (9.1, 11.3), (10.6, 8.3), (13.1, 8.4),
                (15, 11.7), (18.7, 12.8)])
    c.polyline([(12.1, 8.8), (10.6, 14), (14.2, 16.7), (16.6, 21.1)])
    c.polyline([(10.6, 14), (8.7, 18.2), (5.7, 21.1)])


def user_remove(c):
    c.circle(9.2, 7, 3.5)
    c.cubic_stroke((2.8, 19.6), (3.3, 13.3), (9.2, 11.6), (13.4, 14.4))
    c.line(15, 16.4, 21.7, 16.4)


# Aliases resolve to an existing drawing and keep the same private-use code point.
ALIASES = {"globe": "language", "pause-filled": "pause", "phone-off": "end-call"}


SYMBOLS_CLIENT = [
    SymbolSpec("plus", "Common", ("add", "new"), plus),
    SymbolSpec("plus-circle-filled", "Common", ("add", "attachment"), lambda c: disc(c, "plus"), is_filled=True),
    SymbolSpec("minus", "Common", ("remove", "subtract"), minus),
    SymbolSpec("bell-off", "Status", ("mute", "notifications"), bell_off),
    SymbolSpec("chevron-up-down", "Navigation", ("picker", "select"), chooser),
    SymbolSpec("close-circle-filled", "Common", ("clear", "dismiss"), lambda c: disc(c, "close"), is_filled=True),
    SymbolSpec("circle", "Status", ("unselected", "empty"), lambda c: c.circle(12, 12, 9)),
    SymbolSpec("check-circle-filled", "Status", ("selected", "complete"), lambda c: disc(c, "check"), is_filled=True),
    SymbolSpec("whisper", "Chat", ("private", "message"), whisper),
    SymbolSpec("whisper-filled", "Chat", ("private", "selected"), lambda c: whisper(c, True), is_filled=True),
    SymbolSpec("takeover", "Agent", ("human", "control"), takeover),
    SymbolSpec("cloud-computer", "Devices", ("remote", "desktop"), lambda c: device_cloud(c, False)),
    SymbolSpec("cloud-phone", "Devices", ("remote", "mobile"), lambda c: device_cloud(c, True)),
    SymbolSpec("toolbox", "Agent", ("tools", "connections"), toolbox),
    SymbolSpec("send-check", "Chat", ("sent", "outbound"), sent, rtl_mirror=True),
    SymbolSpec("chat-filled", "Chat", ("conversation", "selected"), chat_filled, is_filled=True),
    SymbolSpec("settings-filled", "Settings and preferences", ("gear", "selected"), gear_filled, is_filled=True),
    SymbolSpec("lock-filled", "Security and privacy", ("locked", "private"), lock_filled, is_filled=True),
    SymbolSpec("shield-check-filled", "Security and privacy", ("protected", "sealed"), shield_filled, is_filled=True),
    SymbolSpec("folder-filled", "Files", ("directory", "selected"), lambda c: c.fill_polygon(
        [(2.6, 4.9), (9.5, 4.9), (11.8, 7.5), (21.4, 7.5), (21.4, 20), (2.6, 20)]), is_filled=True),
    SymbolSpec("end-call", "Communication", ("hang-up", "phone-off"), end_call),
    SymbolSpec("video-call", "Communication", ("camera", "meeting"), video_call),
    SymbolSpec("flight", "Travel", ("airplane", "airport"), flight),
    SymbolSpec("train", "Travel", ("rail", "metro"), train),
    SymbolSpec("hotel", "Travel", ("bed", "lodging"), hotel),
    SymbolSpec("dining", "Travel", ("restaurant", "meal"), dining),
    SymbolSpec("walk", "Travel", ("pedestrian", "walking"), walk),
    SymbolSpec("user-remove", "Security and privacy", ("guest", "remove"), user_remove),
    SymbolSpec("shield-off", "Security and privacy", ("unprotected", "disabled"), shield_off),
]
