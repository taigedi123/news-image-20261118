#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news image (1024x1024 PNG).

Deterministic: same bytes on every run. Run: python3 draw.py
Writes entry.png next to this file.
"""
import hashlib
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
W, H = 1024, 1024

NOTO = "/usr/share/fonts/truetype/noto/"
SERIF_B = NOTO + "NotoSerif-Bold.ttf"
SANS_B = NOTO + "NotoSans-Bold.ttf"
SANS_R = NOTO + "NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap to lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, f, max_w, max_lines):
    """Wrap text; shrink font until it fits in max_lines (min size 14)."""
    size = f.size
    while size > 14:
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 2
        f = font(f.path, size)
    return wrap(d, text, f, max_w), f


def card(d, x0, y0, x1, y1, tag, tag_color):
    """White rounded card with a coloured tag bar on top."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill="white",
                        outline="#D9D2BE", width=2)
    d.rounded_rectangle([x0, y0, x1, y0 + 42], radius=14, fill=tag_color)
    d.rectangle([x0, y0 + 28, x1, y0 + 42], fill=tag_color)
    d.rectangle([x0, y0, x1, y0 + 14], fill=tag_color)
    d.text((x0 + 18, y0 + 7), tag, font=font(SANS_B, 23), fill="white")


def text_block(d, x, y, w, text, f, max_lines, color, leading=1.28):
    """Draw wrapped text; return bottom y. Shrinks font to fit max_lines."""
    lines, f = fit_lines(d, text, f, w, max_lines)
    yy = y
    for ln in lines:
        d.text((x, yy), ln, font=f, fill=color)
        yy += int(f.size * leading)
    return yy


# ---------------------------------------------------------------- icons
def icon_summit(d, cx, cy, s=1.0):
    """Three flag circles: CN, US, RU over a green arc."""
    cols = [("#C8102E", "CN"), ("#1D4ED8", "US"), ("#6B7280", "RU")]
    r = int(31 * s)
    gap = int(70 * s)
    for i, (c, lab) in enumerate(cols):
        x = cx + (i - 1) * gap
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=c, outline="white",
                  width=3)
        f = font(SANS_B, int(22 * s))
        tw = d.textlength(lab, font=f)
        d.text((x - tw / 2, cy - int(14 * s)), lab, font=f, fill="white")
    d.arc([cx - int(86 * s), cy + int(16 * s), cx + int(86 * s),
           cy + int(82 * s)], start=200, end=340, fill="#166534", width=4)


def icon_bridge(d, cx, cy, s=1.0):
    """Bridge with a collapsed middle span falling into the strait."""
    u = s
    # arch over the deck between the towers
    d.arc([cx - 70 * u, cy - 52 * u, cx + 70 * u, cy + 6 * u],
          start=180, end=360, fill="#B45309", width=int(5 * u))
    # towers stop at the deck (T-junction, no cross)
    d.line([cx - 70 * u, cy - 38 * u, cx - 70 * u, cy], fill="#1F2937",
           width=int(7 * u))
    d.line([cx + 70 * u, cy - 38 * u, cx + 70 * u, cy], fill="#1F2937",
           width=int(7 * u))
    # intact deck segments
    d.line([cx - 100 * u, cy, cx - 26 * u, cy], fill="#1F2937",
           width=int(7 * u))
    d.line([cx + 26 * u, cy, cx + 100 * u, cy], fill="#1F2937",
           width=int(7 * u))
    # fallen span, tilted down into the water
    d.line([cx - 26 * u, cy, cx + 24 * u, cy + 34 * u], fill="#B91C1C",
           width=int(7 * u))
    # water line under the fallen tip
    d.line([cx + 8 * u, cy + 44 * u, cx + 46 * u, cy + 44 * u],
           fill="#2563EB", width=int(4 * u))


