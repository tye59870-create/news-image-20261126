#!/usr/bin/env python3
"""Render the 26 November 2026 front page for make.fun news-image-20261126.

High-density newspaper front page: 39 regional stories across 6 regions plus
3 illustrated lead stories, a KPI numbers bar, a world map strip with 6
markers, a UTC timeline bar, a red-bordered DATE CHECK badge, a region
distribution bar, and source labels. 1024x1024, deterministic, PIL only.
"""
import math
from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
BACKGROUND = (251, 247, 238)
FOREGROUND = (20, 20, 20)
ACCENT = (176, 30, 40)
DEEP = (22, 35, 63)
MUTED = (90, 88, 82)
BODY_INK = (46, 44, 40)
WHITE = (255, 255, 255)
MAP_FILL = (178, 198, 214)
MAP_LINE = (70, 95, 120)
KPI_BG = (240, 235, 224)
RULE_LIGHT = (210, 204, 192)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

GUTTER = 36
CONTENT_W = PAGE_W - 2 * GUTTER  # 952
COL_GAP = 14
COL_W = (CONTENT_W - 2 * COL_GAP) // 3  # 308
COL_X = [GUTTER, GUTTER + COL_W + COL_GAP, GUTTER + 2 * (COL_W + COL_GAP)]

LEADS = [
    {
        "kicker": "SPACE  ·  NATO",
        "headline": "RUSSIA'S NUCLEAR SATELLITE ALARMS NATO",
        "deck": (
            'Western intel: Moscow\'s nuclear "Sputnik-S" satellite, stored '
            "near Moscow for years, could launch in 60 days (possibly Dec). "
            "NATO's Rutte vows to defend every inch, including space. "
            "Kremlin denies it."
        ),
        "icon": "satellite",
        "tint": (244, 220, 218),
        "source": "Reuters / NDR-WDR-SZ, Nov 23",
    },
    {
        "kicker": "SPACE  ·  MERCURY",
        "headline": "BEPICOLOMBO REACHES MERCURY AFTER 8 YEARS",
        "deck": (
            "ESA/JAXA BepiColombo enters Mercury orbit on 21 Nov 2026 — only "
            "the second mission ever to do so after NASA's MESSENGER. Two "
            "orbiters separate 9–10 Dec; science begins April 2027."
        ),
        "icon": "planet",
        "tint": (214, 230, 242),
        "source": "AP / Washington Post",
    },
    {
        "kicker": "SPACE  ·  CHINA",
        "headline": "FIRST FOREIGNER ABOARD TIANGONG",
        "deck": (
            "Shenzhou-24 docks 11:56 on 25 Nov; crew enters Tiangong the same "
            "day. Pakistani payload specialist Muhammad Zeeshan Ali is the "
            "first foreign astronaut on the station; returns on Shenzhou-23 "
            "in 5–10 days."
        ),
        "icon": "rocket",
        "tint": (250, 232, 205),
        "source": "Xinhua / Reuters",
    },
]

KPIS = [
    ("60 DAYS", "SPUTNIK-S LAUNCH WINDOW"),
    ("8 YRS", "BEPICOLOMBO'S VOYAGE"),
    ("500,000", "RUSSIAN WAR DEAD (OWN FIGURES)"),
    ("+26%", "UK ENERGY BILLS FROM JAN"),
    ("36%", "BANGLADESH WAGE RISE"),
]

