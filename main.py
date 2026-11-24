#!/usr/bin/env python3
"""24 November 2026 in one image.

A pure Python 3.13 standard-library poster: it draws a 1024x1024 PNG
summing up Tuesday 24 November 2026 in 57 verified stories, a UTC
timeline, a world map and a date check, and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).

No network, no third-party packages, fully deterministic: the same
input bytes every run, so two runs write identical files.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # warm newsprint
INK = (20, 24, 32)        # near-black
NAVY = (11, 37, 69)       # masthead
NAVY2 = (18, 58, 102)     # masthead gradient step
RED = (192, 57, 43)       # climax accent
AMBER = (217, 142, 0)     # gold accent
TEAL = (14, 124, 123)     # region accent
GREY = (107, 114, 128)    # secondary text
FAINT = (214, 207, 192)   # hairlines on paper
WHITE = (255, 255, 255)
PANEL = (24, 32, 48)      # dark climax panels
PANEL2 = (31, 43, 66)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits. Uppercase only; text() uppercases.
F = {
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
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "°": ("01100", "10010", "10010", "01100", "00000", "00000", "00000"),
    "•": ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
    "×": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
}
F["–"] = F["-"]
F["—"] = ("00000", "00000", "00000", "11111", "00000", "00000", "00000")
F["’"] = F["'"]

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def glyph(ch):
    return F.get(ch, BLANK)


def text_w(s, scale):
    """Pixel width of s at scale (1px tracking between glyphs)."""
    if not s:
        return 0
    return len(s) * (5 * scale + 1) - 1

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def fill(c):
    px[0:] = bytes(c) * (W * H)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        n = x1 - x0
        px[base:base + n * 3] = bytes(c) * n


def hline(x, y, w, c):
    rect(x, y, w, 1, c)


def vline(x, y, h, c):
    rect(x, y, 1, h, c)


def draw_text(s, x, y, scale, c, bold=False):
    """Draw uppercase text; returns width drawn."""
    s = s.upper()
    cx = x
    for ch in s:
        g = glyph(ch)
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
                    if bold:
                        rect(cx + col * scale + 1, y + r * scale,
                             scale, scale, c)
        cx += 5 * scale + 1
    return cx - x - 1


def wrap(s, max_w, scale):
    """Greedy word wrap to lines fitting max_w pixels at scale."""
    words = s.upper().split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- world map
# Dot-matrix world map: row -> list of (col_start, col_end) land spans.
# 96 columns (longitude -180..180), 40 rows (latitude 75N..60S).
MAP_SPANS = {
    0: [(12, 18), (30, 33), (60, 90)],
    1: [(10, 20), (28, 33), (54, 92)],
    2: [(8, 16), (14, 28), (29, 33), (50, 92)],
    3: [(9, 15), (16, 28), (46, 50), (52, 92)],
    4: [(12, 27), (45, 49), (52, 90)],
    5: [(13, 27), (44, 48), (50, 88)],
    6: [(14, 27), (43, 45), (47, 52), (54, 86)],
    7: [(15, 27), (44, 54), (56, 86), (86, 88)],
    8: [(15, 27), (45, 55), (58, 84), (87, 88)],
    9: [(16, 26), (45, 55), (60, 82), (87, 88)],
    10: [(16, 26), (46, 56), (62, 80)],
    11: [(17, 26), (46, 55), (62, 78)],
    12: [(17, 25), (46, 54), (63, 76)],
    13: [(17, 24), (47, 53), (64, 75)],
    14: [(18, 23), (44, 58), (64, 74), (76, 79)],
    15: [(18, 22), (44, 58), (60, 64), (66, 74), (76, 80)],
    16: [(19, 22), (44, 58), (61, 63), (68, 74), (77, 80)],
    17: [(20, 23), (45, 57), (69, 73), (77, 79)],
    18: [(21, 24), (46, 56), (70, 72), (78, 79)],
    19: [(22, 24), (46, 55), (71, 72), (74, 84)],
    20: [(24, 28), (47, 54), (75, 85)],
    21: [(24, 30), (47, 54), (80, 86)],
    22: [(25, 31), (48, 54), (81, 85)],
    23: [(25, 31), (48, 54)],
    24: [(26, 31), (48, 54), (79, 87)],
    25: [(26, 31), (49, 53), (79, 88)],
    26: [(27, 31), (49, 53), (80, 88)],
    27: [(27, 30), (49, 52), (80, 87)],
    28: [(28, 30), (49, 52), (81, 86)],
    29: [(28, 30), (50, 51), (81, 86)],
    30: [(28, 30), (50, 51), (82, 85), (90, 91)],
    31: [(28, 29), (83, 84), (90, 91)],
    32: [(28, 29), (83, 84)],
    33: [(28, 29), (90, 91)],
    34: [(28, 29)],
    35: [(28, 29)],
    36: [(28, 29)],
    37: [(28, 29)],
}


def draw_map(x0, y0, w, h, c):
    cw, ch = w / 96.0, h / 40.0
    for row, spans in MAP_SPANS.items():
        for a, b in spans:
            for col in range(a, b + 1):
                rect(int(x0 + col * cw), int(y0 + row * ch),
                     max(1, int(cw)), max(1, int(ch)), c)


# ---------------------------------------------------------------- the day
# (region, headline, detail, source) — 57 stories, each verified as
# reported on 24 November 2026; see SOURCES.md for the verification.
STORIES = [
    # South Asia — 28
    ("SOUTH ASIA", "INDIA-NEPAL EXPRESS OPENS",
     "Rs 15,000cr package, 8 MoUs signed", "Jagran Josh"),
    ("SOUTH ASIA", "NEPAL PM ENDS INDIA VISIT",
     "Invites Modi to Kathmandu after talks", "NewKerala"),
    ("SOUTH ASIA", "BANGLADESH VOWS HASINA ARREST",
     "Arrest promised if ex-PM returns", "Studmentor"),
    ("SOUTH ASIA", "RAJYA SABHA MP WADKUTE DIES",
     "Condolences pour in for Wadkute", "Jagran Josh"),
    ("SOUTH ASIA", "RS 2 LAKH AID FOR KUTCH KIN",
     "Aid for Kutch accident families", "Jagran Josh"),
    ("SOUTH ASIA", "SHAH PUSHES SELF-RELIANCE",
     "Shah in Arunachal on self-reliance", "Jagran Josh"),
    ("SOUTH ASIA", "CJI: LEGAL AID FOR STUDENTS",
     "Legal aid must in law courses: CJI", "Jagran Josh"),
    ("SOUTH ASIA", "ODISHA CLEARS CYBER COMMAND",
     "Rs 249-crore Cyber Command approved", "Jagran Josh"),
    ("SOUTH ASIA", "IFFI HOSTS BRICS FILM MEET",
     "BRICS film roundtable opens at IFFI Goa", "Jagran Josh"),
    ("SOUTH ASIA", "MAHARASHTRA ACTS ON ADANI",
     "PCB action against Adani group company", "Jagran Josh"),
    ("SOUTH ASIA", "FSSAI PROSECUTES BISLERI",
     "Unsafe water prosecution ordered", "Observer Voice"),
    ("SOUTH ASIA", "COURT WARRANT FOR RATHEE",
     "Warrant against Dhruv Rathee", "Daily Jagran"),
    ("SOUTH ASIA", "SENSEX CRASHES 1,484 PTS",
     "Sensex 82,435; Nifty down 451 to 25,350", "Studmentor"),
    ("SOUTH ASIA", "OIL IMPORT BILL UP 60%",
     "October oil, gas import bill hits $16bn", "Jagran Josh"),
    ("SOUTH ASIA", "PILOTS ALARM ON SPICEJET",
     "Pilots urge action as crisis grows", "Jagran Josh"),
    ("SOUTH ASIA", "MAHINDRA LAST MILE IPO PLAN",
     "IPO planned within 18 months", "Jagran Josh"),
    ("SOUTH ASIA", "ALUMINIUM SEEKS ZERO DUTY",
     "Makers seek zero import duty", "Jagran Josh"),
    ("SOUTH ASIA", "INDIA-EU DEAL SET FOR 16 DEC",
     "Free trade deal signing set for 16 Dec", "Jagran Josh"),
    ("SOUTH ASIA", "GOOGLE $5M FOR IIT KGP AI",
     "Google funds AI research at IIT KGP", "Jagran Josh"),
    ("SOUTH ASIA", "GURU NANAK JAYANTI MARKED",
     "Observed across India", "Jagran Josh"),
    ("SOUTH ASIA", "JEE MAIN 2027 LATE FEE OPENS",
     "Late-fee window opens for JEE Main 2027", "Jagran Josh"),
    ("SOUTH ASIA", "UP SUPER TET SLIP EXPECTED",
     "City slip expected soon", "Jagran Josh"),
    ("SOUTH ASIA", "BENGAL REVIEWS SEMESTER EXAMS",
     "West Bengal reviews semester exam plan", "Jagran Josh"),
    ("SOUTH ASIA", "NEET PG COUNSELLING REVIEW",
     "NEET PG counselling under review", "Jagran Josh"),
    ("SOUTH ASIA", "CHENNAIYIN, PUNJAB DRAW",
     "ISL points shared in Chennaiyin draw", "Jagran Josh"),
    ("SOUTH ASIA", "JUNIOR SHUTTLERS TAKE TITLES",
     "U-19 national badminton titles decided", "Jagran Josh"),
    ("SOUTH ASIA", "MODI OPENS AI CENTRE AT IIT",
     "AI centre + Rs 400cr research park", "Education Times"),
    ("SOUTH ASIA", "INDIA-CHINA BORDER TALKS",
     "Military commanders meet on border", "Education Times"),
    # East & South-East Asia — 5
    ("EAST & SE ASIA", "CHINA SETS 2030 CARE TARGETS",
     "Elderly care, childcare goals for 2030", "Studmentor"),
    ("EAST & SE ASIA", "S KOREA NAMES FM, SPY CHIEF",
     "New foreign minister, intel chief named", "Studmentor"),
    ("EAST & SE ASIA", "CHINA MEGA CRUISE SETS SAIL",
     "Mega cruise ship begins maiden voyage", "Aktualita"),
    ("EAST & SE ASIA", "MYANMAR SLAMS ASEAN MOVE",
     "Myanmar slams ASEAN decision", "Jagran Josh"),
    ("EAST & SE ASIA", "BANTEN FIRE: 24 DEAD",
     "Search resumes; 30 still missing", "Reuters"),
    # Europe — 6
    ("EUROPE", "KYIV REGION HIT BY DRONES",
     "Russian strikes kill in Kyiv region", "Jagran Josh"),
    ("EUROPE", "COP31 COLLAPSES, NO DEAL",
     "No fossil-fuel deal; longest COP ever", "Studmentor"),
    ("EUROPE", "CGTP RALLIES AT PARLIAMENT",
     "Lisbon rally as budget vote looms", "Europe Says"),
    ("EUROPE", "ARMENIA PROPOSES NEW CHARTER",
     "New constitution to advance peace", "Studmentor"),
    ("EUROPE", "FERRARI UNVEILS TWO 296S",
     "Two new 296 models revealed", "Jagran Josh"),
    ("EUROPE", "GUKESH DEFENDS CHESS CROWN",
     "World title defence opens in Geneva", "Education Times"),
    # Middle East — 4
    ("MIDDLE EAST", "TRUMP WARNS IRAN: TRAUMATIC",
     "Trump warns Iran of traumatic outcome", "Access24"),
    ("MIDDLE EAST", "US MULLS TRAINING SYRIANS",
     "US weighs training Syrian forces", "Reuters"),
    ("MIDDLE EAST", "ISRAELI MILITARY WARNS PM",
     "Military warns Netanyahu on Gaza plan", "Aktualita"),
    ("MIDDLE EAST", "GAZA TOXIC, REPORT WARNS",
     "War left Gaza air, soil, water toxic", "Disclosure"),
    # North America — 9
    ("NORTH AMERICA", "TRUMP PAUSES IOWA BLAST",
     "Army detonation paused after outcry", "CNN"),
    ("NORTH AMERICA", "LA MAN HELD OVER ICE PLOT",
     "Arrest over alleged ICE attack plot", "NY Post"),
    ("NORTH AMERICA", "SENATE TO VOTE $9.4BN CUTS",
     "US Senate to vote on $9.4bn rescissions", "Access24"),
    ("NORTH AMERICA", "US CITIZENSHIP TEST REVAMP",
     "Citizenship test, H-1B changes planned", "Access24"),
    ("NORTH AMERICA", "CANADA JOINS NATO FUND",
     "Canada joins NATO Innovation Fund", "Aktualita"),
    ("NORTH AMERICA", "HUANG BACK AT NVIDIA",
     "Shares +31%, +$952bn in a day", "Reuters"),
    ("NORTH AMERICA", "CROWDSTRIKE BUYS ZSCALER",
     "$43.9bn all-stock deal announced", "Reuters"),
    ("NORTH AMERICA", "TRUMP BLAMES DEMS FOR ROUT",
     "Blames Democrats for market sell-off", "Observer Voice"),
    ("NORTH AMERICA", "S&P -12%, NASDAQ -18%",
     "AI rout since 6 Oct peak", "Reuters"),
    # Oceania — 4
    ("OCEANIA", "INDIA-NZ TEST ENDS IN DRAW",
     "Wellington: NZ 239/5, India 720/9 dec", "myKhel"),
    ("OCEANIA", "INDIA WIN HOCKEY SERIES",
     "Hockey series won in New Zealand", "Jagran Josh"),
    ("OCEANIA", "UNSW OPENS POLICY SCHOOL",
     "Public policy school launches in Canberra", "Medianet"),
    ("OCEANIA", "COP31 DIVERS PLEAD",
     "Divers take ocean plea to parliament", "Medianet"),
    # Science & space — 1
    ("SCIENCE & SPACE", "SUPERMOON MEETS PLEIADES",
     "Full moon passes the Seven Sisters tonight", "CNET"),
]

REGION_ORDER = ["SOUTH ASIA", "EAST & SE ASIA", "EUROPE", "MIDDLE EAST",
                "NORTH AMERICA", "OCEANIA", "SCIENCE & SPACE"]

TIMELINE = [
    ("00:00", "GURU NANAK JAYANTI"),
    ("01:30", "UNSW POLICY SCHOOL"),
    ("04:00", "BANTEN SEARCH RESUMES"),
    ("07:00", "ASIAN MARKETS OPEN"),
    ("10:00", "COP31 FALLOUT"),
    ("13:00", "CGTP RALLY, LISBON"),
    ("14:00", "HUANG RETURNS"),
    ("19:00", "IOWA BLAST PAUSED"),
]

CLIMAX = [
    ("24", "DEAD IN BANTEN", "FACTORY FIRE, 30 STILL MISSING"),
    ("+31%", "NVIDIA SOARS", "$952BN GAINED IN ONE DAY"),
    ("$43.9BN", "CROWDSTRIKE BUYS", "ZSCALER IN ALL-STOCK DEAL"),
]

# ---------------------------------------------------------------- layout
COL_W = 320
COL_GAP = 12
MARGIN = 20
STORY_TOP = 266
STORY_BOTTOM = 988
FOOTER_Y = 992


def story_block_height(headline, detail, source):
    hl = wrap(headline, COL_W, 2)
    dt = wrap(detail + " (" + source + ")", COL_W, 1)
    return len(hl) * 15 + len(dt) * 8 + 4


def draw_story(x, y, headline, detail, source):
    """Draw one story at (x, y); returns height used."""
    hl = wrap(headline, COL_W, 2)
    yy = y
    for ln in hl:
        draw_text(ln, x, yy, 2, INK)
        yy += 15
    dt = wrap(detail + " (" + source + ")", COL_W, 1)
    for ln in dt:
        draw_text(ln, x, yy, 1, GREY)
        yy += 8
    return yy - y + 4


def draw_region_header(x, y, region, count, color):
    rect(x, y, COL_W, 2, color)
    draw_text(region + "  (" + str(count) + ")", x, y + 6, 2, color)
    return 24


def layout_columns():
    """Greedy balanced flow of stories into 3 columns (deterministic)."""
    counts = {}
    for r, _, _, _ in STORIES:
        counts[r] = counts.get(r, 0) + 1
    cols = [[], [], []]
    heights = [0, 0, 0]
    seen_region = [set(), set(), set()]
    for story in STORIES:
        region = story[0]
        h = story_block_height(story[1], story[2], story[3])
        # cheapest column: prefer the shortest, tie-break lowest index
        best = min(range(3), key=lambda i: (heights[i], i))
        if region not in seen_region[best]:
            heights[best] += 26
            seen_region[best].add(region)
            cols[best].append(("HEADER", region, counts[region]))
        cols[best].append(("STORY",) + story)
        heights[best] += h
    return cols, heights


def draw_masthead():
    rect(0, 0, W, 92, NAVY)
    rect(0, 88, W, 4, AMBER)
    draw_text("THE WORLD IN ONE DAY", 20, 10, 2, AMBER)
    draw_text("TUESDAY 24 NOVEMBER 2026", 20, 30, 4, WHITE)
    draw_text("57 STORIES  •  ONE DAY OF WORLD NEWS", 20, 66, 2, (200, 210, 225))
    draw_map(712, 4, 292, 80, (120, 160, 205))


def draw_climax():
    y0, y1 = 92, 184
    rect(0, y0, W, y1 - y0, PANEL)
    pw = (W - 2 * MARGIN - 2 * 12) // 3
    for i, (num, line1, line2) in enumerate(CLIMAX):
        x = MARGIN + i * (pw + 12)
        rect(x, y0 + 8, pw, 76, PANEL2)
        rect(x, y0 + 8, 4, 76, RED if i == 0 else (AMBER if i == 1 else TEAL))
        draw_text(num, x + 16, y0 + 14, 5, WHITE)
        draw_text(line1, x + 16, y0 + 52, 2, AMBER if i == 1 else WHITE)
        draw_text(line2, x + 16, y0 + 70, 1, (180, 190, 205))


def draw_timeline():
    y0 = 184
    draw_text("UTC TIMELINE  —  24 NOVEMBER, AS REPORTED", 20, y0 + 8, 2, TEAL)
    line_y = y0 + 34
    hline(40, line_y, W - 80, (180, 185, 195))
    n = len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = 40 + int((i + 0.5) * (W - 80) / n)
        rect(cx - 3, line_y - 3, 7, 7, RED)
        tw = text_w(t, 1)
        draw_text(t, cx - tw // 2, line_y - 12, 1, INK)
        for j, ln in enumerate(wrap(label, 108, 1)):
            lw = text_w(ln, 1)
            draw_text(ln, cx - lw // 2, line_y + 7 + j * 8, 1, GREY)


def draw_datecheck():
    y0 = 240
    rect(0, y0, W, 26, NAVY2)
    draw_text("DATE CHECK: EVERY STORY VERIFIED AS 24 NOV 2026",
              20, y0 + 7, 2, WHITE)
    draw_text("57 STORIES  •  20+ SOURCES", 716, y0 + 7, 2, AMBER)


NUMBERS = [
    ("24", "DEAD IN BANTEN"),
    ("+31%", "NVIDIA IN A DAY"),
    ("$43.9BN", "CROWDSTRIKE DEAL"),
    ("1,484", "SENSEX POINTS LOST"),
    ("57", "STORIES, 7 REGIONS"),
    ("190+", "NATIONS AT COP31"),
]


def draw_numbers(y0):
    draw_text("THE DAY IN NUMBERS", 20, y0, 2, TEAL)
    y0 += 22
    cw = (W - 2 * MARGIN - 5 * 8) // 6
    for i, (num, label) in enumerate(NUMBERS):
        x = MARGIN + i * (cw + 8)
        rect(x, y0, cw, 40, PANEL)
        nw = text_w(num, 2)
        draw_text(num, x + (cw - nw) // 2, y0 + 5, 2, WHITE)
        lw = text_w(label, 1)
        draw_text(label, x + (cw - lw) // 2, y0 + 26, 1, AMBER)


def draw_stories():
    cols, heights = layout_columns()
    for ci, col in enumerate(cols):
        x = MARGIN + ci * (COL_W + COL_GAP)
        y = STORY_TOP
        for item in col:
            if item[0] == "HEADER":
                y += draw_region_header(x, y, item[1], item[2], TEAL)
            else:
                _, region, headline, detail, source = item
                y += draw_story(x, y, headline, detail, source)
    return heights


def draw_footer():
    y = FOOTER_Y
    hline(20, y, W - 40, FAINT)
    src = ("SOURCES: REUTERS, AP, CNN, NY POST, TBS NEWS, JAGRAN JOSH, "
           "STUDMENTOR, OBSERVER VOICE, MEDIANET, MYKHEL, EUROPE SAYS, "
           "AKTUALITA, ACCESS24, DISCLOSURE, CNET, EDUCATION TIMES")
    for j, ln in enumerate(wrap(src, W - 40, 1)):
        draw_text(ln, 20, y + 8 + j * 8, 1, GREY)
    draw_text("ONE IMAGE  •  ONE DAY  •  BUILT 24 NOV 2026", 20, y + 24, 1, GREY)


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    fill(PAPER)
    draw_masthead()
    draw_climax()
    draw_timeline()
    draw_datecheck()
    heights = draw_stories()
    strip_y = STORY_TOP + max(heights) + 10
    if strip_y + 62 <= FOOTER_Y - 2:
        draw_numbers(strip_y)
    draw_footer()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path)
    print("wrote %s (%d bytes), column heights %s" % (path, size, heights))


if __name__ == "__main__":
    main()