def icon_missile(d, cx, cy, s=1.0):
    """Missile on a 45-degree climb, with flame and burst."""
    u = (0.7071, -0.7071)   # nose direction
    v = (0.7071, 0.7071)    # perpendicular
    def pt(au, bv):
        return (cx + (au * u[0] + bv * v[0]) * s,
                cy + (au * u[1] + bv * v[1]) * s)
    # body
    body = [pt(62, 0), pt(18, 11), pt(-42, 11), pt(-42, -11), pt(18, -11)]
    d.polygon(body, fill="#1F2937")
    # fins at the tail
    d.polygon([pt(-42, 11), pt(-62, 24), pt(-52, 6)], fill="#1F2937")
    d.polygon([pt(-42, -11), pt(-62, -24), pt(-52, -6)], fill="#1F2937")
    # flame
    d.polygon([pt(-42, 7), pt(-72, 0), pt(-42, -7)], fill="#F59E0B")
    # burst star at the nose
    bx, by = pt(78, 0)
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = (24 if i % 2 == 0 else 10) * s
        pts.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
    d.polygon(pts, fill="#DC2626")
    d.ellipse([bx - 6 * s, by - 6 * s, bx + 6 * s, by + 6 * s],
              fill="#F59E0B")


def icon_ballot(d, cx, cy, s=1.0):
    """Ballot box with a checked paper."""
    d.rectangle([cx - 34 * s, cy - 62 * s, cx + 30 * s, cy - 6 * s],
                fill="white", outline="#1F2937", width=int(4 * s))
    d.line([cx - 22 * s, cy - 34 * s, cx - 6 * s, cy - 16 * s,
            cx + 20 * s, cy - 52 * s], fill="#15803D", width=int(7 * s))
    d.rectangle([cx - 62 * s, cy - 6 * s, cx + 62 * s, cy + 58 * s],
                fill="#1D4ED8", outline="#1E3A8A", width=int(3 * s))
    d.rectangle([cx - 26 * s, cy - 2 * s, cx + 26 * s, cy + 6 * s],
                fill="#111827")
    f = font(SANS_B, int(22 * s))
    d.text((cx - 34 * s, cy + 20 * s), "VOTE", font=f, fill="white")


def icon_virus(d, cx, cy, s=1.0):
    """Spiked virus particle."""
    for i in range(12):
        ang = 2 * math.pi * i / 12
        x1 = cx + 34 * s * math.cos(ang)
        y1 = cy + 34 * s * math.sin(ang)
        x2 = cx + 52 * s * math.cos(ang)
        y2 = cy + 52 * s * math.sin(ang)
        d.line([x1, y1, x2, y2], fill="#7E22CE", width=int(6 * s))
        d.ellipse([x2 - 7 * s, y2 - 7 * s, x2 + 7 * s, y2 + 7 * s],
                  fill="#7E22CE")
    d.ellipse([cx - 36 * s, cy - 36 * s, cx + 36 * s, cy + 36 * s],
              fill="#991B1B", outline="#7F1D1D", width=3)
    d.ellipse([cx - 16 * s, cy - 20 * s, cx + 2 * s, cy - 2 * s],
              fill="#DC2626")
    d.ellipse([cx + 4 * s, cy + 6 * s, cx + 18 * s, cy + 20 * s],
              fill="#DC2626")


# ---------------------------------------------------------------- build
def row_card(d, x0, y0, x1, y1, tag, tag_color, icon, head, deck,
             icon_s=0.78, icon_cy=92):
    card(d, x0, y0, x1, y1, tag, tag_color)
    icon(d, x0 + 92, y0 + icon_cy, s=icon_s)
    text_block(d, x0 + 178, y0 + 50, x1 - x0 - 196, head,
               font(SANS_B, 30), 2, "#111827", leading=1.18)
    text_block(d, x0 + 16, y0 + 140, x1 - x0 - 32, deck,
               font(SANS_R, 20), 3, "#3F4756", leading=1.32)