REGIONS = [
    ("ASIA", "9", [
        ("XI PROBE ENSNARES SHANGHAI CHIEF CHEN", None),
        ("S. KOREA MINISTER QUITS OVER EXAM SCANDAL", None),
        ("AUSTRALIA FORCES PLATFORMS TO REMOVE HARMFUL CONTENT", None),
        ("AUSTRALIA-SOLOMON IS. SECURITY PACT", "shield"),
        ("N. KOREA THREATENS SWISS OFFICE", None),
        ("VIETNAM PUSHES GREEN FARMING", None),
        ("S. KOREA TO BOOST EV INDUSTRY", None),
        ("INDIA SPACE ECONOMY $9BN TO $45BN", "rocket"),
        ("IITs ADD 6,000 TECH SEATS", None),
    ]),
    ("MIDDLE EAST", "6", [
        ("IRAN BRACES FOR US BLOCKADE", "ship"),
        ("ISRAEL: IRAN BUILDING CHEMICAL WEAPONS", None),
        ("SWIMMER CROSSES HORMUZ FOR OCEANS", None),
        ("EGYPT: SUEZ REVENUES RECOVERING", None),
        ("ETHIOPIA PUSHES HEALTH INDEPENDENCE", None),
        ("HOUTHI THREAT STILL LOOMS", "flame"),
    ]),
    ("EUROPE", "8", [
        ("EU UNVEILS 22ND RUSSIA SANCTIONS PACKAGE", "shield"),
        ("RUSSIA'S OWN TOLL: NEARLY 500,000 DEAD", None),
        ("FRANCE EYES CRITICAL MINERALS FREEDOM", None),
        ("UK PROBES NUCLEAR TEST LEGACY", None),
        ("POLAND ALARMS OVER AIRSPACE VIOLATIONS", "satellite"),
        ("RUSSIA RAISES DEFENCE SPENDING", None),
        ("UKRAINE-HUNGARY SEEK ECONOMIC TIES", None),
        ("EU PLANS €50BN TECH FUND", None),
    ]),
    ("AMERICAS", "8", [
        ("US CONSUMER CONFIDENCE NEAR 2-YEAR HIGH", None),
        ("CANADA HOLDS INFLATION STRATEGY", None),
        ("PETROBRAS UNVEILS $122BN PLAN", "flame"),
        ("VENEZUELA DEBT: $237.5BN REVEALED", None),
        ("COLOMBIA: 10 YEARS SINCE PEACE DEAL", "globe"),
        ("CARTAGENA HOSTAGES FREED AFTER 17 HRS", None),
        ("US READIES NEW GLOBAL TARIFF PLAN", None),
        ("ABREGO GARCIA LEAVES US FOR SPAIN", None),
    ]),
    ("AFRICA", "4", [
        ("ZIMBABWE ARREST WARRANT FOR MUGABE'S SON", None),
        ("AFRICAN INSURGENTS TURN TO CHEAP DRONES", "flame"),
        ("EGYPT'S SUEZ RECOVERY LIFTS AFRICA TRADE", "ship"),
        ("ETHIOPIA'S HEALTH PUSH DRAWS PRAISE", None),
    ]),
    ("GLOBAL", "4", [
        ("BARBADOS, INDIA PUSH AI GOVERNANCE", None),
        ("UN SEEKS GLOBAL AI SAFETY RULES", "globe"),
        ("REAL MADRID THRASH PSV 5-1", "ball"),
        ("ASTEROID CLOSE-UPS DUE FROM DART FOLLOW-UP", "planet"),
    ]),
]

DIST = [
    ("ASIA", 9),
    ("MIDDLE EAST", 6),
    ("EUROPE", 8),
    ("AMERICAS", 8),
    ("AFRICA", 4),
    ("GLOBAL", 4),
]
DIST_COLORS = [
    (176, 30, 40),
    (214, 110, 30),
    (22, 35, 63),
    (40, 110, 70),
    (120, 70, 140),
    (90, 88, 82),
]

MAP_W, MAP_H = CONTENT_W, 96
# Reference continent polygons scaled cleanly inside MAP_W x MAP_H
CONTINENTS = [
    [(42, 16), (125, 6), (208, 12), (240, 25), (218, 46), (176, 58),
     (145, 78), (94, 82), (52, 58), (32, 33)],
    [(260, 4), (292, 2), (308, 10), (282, 17), (260, 10)],
    [(218, 62), (260, 57), (292, 65), (282, 85), (250, 90), (224, 77)],
    [(446, 12), (488, 6), (520, 15), (510, 29), (478, 33), (456, 25)],
    [(456, 37), (510, 33), (542, 45), (530, 70), (500, 86), (468, 74),
     (452, 53)],
    [(530, 8), (676, 4), (810, 12), (882, 25), (850, 50), (778, 62),
     (705, 57), (622, 50), (560, 33), (530, 20)],
    [(788, 73), (850, 70), (882, 77), (850, 88), (798, 86), (778, 80)],
]

# (x, y, label, align) where align is "right" or "left" of the dot
MARKERS = [
    (360, 11, "MERCURY", "right"),
    (482, 20, "BERLIN", "left"),
    (556, 16, "MOSCOW", "right"),
    (606, 45, "HORMUZ", "right"),
    (734, 32, "JIUQUAN", "right"),
    (242, 62, "CARTAGENA", "right"),
]

