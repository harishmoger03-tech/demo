"""Frame-accurate renderer for Raw_Cinematic_Broll_9x16.mp4.

Streams the source at a constant 30 fps from FFmpeg, builds each output frame from
the EDL (scripts/edl.py) — speaker reframes, motion-graphics scenes, transitions,
grade, grain, captions — and pipes RGB frames into libx264 together with the
mixed audio (scripts/audio.py).

Usage:
  python3 -I scripts/render.py <source.mp4> <mix.wav> <out.mp4>
  python3 -I scripts/render.py <source.mp4> --stills <dir> t1 t2 ...   # QC frames
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import (AI_CARDS, CAPTIONS, CHECK_AT, COST_AT, FACE, FPS, GATHER_AT, H, JODTE_AT,  # noqa: E402
                 ONE_PLACE, OUT_DUR, SEGMENTS, SRC_DUR, STACK_AT, STREAM_TILES, TAG_AT, W)

FONT_DIR = "/usr/share/fonts/opentype/inter"
F_CAPTION = f"{FONT_DIR}/Inter-ExtraBold.otf"
F_CARD = f"{FONT_DIR}/Inter-SemiBold.otf"

GOLD = (243, 201, 105)
GOLD_SOFT = (214, 170, 92)
INK = (16, 12, 10)
WHITE = (250, 248, 244)
SS = 2  # supersampling factor for sprites


# ----------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ease_in_out(p):
    p = clamp(p)
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_back(p, s=1.25):
    p = clamp(p)
    return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2


def lerp(a, b, p):
    return a + (b - a) * p


def font(path, size):
    return ImageFont.truetype(path, size)


def finish(img):
    """Downsample a 2x-supersampled RGBA sprite."""
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def shadowed(sprite, radius=22, opacity=0.55, offset=(0, 10), pad=48):
    """Add a soft drop shadow around an RGBA sprite."""
    w, h = sprite.size
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = sprite.getchannel("A").point(lambda v: int(v * opacity))
    sh = Image.new("RGBA", sprite.size, (0, 0, 0, 255))
    sh.putalpha(a)
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(sh, (pad + offset[0], pad + offset[1]), sh)
    out = Image.alpha_composite(out, layer.filter(ImageFilter.GaussianBlur(radius)))
    out.alpha_composite(sprite, (pad, pad))
    return out


def paste(base, sprite, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    """Alpha-composite `sprite` centred at (cx, cy) with scale/opacity/rotation."""
    if alpha <= 0.003:
        return
    s = sprite
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, round(s.width * scale)), max(1, round(s.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.05:
        s = s.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    x0, y0 = round(cx - s.width / 2), round(cy - s.height / 2)
    sx0, sy0 = max(0, -x0), max(0, -y0)
    sx1, sy1 = min(s.width, base.width - x0), min(s.height, base.height - y0)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    base.alpha_composite(s.crop((sx0, sy0, sx1, sy1)), (x0 + sx0, y0 + sy0))


# ----------------------------------------------------------------- sprites
def renew_icon(d, cx, cy, r, width, color):
    """Circular 'recurring payment' arrows."""
    box = (cx - r, cy - r, cx + r, cy + r)
    d.arc(box, 200, 340, fill=color, width=width)
    d.arc(box, 20, 160, fill=color, width=width)
    for ang in (340, 160):
        a = math.radians(ang)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        t = a + math.pi / 2                       # tangent direction (clockwise)
        k = width * 2.0
        tip = (px + math.cos(t) * k, py + math.sin(t) * k)
        n = (math.cos(a), math.sin(a))
        d.polygon([tip, (px + n[0] * k * 0.95, py + n[1] * k * 0.95), (px - n[0] * k * 0.95, py - n[1] * k * 0.95)],
                  fill=color)


def card_sprite(text, w=760, h=148, blank=False):
    W2, H2 = w * SS, h * SS
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), radius=36 * SS, fill=(22, 17, 14, 214),
                        outline=GOLD_SOFT + (150,), width=2 * SS)
    icx, icy, ir = 84 * SS, H2 // 2, 40 * SS
    d.ellipse((icx - ir, icy - ir, icx + ir, icy + ir), fill=(243, 201, 105, 38))
    renew_icon(d, icx, icy, 19 * SS, 4 * SS, GOLD)
    if blank:                                 # face used for cards at the back of the pile
        return shadowed(finish(im))
    f = font(F_CARD, 56 * SS)
    tb = d.textbbox((0, 0), text, font=f)
    d.text((150 * SS, H2 // 2 - (tb[1] + tb[3]) // 2), text, font=f, fill=WHITE)
    return shadowed(finish(im))


def tile_sprite(text, w=440, h=250):
    W2, H2 = w * SS, h * SS
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), radius=40 * SS, fill=(22, 17, 14, 214),
                        outline=GOLD_SOFT + (150,), width=2 * SS)
    d.rounded_rectangle((36 * SS, 36 * SS, 36 * SS + 54 * SS, 36 * SS + 6 * SS), radius=3 * SS, fill=GOLD + (255,))
    size = 56
    while True:
        f = font(F_CARD, size * SS)
        tb = d.textbbox((0, 0), text, font=f)
        if tb[2] - tb[0] <= W2 - 72 * SS or size <= 40:
            break
        size -= 2
    d.text((W2 // 2 - (tb[0] + tb[2]) // 2, H2 // 2 + 14 * SS - (tb[1] + tb[3]) // 2), text, font=f, fill=WHITE)
    return shadowed(finish(im))


def chip_sprite(text):
    f = font(F_CARD, 46 * SS)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tb = tmp.textbbox((0, 0), text, font=f)
    w2, h2 = tb[2] - tb[0] + 64 * SS, 78 * SS
    im = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w2 - 1, h2 - 1), radius=h2 // 2, fill=(30, 23, 18, 225),
                        outline=(255, 255, 255, 46), width=2 * SS)
    d.text((32 * SS - tb[0], h2 // 2 - (tb[1] + tb[3]) // 2), text, font=f, fill=WHITE)
    return shadowed(finish(im), radius=14, opacity=0.45, offset=(0, 6), pad=30)


def panel_sprite(w, h):
    W2, H2 = w * SS, h * SS
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W2 - 1, H2 - 1), radius=44 * SS, fill=(18, 14, 11, 170),
                        outline=GOLD + (210,), width=3 * SS)
    return shadowed(finish(im), radius=30, opacity=0.5, offset=(0, 14), pad=60)


def check_sprite(r=30):
    s = r * 2 * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=GOLD + (255,))
    pts = [(0.28 * s, 0.53 * s), (0.44 * s, 0.68 * s), (0.73 * s, 0.36 * s)]
    d.line(pts, fill=INK + (255,), width=int(0.11 * s), joint="curve")
    return finish(im)


def tag_sprite(size=190):
    """Price tag with a downward arrow (discount), gold line icon."""
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = int(0.045 * s)
    body = [(0.16 * s, 0.30 * s), (0.42 * s, 0.10 * s), (0.86 * s, 0.10 * s), (0.86 * s, 0.90 * s),
            (0.42 * s, 0.90 * s), (0.16 * s, 0.70 * s)]
    d.polygon(body, fill=(20, 15, 12, 200))
    d.line(body + [body[0]], fill=GOLD + (255,), width=lw, joint="curve")
    hx, hy, hr = 0.33 * s, 0.50 * s, 0.055 * s
    d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), outline=GOLD + (255,), width=int(lw * 0.8))
    ax = 0.63 * s
    d.line([(ax, 0.26 * s), (ax, 0.70 * s)], fill=WHITE + (255,), width=lw)
    d.polygon([(ax - 0.13 * s, 0.60 * s), (ax + 0.13 * s, 0.60 * s), (ax, 0.77 * s)], fill=WHITE + (255,))
    return shadowed(finish(im), radius=16, opacity=0.6, offset=(0, 8), pad=36)


def rupee_meter(w=700, h=30):
    W2, H2 = w * SS, h * SS
    track = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    ImageDraw.Draw(track).rounded_rectangle((0, 0, W2 - 1, H2 - 1), radius=H2 // 2, fill=(20, 15, 12, 190),
                                            outline=GOLD_SOFT + (120,), width=2 * SS)
    fill = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    grad = np.zeros((H2, W2, 4), np.uint8)
    x = np.linspace(0, 1, W2)[None, :]
    for c, (a, b) in enumerate(zip((214, 170, 92), (255, 222, 150))):
        grad[..., c] = (a + (b - a) * x).astype(np.uint8)
    grad[..., 3] = 255
    mask = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(mask).rounded_rectangle((3 * SS, 3 * SS, W2 - 3 * SS, H2 - 3 * SS), radius=H2 // 2, fill=255)
    fill = Image.fromarray(grad, "RGBA")
    fill.putalpha(mask)
    f = font(F_CARD, 54 * SS)
    sym = Image.new("RGBA", (70 * SS, 80 * SS), (0, 0, 0, 0))
    ImageDraw.Draw(sym).text((35 * SS, 40 * SS), "₹", font=f, fill=GOLD + (255,), anchor="mm")
    return finish(track), finish(fill), finish(sym)


# ----------------------------------------------------------------- captions
CAP_FONT = font(F_CAPTION, 62 * SS)
CAP_MAXW = 820
CAP_Y = 1390       # below the mic mount even at the 1.14 punch-in; above platform UI
_cap_cache = {}


def norm(word):
    return "".join(ch for ch in word.lower() if ch.isalnum() or ch == "-")


def caption_sprite(text, gold):
    key = (text, frozenset(gold))
    if key in _cap_cache:
        return _cap_cache[key]
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    words = text.split(" ")
    space = d0.textlength(" ", font=CAP_FONT)
    lines, cur = [], []
    for wd in words:                          # greedy wrap
        trial = " ".join(cur + [wd])
        if cur and d0.textlength(trial, font=CAP_FONT) > (CAP_MAXW - 56) * SS:
            lines.append(cur)
            cur = [wd]
        else:
            cur.append(wd)
    lines.append(cur)
    asc, desc = CAP_FONT.getmetrics()
    lh = int((asc + desc) * 1.02)
    widths = [d0.textlength(" ".join(l), font=CAP_FONT) for l in lines]
    padx, pady = 30 * SS, 16 * SS
    bw, bh = int(max(widths) + 2 * padx), int(lh * len(lines) + 2 * pady)
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=26 * SS, fill=(12, 9, 7, 150))
    y = pady
    for l, lw in zip(lines, widths):
        x = (bw - lw) / 2
        for wd in l:
            col = GOLD if norm(wd) in gold else WHITE
            d.text((x, y), wd, font=CAP_FONT, fill=col + (255,))
            x += d0.textlength(wd, font=CAP_FONT) + space
        y += lh
    spr = shadowed(finish(im), radius=12, opacity=0.35, offset=(0, 4), pad=24)
    _cap_cache[key] = spr
    return spr


def draw_captions(base, t):
    for i, (a, b, text, hl) in enumerate(CAPTIONS):
        if not (a <= t < b):
            continue
        gold = {norm(w) for w, at in hl if at is None or t >= at}
        spr = caption_sprite(text, gold)
        p = ease_out((t - a) / (5 / FPS))
        nxt = CAPTIONS[i + 1][0] if i + 1 < len(CAPTIONS) else 99
        out = 1.0 if nxt - b < 0.1 else clamp((b - t) / (4 / FPS))   # fade only before a gap
        paste(base, spr, W / 2, CAP_Y + (1 - p) * 14, alpha=min(p, out))


# ----------------------------------------------------------------- grade
def build_lut():
    xs = np.array([0, .10, .25, .50, .75, .90, 1.0])
    ys = np.array([.016, .085, .232, .50, .768, .902, .968])     # gentle S, soft roll-off
    x = np.arange(256) / 255
    base = np.interp(x, xs, ys)
    r = np.clip(base * (1 + 0.012 * x), 0, 1)                    # faint warmth in highlights
    g = base
    b = np.clip(base * (1 - 0.018 * x) + 0.006 * (1 - x), 0, 1)
    return (np.stack([r, g, b], 1) * 255).astype(np.float32)


LUT = build_lut()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H / 2)) ** 2) / math.sqrt(2)
VIGNETTE = (1 - 0.22 * np.clip(_r, 0, 1) ** 2.3)[..., None].astype(np.float32)
GLOW = np.exp(-(((xx - W * 0.5) / 520) ** 2 + ((yy - H * 0.42) / 760) ** 2))[..., None].astype(np.float32)
del yy, xx, _r
_grng = np.random.default_rng(3)
GRAIN = []
for _ in range(12):
    g = _grng.standard_normal((H // 2, W // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(g, "F").resize((W, H), Image.BILINEAR))
    GRAIN.append((g * 2.1)[..., None])


def grade(rgb_u8, n):
    lut = LUT
    out = np.empty(rgb_u8.shape, np.float32)
    for c in range(3):
        out[..., c] = lut[rgb_u8[..., c], c]
    lum = out @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    out = lum[..., None] + (out - lum[..., None]) * 0.97           # restrained saturation
    out *= VIGNETTE
    out += GRAIN[n % len(GRAIN)]
    return out


def plate(src_u8, t):
    """Blurred, darkened speaker plate behind motion graphics (keeps continuity)."""
    im = Image.fromarray(src_u8).resize((270, 480), Image.BOX).filter(ImageFilter.GaussianBlur(7))
    z = 1.10 + 0.02 * (t % 10) / 10
    cw, ch = 270 / z, 480 / z
    im = im.resize((W, H), Image.BICUBIC, box=(135 - cw / 2, 240 - ch / 2, 135 + cw / 2, 240 + ch / 2))
    a = np.asarray(im, np.float32) * 0.36
    a += GLOW * np.array([46, 30, 16], np.float32)
    return np.clip(a, 0, 255).astype(np.uint8)


def reframe(src_u8, scale):
    if abs(scale - 1) < 1e-4:
        return src_u8
    cw, ch = W / scale, H / scale
    x0 = clamp(FACE[0] - cw / 2, 0, W - cw)
    y0 = clamp(FACE[1] - ch / 2, 0, H - ch)
    return np.asarray(Image.fromarray(src_u8).resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)))


# ----------------------------------------------------------------- scenes
SPR = {}


def build_sprites():
    SPR["ai"] = [card_sprite(t) for t, _ in AI_CARDS]
    SPR["ai_blank"] = card_sprite("", blank=True)
    SPR["tiles"] = [tile_sprite(t) for t, _ in STREAM_TILES]
    SPR["chips"] = [chip_sprite(t) for t in ONE_PLACE]
    SPR["panel"] = panel_sprite(820, 7 * 92 + 64)
    SPR["check"] = check_sprite()
    SPR["tag"] = tag_sprite()
    SPR["track"], SPR["fill"], SPR["rupee"] = rupee_meter()


def scene_ai_stack(o, t):
    list_y = [560, 730, 900, 1070]
    q = ease_in_out((t - STACK_AT) / 0.5)
    for i, (spr, (_, at)) in enumerate(zip(SPR["ai"], AI_CARDS)):
        p = ease_out((t - (at - 0.06)) / 0.38)
        if p <= 0:
            continue
        y = lerp(list_y[i], 640 + i * 26, q)
        sc = lerp(0.96 + 0.04 * p, 1 - (3 - i) * 0.035, q)
        x = 540 + (1 - p) * 140
        a = p * lerp(1, 0.9 + 0.1 * (i == 3), q)
        if i < 3 and q > 0:                   # back of the pile: text fades out as it stacks
            paste(o, SPR["ai_blank"], x, y, scale=sc, alpha=a * q)
            a *= 1 - q
        paste(o, spr, x, y, scale=sc, alpha=a)
    m = ease_out((t - (COST_AT - 0.08)) / 0.25)
    if m > 0:
        cy = 930
        paste(o, SPR["track"], 560, cy, alpha=m)
        paste(o, SPR["rupee"], 175, cy - 2, alpha=m)
        steps = [(COST_AT, 0.0, 0.32), (JODTE_AT[0], 0.32, 0.66), (JODTE_AT[1], 0.66, 1.0)]
        frac = 0.0
        for at, a, b in steps:
            if t >= at:
                frac = lerp(a, b, ease_out((t - at) / 0.22))
        fw = int(SPR["fill"].width * frac)
        if fw > 4:
            f = SPR["fill"].crop((0, 0, fw, SPR["fill"].height))
            x0 = 560 - SPR["fill"].width / 2
            paste(o, f, x0 + fw / 2, cy, alpha=m)
            for at in JODTE_AT:                       # soft pulse on each "jodte"
                g = clamp(1 - abs(t - at - 0.08) / 0.16)
                if g > 0:
                    paste(o, SPR["check"].resize((14, 14)), x0 + fw, cy, scale=1 + 2.4 * g, alpha=0.55 * g)


def scene_stream_grid(o, t, t0):
    pos = [(300, 700), (780, 700), (300, 980), (780, 980)]
    z = 1 + 0.03 * clamp((t - t0) / 2.8)
    for spr, (x, y), (_, at) in zip(SPR["tiles"], pos, STREAM_TILES):
        p = clamp((t - (at - 0.05)) / 0.32)
        if p <= 0:
            continue
        sc = lerp(0.88, 1.0, ease_back(p)) * z
        paste(o, spr, 540 + (x - 540) * z, 840 + (y - 840) * z, scale=sc, alpha=ease_out(p))


def scene_one_place(o, t, t0):
    # hand-placed loose spread (x, y, tilt) clear of the face-free caption band
    scatter = [(270, 380, -7), (790, 330, 6), (560, 560, -4), (250, 780, 8), (840, 860, -6),
               (420, 1060, 5), (790, 1180, -8)]
    pa = ease_out((t - (GATHER_AT + 0.25)) / 0.45)
    panel_cy = 790
    if pa > 0:
        paste(o, SPR["panel"], 540, panel_cy, scale=lerp(1.04, 1.0, pa), alpha=pa)
    top = panel_cy - (7 * 92 + 64) / 2 + 32 + 46
    for i, (spr, (sx, sy, ang)) in enumerate(zip(SPR["chips"], scatter)):
        fin = ease_out((t - t0 - i * 0.03) / 0.22)
        g = ease_in_out((t - GATHER_AT - i * 0.04) / 0.7)
        tx = 170 + (spr.width - 60) / 2
        ty = top + i * 92
        paste(o, spr, lerp(sx, tx, g), lerp(sy, ty, g), angle=lerp(ang, 0, g), alpha=fin * lerp(0.85, 1, g))
        c = clamp((t - (CHECK_AT + i * 0.08)) / 0.26)
        if c > 0:
            paste(o, SPR["check"], 860, ty, scale=lerp(0.5, 1.0, ease_back(c)), alpha=ease_out(c))


def render_segment(seg, t, src, n):
    """Return the composited RGB uint8 frame for `seg` at time t (no captions)."""
    k = seg["kind"]
    if k == "speaker":
        p = ease_in_out((t - seg["start"]) / (seg["end"] - seg["start"]))
        img = grade(reframe(src, lerp(*seg["zoom"], p)), n)
        im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
        if seg["id"] == "V3":
            c = clamp((t - (TAG_AT - 0.04)) / 0.4)
            if c > 0:
                paste(im, SPR["tag"], 885 + 0 * c, 285 + (1 - ease_out(c)) * -18,
                      scale=lerp(0.7, 1.0, ease_back(c)), alpha=ease_out(c), angle=lerp(-14, -6, ease_out(c)))
        return im
    img = grade(plate(src, t), n)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    if k == "mg_ai_stack":
        scene_ai_stack(im, t)
    elif k == "mg_stream_grid":
        scene_stream_grid(im, t, seg["start"])
    elif k == "mg_one_place":
        scene_one_place(im, t, seg["start"])
    return im


def frame_at(n, src):
    t = n / FPS
    i = next(j for j, s in enumerate(SEGMENTS) if s["start"] <= t < s["end"] or j == len(SEGMENTS) - 1)
    seg = SEGMENTS[i]
    im = render_segment(seg, t, src, n)
    tr = seg.get("trans_in")
    if tr and i > 0 and t < seg["start"] + tr[1]:
        p = ease_in_out((t - seg["start"]) / tr[1])
        prev = render_segment(SEGMENTS[i - 1], t, src, n)
        im = Image.blend(prev, im, p)
    draw_captions(im, t)
    rgb = im.convert("RGB")
    if t >= SRC_DUR:                                   # tail: fade the held frame to black
        f = 1 - ease_in_out((t - SRC_DUR) / (OUT_DUR - SRC_DUR - 1 / FPS))
        rgb = Image.fromarray((np.asarray(rgb, np.float32) * f).astype(np.uint8))
    return rgb


# ----------------------------------------------------------------- main
def source_frames(src_path):
    cmd = ["ffmpeg", "-v", "error", "-i", src_path, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
    size = W * H * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()


def main():
    src_path = sys.argv[1]
    build_sprites()
    total = int(round(OUT_DUR * FPS))
    if sys.argv[2] == "--stills":
        outdir, times = sys.argv[3], [float(x) for x in sys.argv[4:]]
        os.makedirs(outdir, exist_ok=True)
        want = {int(round(x * FPS)): x for x in times}
        last = None
        for n, fr in enumerate(source_frames(src_path)):
            last = fr
            if n in want:
                frame_at(n, fr).save(f"{outdir}/t{want[n]:05.2f}.png")
        for n in want:
            if n >= int(round(SRC_DUR * FPS)) and last is not None:
                frame_at(n, last).save(f"{outdir}/t{want[n]:05.2f}.png")
        return
    mix, out = sys.argv[2], sys.argv[3]
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", mix,
        "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level:v", "4.2",
        "-x264-params", "keyint=60:min-keyint=30",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-map", "0:v", "-map", "1:a", "-t", f"{OUT_DUR}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = 0
    last = None
    for fr in source_frames(src_path):
        if n >= total:
            break
        last = fr
        enc.stdin.write(frame_at(n, fr).tobytes())
        n += 1
        if n % 60 == 0:
            print(f"frame {n}/{total}", flush=True)
    while n < total:                                   # held final source frame for the tail
        enc.stdin.write(frame_at(n, last).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    print(f"wrote {out} ({n} frames)")


if __name__ == "__main__":
    main()