def build():
    img = Image.new("RGB", (W, H), "#F6F1E3")
    d = ImageDraw.Draw(img)

    # ---- header ------------------------------------------------------
    d.rectangle([0, 0, W, 150], fill="#14264A")
    d.text((32, 14), "THE WORLD IN ONE DAY  •  FIVE STORIES",
           font=font(SANS_B, 29), fill="#E8B93C")
    df = font(SERIF_B, 62)
    date = "WEDNESDAY 18 NOVEMBER 2026"
    while d.textlength(date, font=df) > 960 and df.size > 40:
        df = font(SERIF_B, df.size - 2)
    d.text((32, 46), date, font=df, fill="white")
    d.text((32, 120), "The day's most consequential world news, at a glance",
           font=font(SANS_R, 23), fill="#C9D2E0")
    d.rectangle([0, 150, W, 156], fill="#E8B93C")

    # ---- lead story: Shenzhen summit ---------------------------------
    card(d, 32, 170, 992, 388, "TOP STORY  •  SHENZHEN SUMMIT", "#B91C1C")
    icon_summit(d, 122, 296, s=0.9)
    text_block(d, 252, 220, 712,
               "Trump lands in Shenzhen as Xi and Putin meet",
               font(SANS_B, 40), 2, "#111827", leading=1.18)
    text_block(d, 252, 320, 712,
               "Xi greets Trump at the airport. The three leaders hold "
               "their first trilateral summit on Thursday.",
               font(SANS_R, 22), 2, "#3F4756", leading=1.32)

    # ---- row 2 -------------------------------------------------------
    row_card(d, 32, 402, 502, 632, "UKRAINE", "#1D4ED8", icon_bridge,
             "Kerch Bridge hit again — span falls",
             "Ukraine strikes the bridge for a second day; part of its "
             "road span and an arch fall into the strait.",
             icon_s=0.78, icon_cy=88)
    row_card(d, 522, 402, 992, 632, "MIDDLE EAST", "#166534", icon_missile,
             "US jets hit Iran; Iran fires back",
             "US jets hit a Revolutionary Guard missile site on Qeshm "
             "Island; Iran fires drones at Bahrain and Kuwait.",
             icon_s=0.68, icon_cy=96)

    # ---- row 3 -------------------------------------------------------
    row_card(d, 32, 646, 502, 876, "UNITED STATES", "#6D28D9", icon_ballot,
             "Peltola wins Alaska Senate seat",
             "Democrat Mary Peltola defeats Republican Dan Sullivan. "
             "Democrats are projected to hold a 56–44 Senate majority.",
             icon_s=0.72, icon_cy=92)
    row_card(d, 522, 646, 992, 876, "HEALTH  •  AFRICA", "#991B1B",
             icon_virus,
             "Ebola in DR Congo tops 11,000 cases",
             "More than 5,400 have died — the toll has doubled in three "
             "months, the second-largest outbreak on record.",
             icon_s=0.75, icon_cy=92)

    # ---- also-today strip --------------------------------------------
    d.rounded_rectangle([32, 890, 992, 962], radius=12, fill="#14264A")
    label = "ALSO TODAY   "
    line1 = "Voyager 1 reaches one light-day from Earth"
    line2 = ("US loses measles elimination status (5,412 cases)  •  "
             "Cyclone Xavier hits the Cook Islands")
    size = 22
    while size > 16:
        bf = font(SANS_B, size)
        sf = font(SANS_R, size)
        w1 = d.textlength(label, font=bf) + d.textlength(line1, font=sf)
        w2 = d.textlength(line2, font=sf)
        if max(w1, w2) <= 928:
            break
        size -= 1
    d.text((48, 892), label, font=bf, fill="#E8B93C")
    d.text((48 + d.textlength(label, font=bf), 892), line1, font=sf,
           fill="white")
    d.text((48, 892 + int(size * 1.35)), line2, font=sf, fill="white")

    # ---- footer ------------------------------------------------------
    ff = font(SANS_R, 18)
    foot = ("Five stories from Wednesday 18 November 2026  •  "
            "Events first reported that day")
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 974), foot, font=ff, fill="#6B7280")

    img.save(OUT, format="PNG")
    return OUT


if __name__ == "__main__":
    path = build()
    data = open(path, "rb").read()
    print(path, len(data), "bytes",
          hashlib.sha256(data).hexdigest())