_FONT_CACHE = {}


def load(path, size):
    key = (path, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


def fit_lines(draw, text, font, width):
    done, current = [], ""
    for word in text.split(" "):
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                done.append(current)
            current = word
    if current:
        done.append(current)
    return done


def fit_font_single_line(draw, text, path, max_size, min_size, max_width):
    for size in range(max_size, min_size - 1, -1):
        font = load(path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
    return load(path, min_size)


def put_centred(draw, cx, y, text, font, fill=FOREGROUND):
    wide = draw.textlength(text, font=font)
    draw.text((cx - wide / 2, y), text, font=font, fill=fill)
    return y + font.size


def hrule(draw, y, x0=GUTTER, x1=PAGE_W - GUTTER, weight=1, fill=FOREGROUND):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)
    return y + weight


def icon_satellite(draw, x, y, s, ink=DEEP):
    # Solar panel wings
    draw.rectangle([x, y + s * .34, x + s * .28, y + s * .66], fill=ink)
    draw.rectangle([x + s * .72, y + s * .34, x + s, y + s * .66], fill=ink)
    # Solar panel struts
    draw.line([x + s * .28, y + s * .5, x + s * .36, y + s * .5],
              fill=FOREGROUND, width=max(1, s // 24))
    draw.line([x + s * .64, y + s * .5, x + s * .72, y + s * .5],
              fill=FOREGROUND, width=max(1, s // 24))
    # Solar grid lines on larger icons
    if s >= 24:
        for frac in (0.14, 0.86):
            draw.line([x + s * frac, y + s * .34, x + s * frac, y + s * .66],
                      fill=WHITE, width=1)
        draw.line([x, y + s * .5, x + s * .28, y + s * .5], fill=WHITE, width=1)
        draw.line([x + s * .72, y + s * .5, x + s, y + s * .5], fill=WHITE, width=1)
    # Central satellite body
    draw.rectangle([x + s * .36, y + s * .26, x + s * .64, y + s * .74],
                   fill=FOREGROUND, outline=ink, width=1)
    # Nuclear warning core indicator
    draw.ellipse([x + s * .42, y + s * .42, x + s * .58, y + s * .58],
                 fill=ACCENT)
    # Top antenna + dish
    draw.line([x + s * .5, y + s * .14, x + s * .5, y + s * .26],
              fill=FOREGROUND, width=max(1, s // 20))
    draw.arc([x + s * .36, y + s * .02, x + s * .64, y + s * .24],
             20, 160, fill=FOREGROUND, width=max(1, s // 18))
    # Signal arcs
    if s >= 24:
        draw.arc([x + s * .62, y + s * .02, x + s * .86, y + s * .26],
                 270, 355, fill=ACCENT, width=2)
        draw.arc([x + s * .66, y - s * .04, x + s * .96, y + s * .26],
                 275, 350, fill=ACCENT, width=1)


def icon_planet(draw, x, y, s, ink=DEEP):
    # Mercury sphere
    r = s * .30
    cx, cy = x + s * .50, y + s * .50
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(110, 132, 156), outline=ink, width=max(1, s // 18))
    # Surface craters
    if s >= 24:
        draw.ellipse([cx - r * .48, cy - r * .35, cx - r * .12, cy + r * .01],
                     fill=(84, 104, 128))
        draw.ellipse([cx + r * .15, cy + r * .08, cx + r * .48, cy + r * .41],
                     fill=(84, 104, 128))
        draw.ellipse([cx - r * .10, cy + r * .28, cx + r * .12, cy + r * .50],
                     fill=(136, 156, 178))
    # Tilted orbit ring around planet
    rx, ry = s * .48, s * .17
    angle = -0.38
    ca, sa = math.cos(angle), math.sin(angle)
    pts = []
    for deg in range(0, 361, 10):
        rad = math.radians(deg)
        px = rx * math.cos(rad)
        py = ry * math.sin(rad)
        pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    draw.line(pts, fill=ink, width=max(1, s // 22))
    # BepiColombo spacecraft dot on orbit
    rad = math.radians(-28)
    px, py = rx * math.cos(rad), ry * math.sin(rad)
    ox, oy = cx + px * ca - py * sa, cy + px * sa + py * ca
    dot = max(2, s // 14)
    draw.ellipse([ox - dot, oy - dot, ox + dot, oy + dot],
                 fill=ACCENT, outline=WHITE, width=1)


def icon_rocket(draw, x, y, s, ink=DEEP):
    draw.polygon([(x + s * .5, y), (x + s * .72, y + s * .35),
                  (x + s * .28, y + s * .35)], fill=ink)
    draw.rectangle([x + s * .32, y + s * .32, x + s * .68, y + s * .72],
                   fill=ink)
    draw.polygon([(x + s * .32, y + s * .72), (x + s * .12, y + s * .88),
                  (x + s * .32, y + s * .82)], fill=ink)
    draw.polygon([(x + s * .68, y + s * .72), (x + s * .88, y + s * .88),
                  (x + s * .68, y + s * .82)], fill=ink)
    draw.polygon([(x + s * .42, y + s * .72), (x + s * .58, y + s * .72),
                  (x + s * .5, y + s)], fill=ACCENT)
    draw.ellipse([x + s * .42, y + s * .42, x + s * .58, y + s * .58],
                 fill=WHITE)


def icon_shield(draw, x, y, s, ink=ACCENT):
    draw.polygon([(x + s * .5, y), (x + s * .94, y + s * .18),
                  (x + s * .94, y + s * .55), (x + s * .5, y + s),
                  (x + s * .06, y + s * .55), (x + s * .06, y + s * .18)],
                 outline=ink, width=max(1, s // 9))
    draw.ellipse([x + s * .38, y + s * .30, x + s * .62, y + s * .54],
                 fill=ink)
    draw.rectangle([x + s * .45, y + s * .50, x + s * .55, y + s * .74],
                   fill=ink)


def icon_globe(draw, x, y, s, ink=DEEP):
    draw.ellipse([x, y, x + s, y + s], outline=ink, width=max(1, s // 9))
    draw.ellipse([x + s * .3, y, x + s * .7, y + s], outline=ink, width=1)
    draw.line([x, y + s * .5, x + s, y + s * .5], fill=ink, width=1)
    draw.arc([x, y + s * .18, x + s, y + s * .82], 200, 340, fill=ink, width=1)
    draw.arc([x, y + s * .18, x + s, y + s * .82], 20, 160, fill=ink, width=1)


def icon_ship(draw, x, y, s, ink=DEEP):
    draw.polygon([(x, y + s * .55), (x + s, y + s * .55),
                  (x + s * .85, y + s * .85), (x + s * .15, y + s * .85)],
                 fill=ink)
    draw.rectangle([x + s * .44, y + s * .12, x + s * .56, y + s * .55],
                   fill=ink)
    draw.line([x + s * .05, y + s * .95, x + s * .95, y + s * .95],
              fill=MAP_LINE, width=max(1, s // 8))


def icon_flame(draw, x, y, s, ink=(214, 110, 30)):
    draw.polygon([(x + s * .5, y), (x + s * .85, y + s * .45),
                  (x + s * .95, y + s * .7), (x + s * .7, y + s),
                  (x + s * .3, y + s), (x + s * .05, y + s * .7),
                  (x + s * .15, y + s * .45)], fill=ink)
    draw.polygon([(x + s * .5, y + s * .45), (x + s * .68, y + s * .68),
                  (x + s * .5, y + s * .85), (x + s * .32, y + s * .68)],
                 fill=(250, 232, 205))


def icon_ball(draw, x, y, s, ink=FOREGROUND):
    draw.ellipse([x, y, x + s, y + s], outline=ink, width=max(1, s // 9))
    draw.polygon([(x + s * .5, y + s * .3), (x + s * .68, y + s * .45),
                  (x + s * .6, y + s * .68), (x + s * .4, y + s * .68),
                  (x + s * .32, y + s * .45)], fill=ink)


ICONS = {
    "satellite": icon_satellite,
    "planet": icon_planet,
    "rocket": icon_rocket,
    "shield": icon_shield,
    "globe": icon_globe,
    "ship": icon_ship,
    "flame": icon_flame,
    "ball": icon_ball,
}


def draw_globe(draw, cx, cy, radius):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 outline=FOREGROUND, width=3)
    draw.ellipse([cx - 10, cy - radius, cx + 10, cy + radius],
                 outline=FOREGROUND, width=2)
    draw.line([cx - radius, cy, cx + radius, cy], fill=FOREGROUND, width=2)
    draw.arc([cx - radius, cy - 14, cx + radius, cy + 14], 200, 340,
             fill=FOREGROUND, width=2)
    draw.arc([cx - radius, cy - 14, cx + radius, cy + 14], 20, 160,
             fill=FOREGROUND, width=2)


def draw_masthead(draw):
    cx = PAGE_W // 2
    draw_globe(draw, 62, 56, 17)
    # Red-bordered DATE CHECK badge
    bx0, by0, bx1, by1 = 794, 30, PAGE_W - GUTTER, 72
    draw.rectangle([bx0, by0, bx1, by1], fill=WHITE, outline=ACCENT, width=2)
    draw.rectangle([bx0, by0, bx1, by0 + 19], fill=ACCENT)
    put_centred(draw, (bx0 + bx1) / 2, by0 + 3, "DATE CHECK",
                load(SANS_BOLD, 12), fill=WHITE)
    put_centred(draw, (bx0 + bx1) / 2, by0 + 24, "THU 26 NOV 2026 · UTC",
                load(SANS_BOLD, 12), fill=ACCENT)
    # Newspaper title & date line
    put_centred(draw, cx, 32, "THE WORLD IN ONE IMAGE",
                load(SERIF_BOLD, 33))
    put_centred(draw, cx, 78,
                "T H U R S D A Y ,  2 6  N O V E M B E R  2 0 2 6",
                load(SANS_BOLD, 15), fill=ACCENT)
    y = hrule(draw, 102, weight=3)
    y = hrule(draw, y + 3, weight=1)
    return y + 7


def draw_kpi(draw, y):
    h = 34
    draw.rectangle([GUTTER, y, PAGE_W - GUTTER, y + h], fill=KPI_BG,
                   outline=RULE_LIGHT, width=1)
    cell_w = CONTENT_W / len(KPIS)
    for i, (num, label) in enumerate(KPIS):
        x = int(GUTTER + i * cell_w)
        if i:
            draw.line([x, y + 5, x, y + h - 5], fill=MUTED, width=1)
        draw.text((x + 8, y + 3), num, font=load(SANS_BOLD, 16), fill=ACCENT)
        lbl_font = fit_font_single_line(draw, label, SANS_BOLD, 8, 7,
                                        cell_w - 12)
        draw.text((x + 8, y + 21), label, font=lbl_font, fill=BODY_INK)
    return y + h + 8


def draw_leads(draw, y):
    box_h = 74
    kicker_h = 17
    head_lines_max = 2
    head_line_h = 24
    deck_lines_max = 4
    deck_line_h = 14
    for idx, lead in enumerate(LEADS):
        x = COL_X[idx]
        # Illustrated header box
        draw.rectangle([x, y, x + COL_W, y + box_h], fill=lead["tint"],
                       outline=FOREGROUND, width=1)
        icon_s = 46
        ICONS[lead["icon"]](draw, x + COL_W // 2 - icon_s // 2, y + 7, icon_s)
        draw.text((x + 7, y + box_h - 14), lead["source"],
                  font=load(SANS_BOLD, 9), fill=MUTED)
        # Kicker
        yy = y + box_h + 6
        draw.text((x, yy), lead["kicker"], font=load(SANS_BOLD, 12),
                  fill=ACCENT)
        yy += kicker_h
        # Headline (2 lines, exact fit)
        head_font = load(SERIF_BOLD, 20)
        hlines = fit_lines(draw, lead["headline"], head_font, COL_W)
        if len(hlines) > head_lines_max:
            head_font = load(SERIF_BOLD, 18)
            hlines = fit_lines(draw, lead["headline"], head_font, COL_W)
        for line in hlines[:head_lines_max]:
            draw.text((x, yy), line, font=head_font, fill=FOREGROUND)
            yy += head_line_h
        yy += 3
        # Deck (wrapped, auto-size so all lines fit with zero clipping)
        deck_font = load(SANS, 11)
        dlines = fit_lines(draw, lead["deck"], deck_font, COL_W)
        if len(dlines) > deck_lines_max:
            deck_font = load(SANS, 10)
            dlines = fit_lines(draw, lead["deck"], deck_font, COL_W)
        for line in dlines[:deck_lines_max]:
            draw.text((x, yy), line, font=deck_font, fill=BODY_INK)
            yy += deck_line_h
    return (y + box_h + 6 + kicker_h + head_lines_max * head_line_h
            + 3 + deck_lines_max * deck_line_h + 6)


def draw_map(draw, y):
    label_font = load(SANS_BOLD, 12)
    draw.text((GUTTER, y), "THE WORLD TODAY", font=label_font, fill=DEEP)
    right = "6 REGIONS · 39 STORIES + 3 LEADS"
    draw.text((PAGE_W - GUTTER - draw.textlength(right, font=label_font), y),
              right, font=label_font, fill=ACCENT)
    my = y + 17
    draw.rectangle([GUTTER, my, GUTTER + MAP_W, my + MAP_H],
                   fill=(232, 240, 246), outline=FOREGROUND, width=1)
    for poly in CONTINENTS:
        pts = [(GUTTER + px, my + py) for px, py in poly]
        draw.polygon(pts, fill=MAP_FILL, outline=MAP_LINE)
    mfont = load(SANS_BOLD, 9)
    for mx, myy, label, align in MARKERS:
        cx, cy = GUTTER + mx, my + myy
        if label == "MERCURY":
            draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6],
                         outline=DEEP, width=1)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ACCENT,
                     outline=WHITE, width=1)
        tw = draw.textlength(label, font=mfont)
        if align == "left":
            lx = cx - 6 - tw
        else:
            lx = cx + 6
        draw.text((lx, cy - 5), label, font=mfont, fill=ACCENT)
    return my + MAP_H + 8


def draw_timeline(draw, y):
    label_font = load(SANS_BOLD, 12)
    draw.text((GUTTER, y), "UTC TIMELINE — KEY EVENTS (21–26 NOVEMBER 2026)",
              font=label_font, fill=DEEP)
    line_y = y + 34
    x0, x1 = GUTTER, PAGE_W - GUTTER
    span = x1 - x0
    draw.line([x0, line_y, x1, line_y], fill=FOREGROUND, width=2)

    # Timeline axis ticks (21 Nov, scale break, then 25 Nov 00:00 -> 26 Nov)
    tick_font = load(SANS, 9)
    ticks = [
        (0.06, "21 NOV"),
        (0.32, "25 NOV 00:00"),
        (0.56, "04:00"),
        (0.76, "12:00"),
        (0.95, "26 NOV 00:00"),
    ]
    for frac, tlabel in ticks:
        tx = x0 + span * frac
        draw.line([tx, line_y - 4, tx, line_y + 4], fill=FOREGROUND, width=2)
        tw = draw.textlength(tlabel, font=tick_font)
        draw.text((tx - tw / 2, line_y + 6), tlabel, font=tick_font,
                  fill=MUTED)

    # Scale break marks between 21 Nov and 25 Nov
    bx = x0 + span * 0.21
    draw.rectangle([bx - 5, line_y - 4, bx + 5, line_y + 4], fill=BACKGROUND)
    draw.line([bx - 4, line_y + 5, bx, line_y - 5], fill=MUTED, width=1)
    draw.line([bx + 1, line_y + 5, bx + 5, line_y - 5], fill=MUTED, width=1)

    # 3 staggered UTC events
    ev_font = load(SANS_BOLD, 10)
    events = [
        (0.06, "21 NOV — BEPICOLOMBO ENTERS MERCURY ORBIT", True),
        (0.335, "00:18 UTC — SHENZHOU-24 LIFTOFF (25 NOV)", False),
        (0.555, "03:56 UTC — SHENZHOU-24 DOCKS TIANGONG", True),
    ]
    for frac, elabel, above in events:
        tx = x0 + span * frac
        draw.ellipse([tx - 4, line_y - 4, tx + 4, line_y + 4],
                     fill=ACCENT, outline=WHITE, width=1)
        ew = draw.textlength(elabel, font=ev_font)
        lx = min(max(x0, tx - 4), x1 - ew)
        if above:
            draw.text((lx, line_y - 18), elabel, font=ev_font, fill=ACCENT)
        else:
            draw.text((lx, line_y + 19), elabel, font=ev_font, fill=ACCENT)
    return line_y + 34


def draw_regions(draw, y, row_regions, row_h):
    for idx, (name, count, stories) in enumerate(row_regions):
        x = COL_X[idx]
        if idx > 0:
            vx = x - COL_GAP // 2
            draw.line([vx, y, vx, y + row_h - 4], fill=RULE_LIGHT, width=1)
        draw.rectangle([x, y, x + COL_W, y + 19], fill=DEEP)
        draw.text((x + 6, y + 3), name, font=load(SANS_BOLD, 12), fill=WHITE)
        cnt = f"{count} STORIES"
        cnt_font = load(SANS_BOLD, 9)
        draw.text((x + COL_W - 6 - draw.textlength(cnt, font=cnt_font), y + 5),
                  cnt, font=cnt_font, fill=WHITE)
        yy = y + 24
        for headline, icon in stories:
            tx = x
            if icon:
                ICONS[icon](draw, x, yy + 1, 12)
                tx = x + 16
            avail_w = COL_W - (tx - x)
            font = fit_font_single_line(draw, headline, SANS, 11, 8, avail_w)
            y_off = (11 - font.size) // 2
            draw.text((tx, yy + y_off), headline, font=font, fill=BODY_INK)
            yy += 16
    return y + row_h


def draw_distribution(draw, y):
    label_font = load(SANS_BOLD, 12)
    draw.text((GUTTER, y), "STORIES BY REGION (39 GRID STORIES)",
              font=label_font, fill=DEEP)
    y += 17
    total = sum(n for _, n in DIST)
    bx, bw, bh = GUTTER, CONTENT_W, 17
    xx = bx
    bar_font = load(SANS_BOLD, 10)
    for idx, ((name, n), color) in enumerate(zip(DIST, DIST_COLORS)):
        if idx == len(DIST) - 1:
            w = (bx + bw) - xx
        else:
            w = round(bw * n / total)
        draw.rectangle([xx, y, xx + w - 1, y + bh], fill=color)
        num_txt = str(n)
        nw = draw.textlength(num_txt, font=bar_font)
        draw.text((xx + (w - nw) / 2, y + 3), num_txt,
                  font=bar_font, fill=WHITE)
        xx += w
    draw.rectangle([bx, y, bx + bw, y + bh], outline=FOREGROUND, width=1)
    y += bh + 6
    lx = GUTTER
    leg_font = load(SANS_BOLD, 10)
    for (name, n), color in zip(DIST, DIST_COLORS):
        draw.rectangle([lx, y + 1, lx + 10, y + 11], fill=color)
        txt = f"{name} {n}"
        draw.text((lx + 14, y), txt, font=leg_font, fill=BODY_INK)
        lx += 14 + draw.textlength(txt, font=leg_font) + 18
    return y + 15


def render():
    page = Image.new("RGB", (PAGE_W, PAGE_H), BACKGROUND)
    draw = ImageDraw.Draw(page)
    draw.rectangle([12, 12, PAGE_W - 13, PAGE_H - 13], outline=FOREGROUND,
                   width=2)
    draw.rectangle([20, 20, PAGE_W - 21, PAGE_H - 21], outline=FOREGROUND,
                   width=1)
    y = draw_masthead(draw)
    y = draw_kpi(draw, y)
    y = draw_leads(draw, y)
    y = draw_map(draw, y)
    y = draw_timeline(draw, y)
    y = draw_regions(draw, y + 4, REGIONS[:3], 170)
    y = draw_regions(draw, y + 4, REGIONS[3:], 154)
    y = draw_distribution(draw, y + 6)
    hrule(draw, y + 6)
    put_centred(
        draw, PAGE_W // 2, y + 11,
        "Sources: Reuters · AP · Xinhua · NYT · CNN · SCMP · Washington Post",
        load(SANS, 12), fill=MUTED,
    )
    put_centred(
        draw, PAGE_W // 2, y + 27,
        "Compiled from the day's reporting  ·  Thursday 26 November 2026",
        load(SANS, 12), fill=MUTED,
    )
    return page


def main():
    image = render()
    image.save("entry.png", "PNG", optimize=True)
    print("saved entry.png", image.size)


if __name__ == "__main__":
    main()
