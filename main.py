#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE: Tuesday 17 November 2026.

Draws a newspaper front page, 1024x1024, standard library only.
Deterministic: no time, no randomness, no network. Writes entry.png
next to this file and to $MAKEFUN_OUTPUT_DIR/entry.png when set.
"""
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (253, 246, 227)
INK = (18, 18, 18)
PAPER2 = (244, 234, 205)
SKY = (178, 216, 240)
SEA = (38, 110, 180)
DEEPSEA = (24, 80, 150)
GREY = (120, 120, 118)
DARKGREY = (70, 70, 68)
STEEL = (150, 158, 165)
ORANGE = (240, 120, 20)
FLAME = (255, 176, 32)
RED = (200, 40, 32)
DUSK = (232, 150, 90)
DUSK2 = (120, 80, 130)
GREEN = (90, 160, 90)
TAN = (222, 196, 140)

# 5x7 bitmap font, each glyph is 7 rows of 5 bits ("1" = ink).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "00100", "01000"),
    "'": ("00000", "00100", "00100", "00000", "00000", "00000", "00000"),
    ":": ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ";": ("00000", "00100", "00000", "00000", "00000", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}

PIX = bytearray(W * H * 3)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = color


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = yy * W * 3
        for xx in range(x0, x1):
            i = base + xx * 3
            PIX[i], PIX[i + 1], PIX[i + 2] = color


def hline(x, y, w, color, thick=1):
    fill_rect(x, y, w, thick, color)


def vline(x, y, h, color, thick=1):
    fill_rect(x, y, thick, h, color)


def circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        for xx in range(cx - dx, cx + dx + 1):
            put(xx, cy + dy, color)


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for t in range(thick):
            put(x0 + t, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def poly_fill(points, color):
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                put(xx, y, color)


def text_w(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    for ci, ch in enumerate(text):
        glyph = FONT.get(ch, FONT[" "])
        ox = x + ci * 6 * scale
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == "1":
                    fill_rect(ox + c * scale, y + r * scale, scale, scale, color)


def draw_centered(cx, y, text, scale, color):
    draw_text(cx - text_w(text, scale) // 2, y, text, scale, color)


def wrap(text, scale, max_w):
    max_chars = max(1, max_w // (6 * scale))
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cx, y, text, scale, color, max_w, leading=4):
    lines = wrap(text, scale, max_w)
    for i, ln in enumerate(lines):
        draw_centered(cx, y + i * (7 * scale + leading), ln, scale, color)
    return len(lines) * (7 * scale + leading)


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += PIX[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- scenes (panels 1 and 2) ----

def scene_kerch(px, py, pw, ph):
    fill_rect(px, py, pw, ph, SKY)
    water_y = py + int(ph * 0.62)
    fill_rect(px, water_y, pw, ph - int(ph * 0.62), SEA)
    # sun
    circle(px + pw - 60, py + 40, 24, (255, 214, 90))
    # bridge deck with a broken gap in the middle
    deck_y = py + int(ph * 0.45)
    fill_rect(px + 10, deck_y, pw // 2 - 45, 12, STEEL)
    fill_rect(px + pw // 2 + 35, deck_y, pw // 2 - 45, 12, STEEL)
    # leaning tower on the right span
    line(px + pw - 110, deck_y, px + pw - 80, deck_y - 90, DARKGREY, 6)
    # cables
    line(px + 30, deck_y, px + pw // 2 - 45, deck_y - 70, DARKGREY, 2)
    # broken deck pieces falling
    poly_fill([(px + pw // 2 - 40, deck_y), (px + pw // 2 - 10, deck_y),
               (px + pw // 2 - 20, deck_y + 45), (px + pw // 2 - 48, deck_y + 30)], STEEL)
    # smoke rising from the gap
    circle(px + pw // 2 - 8, deck_y - 22, 16, DARKGREY)
    circle(px + pw // 2 + 6, deck_y - 44, 18, GREY)
    circle(px + pw // 2 - 2, deck_y - 62, 13, GREY)
    # waves
    for wx in range(px + 8, px + pw - 8, 46):
        line(wx, water_y + 42, wx + 24, water_y + 42, (255, 255, 255), 2)
        line(wx + 10, water_y + 66, wx + 34, water_y + 66, (255, 255, 255), 2)


def scene_hormuz(px, py, pw, ph):
    fill_rect(px, py, pw, ph, SKY)
    sea_y = py + int(ph * 0.55)
    fill_rect(px, sea_y, pw, ph - int(ph * 0.55), SEA)
    circle(px + 56, py + 36, 22, (255, 214, 90))
    # tanker hull
    hull_y = sea_y - 18
    fill_rect(px + 30, hull_y, pw - 60, 34, (140, 30, 26))
    fill_rect(px + 30, hull_y + 34, pw - 60, 8, INK)
    # tanker deck structures
    fill_rect(px + 44, hull_y - 34, 60, 34, (200, 200, 200))
    fill_rect(px + pw - 120, hull_y - 52, 70, 52, (220, 220, 220))
    # flames from the deck
    for fx, fh in ((px + 170, 46), (px + 200, 62), (px + 230, 44), (px + 260, 56)):
        poly_fill([(fx - 16, hull_y), (fx, hull_y - fh), (fx + 16, hull_y)], ORANGE)
        poly_fill([(fx - 9, hull_y), (fx, hull_y - fh + 18), (fx + 9, hull_y)], FLAME)
    # black smoke
    circle(px + 200, hull_y - 52, 14, INK)
    circle(px + 224, hull_y - 66, 15, DARKGREY)
    circle(px + 196, hull_y - 74, 11, DARKGREY)
    # waves
    for wx in range(px + 8, px + pw - 8, 46):
        line(wx, sea_y + 52, wx + 24, sea_y + 52, (255, 255, 255), 2)


def scene_meet(px, py, pw, ph):
    # dusk sky over a city skyline
    fill_rect(px, py, pw, ph, DUSK)
    fill_rect(px, py + int(ph * 0.45), pw, ph - int(ph * 0.45), DUSK2)
    circle(px + pw - 70, py + 34, 20, (255, 220, 140))
    # skyline towers
    towers = [(0, 90, 60, 110), (64, 60, 54, 140), (122, 100, 66, 100),
              (192, 50, 58, 150), (254, 84, 56, 116), (314, 64, 60, 136),
              (378, 96, 58, 104), (440, 70, 30, 130)]
    for tx, ty, tw, th in towers:
        fill_rect(px + tx, py + ph - th - 52, tw, th, (40, 36, 52))
        for wy in range(py + ph - th - 40, py + ph - 60, 22):
            for wx in range(px + tx + 8, px + tx + tw - 8, 18):
                fill_rect(wx, wy, 7, 9, (255, 220, 120))
    ground_y = py + ph - 52
    fill_rect(px, ground_y, pw, 52, (60, 50, 44))
    # three flags: red, stars-and-stripes, white-blue-red
    flag_x = [px + 60, px + pw // 2 - 15, px + pw - 110]
    flag_cols = [(RED, RED, RED), (RED, (255, 255, 255), (40, 60, 160)),
                 ((255, 255, 255), (40, 60, 160), RED)]
    for fx, cols in zip(flag_x, flag_cols):
        vline(fx, py + 18, 74, INK, 3)
        for i, col in enumerate(cols):
            fill_rect(fx + 3, py + 18 + i * 12, 44, 12, col)
    # three figures seated at a table
    for fx in (px + 90, px + pw // 2 - 20, px + pw - 150):
        circle(fx + 20, ground_y + 8, 9, (250, 220, 190))
        fill_rect(fx + 8, ground_y + 18, 24, 26, INK)
    fill_rect(px + 60, ground_y + 36, pw - 120, 6, (150, 110, 60))


def scene_rwanda(px, py, pw, ph):
    fill_rect(px, py, pw, ph, SKY)
    # small Europe shape, top left
    poly_fill([(px + 30, py + 20), (px + 96, py + 14), (px + 110, py + 44),
               (px + 88, py + 66), (px + 44, py + 62), (px + 26, py + 40)],
              (120, 170, 220))
    draw_text(px + 44, py + 34, "EU", 2, INK)
    # Africa shape
    africa = [(px + 150, py + 30), (px + 330, py + 22), (px + 400, py + 52),
              (px + 380, py + 110), (px + 330, py + 150), (px + 300, py + 175),
              (px + 262, py + 150), (px + 230, py + 120), (px + 180, py + 100),
              (px + 150, py + 66)]
    poly_fill(africa, TAN)
    # Rwanda star, east-central Africa
    sx, sy = px + 315, py + 92
    star = [(sx, sy - 14), (sx + 4, sy - 4), (sx + 14, sy - 4), (sx + 6, sy + 3),
            (sx + 9, sy + 13), (sx, sy + 7), (sx - 9, sy + 13), (sx - 6, sy + 3),
            (sx - 14, sy - 4), (sx - 4, sy - 4)]
    poly_fill(star, RED)
    draw_text(px + 330, py + 104, "RWANDA", 2, INK)
    # arrow flying in from Europe to Rwanda
    line(px + 110, py + 44, sx - 16, sy - 8, RED, 3)
    poly_fill([(sx - 16, sy - 8), (sx - 34, sy - 16), (sx - 30, sy + 2)], RED)
    # five flag chips
    chips = [("DE", (0, 0, 0)), ("DK", RED), ("AT", RED),
             ("GR", (40, 90, 180)), ("NL", (200, 40, 32))]
    chip_y = py + ph - 34
    for i, (code, col) in enumerate(chips):
        cx = px + 24 + i * 88
        fill_rect(cx, chip_y, 76, 26, (255, 255, 255))
        for t in range(2):
            vline(cx + t, chip_y, 26, INK)
            vline(cx + 75 - t, chip_y, 26, INK)
            hline(cx, chip_y + t, 76, INK)
            hline(cx, chip_y + 25 - t, 76, INK)
        fill_rect(cx + 4, chip_y + 4, 14, 18, col)
        draw_text(cx + 24, chip_y + 6, code, 2, INK)


def footer():
    y0 = 852
    hline(24, y0, W - 48, INK, 3)
    draw_centered(W // 2, y0 + 12, "ALSO IN THE NEWS", 3, INK)
    items = [
        "- PENTAGON FAILS ITS AUDIT FOR A NINTH YEAR",
        "- VULCAN ROCKET LOSS DESTROYS 40 LEO SATELLITES",
        "- JPMORGAN BLAMES A SOFTWARE BUG FOR MONDAY'S OUTAGE",
    ]
    for i, item in enumerate(items):
        draw_text(48, y0 + 52 + i * 26, item, 2, INK)


def panel(px, py, pw, ph, scene, headline, caption):
    fill_rect(px, py, pw, ph, PAPER2)
    for t in range(3):
        vline(px + t, py, ph, INK)
        vline(px + pw - 1 - t, py, ph, INK)
        hline(px, py + t, pw, INK)
        hline(px, py + ph - 1 - t, pw, INK)
    scene_h = int(ph * 0.58)
    scene(px + 6, py + 6, pw - 12, scene_h)
    hy = py + 6 + scene_h + 14
    draw_centered(px + pw // 2, hy, headline, 3, INK)
    cy = hy + 7 * 3 + 12
    draw_wrapped(px + pw // 2, cy, caption, 2, INK, pw - 28)


def masthead():
    draw_centered(W // 2, 30, "THE WORLD IN ONE PICTURE", 5, INK)
    hline(24, 96, W - 48, INK, 3)
    draw_centered(W // 2, 108, "TUESDAY 17 NOVEMBER 2026", 4, INK)
    hline(24, 152, W - 48, INK, 3)


def main():
    fill_rect(0, 0, W, H, CREAM)
    for t in range(8):
        vline(t, 0, H, INK)
        vline(W - 1 - t, 0, H, INK)
        hline(0, t, W, INK)
        hline(0, H - 1 - t, W, INK)
    masthead()
    gx, gy = 24, 168
    pw, ph = 480, 330
    panel(gx, gy, pw, ph, scene_kerch, "KERCH BRIDGE HIT",
          "UKRAINE COLLAPSES THE KERCH ROAD SPAN; RUSSIA HITS KYIV BRIDGES.")
    panel(gx + pw + 16, gy, pw, ph, scene_hormuz, "FIRE NEAR HORMUZ",
          "TWO TANKERS HIT MINES AND CATCH FIRE; THIRD US CARRIER ARRIVES.")
    panel(gx, gy + ph + 16, pw, ph, scene_meet, "XI, TRUMP, PUTIN MEET",
          "FIRST THREE-WAY TALKS SET FOR THURSDAY IN SHENZHEN; TRUMP IN MANILA.")
    panel(gx + pw + 16, gy + ph + 16, pw, ph, scene_rwanda, "RWANDA RETURNS HUB",
          "FIVE EUROPEAN STATES PLAN A JOINT HUB FOR REJECTED ASYLUM SEEKERS.")
    footer()
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        write_png(os.path.join(outdir, "entry.png"))
    else:
        write_png(os.path.join(here, "entry.png"))


if __name__ == "__main__":
    main()
