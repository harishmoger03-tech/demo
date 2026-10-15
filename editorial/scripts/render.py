"""Editorial film edit renderer for Raw.mp4 (editorial-film-edit skill).

Layer order per frame: picture (presenter / split / collage) -> emphasis words ->
presenter cut-out (text behind subject) -> bloom -> fresh grain -> captions.
Style lives in style.json, this video's content and timings in project.json.

Usage:
  python3 -I scripts/render.py <project_dir> out/<name>.mp4          # full render (+ original audio)
  python3 -I scripts/render.py <project_dir> --stills <dir> t1 t2 ... # test frames
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(sys.argv[1])
ST = json.load(open(f"{ROOT}/style.json"))
PJ = json.load(open(f"{ROOT}/project.json"))
FPS, W, H, NF = PJ["fps"], PJ["width"], PJ["height"], PJ["frames"]
FX, FY = PJ["face"]
SRC = os.path.normpath(os.path.join(ROOT, PJ["source"]))
FONTS = f"{ROOT}/assets/fonts"
MASKS = f"{ROOT}/work/masks"


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


PAL = {k: hexrgb(v) for k, v in ST["palette"].items()}
F = ST["fonts"]


def font(role, kind, size):
    return ImageFont.truetype(f"{FONTS}/{F[role][kind]}", int(size))


# ---------------------------------------------------------------- timing helpers
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def lerp(a, b, k):
    return a + (b - a) * k


def ease_io(k):
    k = clamp(k)
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def ease_out(k):
    return 1 - (1 - clamp(k)) ** 3


def stepped(t, t0, fps):
    """Posterised time for TYPE / collage pieces only (picture and grain stay at 30 fps)."""
    if t < t0:
        return t
    return t0 + math.floor((t - t0) * fps + 1e-6) / fps


def scene_at(t):
    for s in PJ["scenes"]:
        if s["t0"] <= t < s["t1"]:
            return s
    return PJ["scenes"][-1]


# ---------------------------------------------------------------- grades
def presenter_lut():
    g = ST["grade_presenter"]
    x = np.arange(256, dtype=np.float32) / 255
    y = (g["black"] + (g["white"] - g["black"]) * x ** g["gamma"]) / 255
    y = y + 0.04 * np.sin(np.pi * x) * (x - 0.5) * -1           # gentle shoulder/toe softness
    return np.clip(y, 0, 1).astype(np.float32)


PLUT = presenter_lut()


def grade_presenter(rgb_u8):
    g = ST["grade_presenter"]
    o = PLUT[rgb_u8]
    lum = o @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    o = lum[..., None] + (o - lum[..., None]) * g["saturation"]
    o[..., 0] *= 1 + g["warmth"]
    o[..., 2] *= 1 - g["warmth"]
    return o


def grade_bw(rgb_f):
    """Bright neutral B&W for collage inserts (applied to their photographic/paper layers)."""
    g = ST["grade_bw"]
    lum = rgb_f @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    y = (g["black"] + (g["white"] - g["black"]) * np.clip(lum, 0, 1) ** g["gamma"]) / 255
    return np.repeat(y[..., None], 3, axis=2)


# ---------------------------------------------------------------- paper
def paper(w, h, base, seed, fibre=True, blotch=None):
    """Static paper texture (it belongs to the sheet; film grain is separate and per frame)."""
    pp = ST["paper"]
    blotch = pp["blotch"] if blotch is None else blotch
    r = np.random.default_rng(seed)
    low = r.standard_normal((h // 90 + 2, w // 90 + 2)).astype(np.float32)
    low = np.asarray(Image.fromarray(low, "F").resize((w, h), Image.BICUBIC))
    hi = r.standard_normal((h, w)).astype(np.float32)
    hi = soften(hi, 0.25)
    v = 1 + blotch * low + pp["speck"] * hi
    img = np.array(base, np.float32)[None, None, :] / 255 * v[..., None]
    if fibre:
        im = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(im)
        for _ in range(int(w * h * pp["fibre_density"])):
            x, y = r.uniform(0, w), r.uniform(0, h)
            a, l = r.uniform(0, math.pi), r.uniform(6, 26)
            d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=int(r.uniform(8, 20)), width=1)
        f = np.asarray(im.filter(ImageFilter.GaussianBlur(0.5)), np.float32) / 255
        img = img * (1 - 0.35 * f[..., None])
    return np.clip(img, 0, 1)


def soften(a, w):
    """Cheap separable 3-tap blur for float noise fields (Pillow cannot blur mode F)."""
    a = a * (1 - 2 * w) + (np.roll(a, 1, 0) + np.roll(a, -1, 0)) * w
    return a * (1 - 2 * w) + (np.roll(a, 1, 1) + np.roll(a, -1, 1)) * w


def to_im(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def shadowed(sprite, blur=14, off=(0, 10), alpha=0.42):
    a = sprite.getchannel("A")
    pad = blur * 3
    out = Image.new("RGBA", (sprite.width + 2 * pad, sprite.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", sprite.size, (20, 16, 12, 255))
    sh.putalpha(a.point(lambda v: int(v * alpha)))
    out.alpha_composite(sh, (pad + off[0], pad + off[1]))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sprite, (pad, pad))
    return out


def paste(base, spr, cx, cy, alpha=1.0, angle=0.0, scale=1.0):
    if alpha <= 0.004:
        return
    s = spr
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, round(s.width * scale)), max(1, round(s.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.01:
        s = s.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    x0, y0 = round(cx - s.width / 2), round(cy - s.height / 2)
    sx0, sy0 = max(0, -x0), max(0, -y0)
    sx1, sy1 = min(s.width, base.width - x0), min(s.height, base.height - y0)
    if sx1 > sx0 and sy1 > sy0:
        base.alpha_composite(s.crop((sx0, sy0, sx1, sy1)), (x0 + sx0, y0 + sy0))


# ---------------------------------------------------------------- inserts
PW = int(W * (1 - ST["split"]["at"]))           # insert panel width (right side)
_cache = {}
AR = ST["archival"]
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def surface(w, h, seed):
    """Shared archival table surface for every insert: textured card under one soft key light."""
    key = ("surface", w, h, seed)
    if key not in _cache:
        tex = paper(w, h, hexrgb(AR["surface"]), seed, fibre=True, blotch=AR["surface_blotch"])
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt(((xx - W * AR["light_xy"][0]) / (1.1 * W)) ** 2 + ((yy - H * AR["light_xy"][1]) / (0.95 * H)) ** 2)
        light = AR["light_hi"] - (AR["light_hi"] - AR["light_lo"]) * np.clip(d, 0, 1) ** 1.4
        _cache[key] = to_im(tex * light[..., None]).convert("RGBA")
    return _cache[key].copy()


def obj_shadow(spr):
    sh = AR["shadow"]
    return shadowed(spr, blur=sh["blur"], off=tuple(sh["off"]), alpha=sh["alpha"])


def archival(im, t, t0, t1):
    """Treat a drawn insert as filmed archival footage: slow rostrum push + drift,
    lens softness, bright neutral B&W. Muted-red ink keeps a touch of its colour."""
    w, h = im.size
    k = clamp((t - t0) / max(t1 - t0, 1e-3))
    z = lerp(1.02, AR["rostrum_push"], ease_io(k))            # starts slightly in so the drift has margin
    dx = AR["rostrum_drift_px"] * (ease_io(k) - 0.5)
    cw, ch = w / z, h / z
    x0 = clamp((w - cw) / 2 + dx / z, 0, w - cw)
    y0 = (h - ch) * 0.45
    rgb = im.convert("RGB").resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    rgb = rgb.filter(ImageFilter.GaussianBlur(AR["lens_soft_px"]))
    a = np.asarray(rgb, np.float32) / 255
    bw = grade_bw(a)
    red = np.clip((a[..., 0] - np.maximum(a[..., 1], a[..., 2]) - 0.08) / 0.15, 0, 1)[..., None]
    out = bw + red * (a - (a @ LUMA)[..., None]) * AR["ink_keep"]
    return to_im(out).convert("RGBA")


def receipt_panel(t, odx=0.0):
    if "thermal" not in _cache:
        _cache["thermal"] = paper(460, 2600, PAL["paper_white"], 12, fibre=False, blotch=0.006)
    panel = surface(PW, H, 11)
    mono = font("mono", "medium", 36)
    lines = []                                   # (text, t_print, colour)
    for ln in PJ["receipt_lines"]:
        lines.append((ln["text"], ln["t"], PAL["ink"]))
    feeds = PJ["receipt_feed"]
    lines.append(("- - - - - - - - - - - -", feeds[0], PAL["grey_rule"]))
    lines.append(("TOTAL", feeds[1], PAL["ink"]))
    ts = stepped(t, 3.2, ST["type_motion"]["stepped_fps"])
    n_printed = sum(1 for _, tp, _ in lines if ts >= tp)
    strip_h = 260 + 74 * max(n_printed, 1) + 160
    strip = to_im(_cache["thermal"][:strip_h]).convert("RGBA")
    d = ImageDraw.Draw(strip)
    mask = Image.new("L", strip.size, 255)
    md = ImageDraw.Draw(mask)
    for x in range(0, strip.width + 14, 14):                  # torn top + bottom
        md.polygon([(x, 0), (x + 7, 9), (x + 14, 0)], fill=0)
        md.polygon([(x, strip_h), (x + 7, strip_h - 9), (x + 14, strip_h)], fill=0)
    y = 120
    for text, tp, col in lines:
        if ts < tp:
            continue
        k = clamp((ts - tp) / 0.4)                            # typewriter reveal, stepped
        d.text((40, y), text[: max(1, int(len(text) * k))], font=mono, fill=col + (255,))
        if text.isupper() and text != "TOTAL" and k >= 1:
            dx = 40 + d.textlength(text, font=mono) + 14
            while dx < 420:
                d.ellipse((dx, y + 24, dx + 4, y + 28), fill=PAL["grey_rule"] + (255,))
                dx += 14
        if text == "TOTAL" and ts >= feeds[2]:                # muted-red ink ring, stop-motion
            ks = clamp((ts - feeds[2]) / 0.2)
            rr = int(lerp(110, 84, ks))
            cx, cy = 40 + d.textlength("TOTAL", font=mono) / 2, y + 22
            d.ellipse((cx - rr, cy - rr * 0.55, cx + rr, cy + rr * 0.55), outline=PAL["muted_red"] + (235,), width=4)
        y += 74
    strip.putalpha(mask)
    slot_y = 1350
    feed_jump = 0
    for ft in feeds:                                          # small paper jolt on each feed
        if 0 <= ts - ft < 0.2:
            feed_jump = 14 * (1 - (ts - ft) / 0.2)
    sp = obj_shadow(strip)
    pad = (sp.height - strip.height) // 2
    top = slot_y - strip.height - feed_jump
    panel.alpha_composite(sp, (int(PW / 2 + odx - sp.width / 2), int(top - pad)))
    pd = ImageDraw.Draw(panel)                                # printer slot the paper feeds from
    pd.rounded_rectangle((40 + odx, slot_y - 6, PW - 40 + odx, slot_y + 40), radius=10, fill=PAL["charcoal"] + (255,))
    pd.rectangle((70 + odx, slot_y - 2, PW - 70 + odx, slot_y + 6), fill=(10, 9, 8, 255))
    return panel


def ledger_panel(t, odx=0.0):
    if "card" not in _cache:
        cw, ch = 460, 940
        cim = to_im(paper(cw, ch, PAL["cream"], 22, blotch=0.02)).convert("RGBA")
        d = ImageDraw.Draw(cim)
        d.line([(0, 120), (cw, 120)], fill=PAL["muted_red"] + (220,), width=3)
        for i in range(1, 9):
            d.line([(0, 120 + i * 96), (cw, 120 + i * 96)], fill=PAL["grey_rule"] + (200,), width=2)
        mono = font("mono", "regular", 31)
        for i, name in enumerate(PJ["ledger"]):
            yy = 120 + i * 96 + 32
            d.rectangle((34, yy, 66, yy + 32), outline=PAL["ink"] + (255,), width=3)
            d.text((88, yy - 2), name, font=mono, fill=PAL["ink"] + (255,))
        _cache["card"] = cim
    panel = surface(PW, H, 21)
    card = _cache["card"].copy()
    d = ImageDraw.Draw(card)
    lc = PJ["ledger_check"]
    ts = stepped(t, lc["t"], ST["type_motion"]["stepped_fps"])
    for i in range(len(PJ["ledger"])):
        k = clamp((ts - (lc["t"] + i * lc["step"])) / 0.2)
        if k <= 0:
            continue
        yy = 120 + i * 96 + 32
        p0, p1, p2 = (36, yy + 16), (50, yy + 30), (76, yy - 6)
        if k < 0.5:
            q = k / 0.5
            d.line([p0, (lerp(p0[0], p1[0], q), lerp(p0[1], p1[1], q))], fill=PAL["muted_red"] + (255,), width=6)
        else:
            q = (k - 0.5) / 0.5
            d.line([p0, p1, (lerp(p1[0], p2[0], q), lerp(p1[1], p2[1], q))], fill=PAL["muted_red"] + (255,), width=6, joint="curve")
    paste(panel, obj_shadow(card), PW / 2 + odx, 1000, angle=-2.0)
    return panel


def tickets_frame(t, t0):
    if "tk" not in _cache:
        tk = []
        for i, tkt in enumerate(PJ["tickets"]):
            tw, th = 720, 220
            pim = to_im(paper(tw, th, PAL["cream"], 40 + i, blotch=0.02)).convert("RGBA")
            d = ImageDraw.Draw(pim)
            d.rectangle((10, 10, tw - 11, th - 11), outline=PAL["muted_red"] + (200,), width=2)
            for yy in range(14, th - 14, 18):                 # perforation
                d.ellipse((168, yy, 175, yy + 7), fill=hexrgb(AR["surface"]) + (255,))
            mono = font("mono", "regular", 24)
            lab = Image.new("RGBA", (180, 40), (0, 0, 0, 0))
            ImageDraw.Draw(lab).text((0, 4), "SUBSCRIPTION", font=mono, fill=PAL["ink"] + (230,))
            pim.alpha_composite(lab.rotate(90, expand=True), (60, 20))
            sf = font("serif", "italic", 112)
            nb = d.textbbox((0, 0), tkt["name"], font=sf)
            d.text((200 + (tw - 210 - (nb[2] - nb[0])) / 2 - nb[0], th / 2 - (nb[1] + nb[3]) / 2), tkt["name"], font=sf,
                   fill=PAL["ink"] + (255,))
            notch = Image.new("L", (tw, th), 255)
            nd = ImageDraw.Draw(notch)
            nd.ellipse((171 - 16, -16, 171 + 16, 16), fill=0)
            nd.ellipse((171 - 16, th - 16, 171 + 16, th + 16), fill=0)
            pim.putalpha(notch)
            tk.append(obj_shadow(pim))
        _cache["tk"] = tk
    im = surface(W, H, 31)
    d = ImageDraw.Draw(im)
    red = PAL["muted_red"] + (150,)
    for (cx, cy) in [(140, 260), (940, 260), (140, 1420), (940, 1420)]:   # registration marks
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), outline=red, width=2)
        d.line([(cx - 36, cy), (cx + 36, cy)], fill=red, width=2)
        d.line([(cx, cy - 36), (cx, cy + 36)], fill=red, width=2)
    k = ease_out((t - t0) / 0.6)                              # technical line draws across
    d.line([(80, 1395), (80 + 920 * k, 1395)], fill=red, width=2)
    pos = [(560, 520, -5), (520, 780, 3), (570, 1040, -2.5), (520, 1300, 4)]
    cf = ST["type_motion"]["collage_steps_fps"]
    for spr, tkt, (x, y, ang) in zip(_cache["tk"], PJ["tickets"], pos):
        ts = stepped(t, tkt["t"] - 0.12, cf)
        k = clamp((ts - (tkt["t"] - 0.12)) / 0.3)
        if k <= 0:
            continue
        e = ease_out(k)
        paste(im, spr, x, y - 160 * (1 - e), angle=ang + 10 * (1 - e), scale=lerp(1.08, 1.0, e))
    return im


def scene_by_id(i):
    return next(s for s in PJ["scenes"] if s["id"] == i)


# ---------------------------------------------------------------- presenter geometry
def presenter_state(t):
    """(scale, x_offset, panel_w) of the presenter picture; handles split entry / exit."""
    s = scene_at(t)
    sp = ST["split"]
    split_ox = FX - (W - PW) / 2                      # face to the centre of the left panel
    if s["kind"] == "split":
        e = ease_io((t - s["t0"]) / sp["entry_s"])
        prev = PJ["scenes"][PJ["scenes"].index(s) - 1]
        pscale = prev.get("push", [1, 1])[1] if prev["kind"] == "presenter" else 1.0
        return lerp(pscale, 1.0, e), lerp(0, split_ox, e), lerp(W, W - PW, e), e
    if s["kind"] == "presenter":
        k = (t - s["t0"]) / (s["t1"] - s["t0"])
        sc = lerp(*s["push"], ease_io(k))
        i = PJ["scenes"].index(s)
        if i > 0 and PJ["scenes"][i - 1]["kind"] == "split" and t - s["t0"] < sp["exit_s"]:
            e = 1 - ease_io((t - s["t0"]) / sp["exit_s"])
            return lerp(sc, 1.0, e), lerp(0, split_ox, e), lerp(W, W - PW, e), e
        return sc, 0.0, W, 0.0
    return 1.0, 0.0, W, 0.0


def presenter_box(scale, ox, pw):
    x0 = FX + (0 + ox - FX) / scale
    x1 = FX + (pw + ox - FX) / scale
    y0 = FY + (0 - FY) / scale
    y1 = FY + (H - FY) / scale
    return (x0, y0, x1, y1)


def mask_at(n):
    p = f"{MASKS}/m_{min(n, NF - 1):04d}.png"
    return Image.open(p).resize((W, H), Image.BICUBIC)


# ---------------------------------------------------------------- type
_spr = {}


def word_sprite(lay, colour):
    key = (lay["id"], colour)
    if key not in _spr:
        f = font("serif", "italic", lay["size"]) if lay["role"] == "serif" else font("sans", "heavy", lay["size"])
        d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        bb = d0.textbbox((0, 0), lay["text"], font=f)
        pad = 40
        im = Image.new("RGBA", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), lay["text"], font=f, fill=colour + (255,))
        if lay.get("underline"):
            _spr[key + ("ul",)] = (pad, im.height - pad + 18, im.width - pad)
        _spr[key] = im
    return _spr[key]


def type_state(lay, t):
    tm = ST["type_motion"]
    tt = stepped(t, lay["t0"], tm["stepped_fps"]) if lay.get("stepped") else t
    if tt < lay["t0"] or t >= lay["t1"]:
        return None
    ki = ease_out((tt - lay["t0"]) / tm["enter"])
    ko = clamp((lay["t1"] - t) / tm["exit"])
    alpha = min(ki, ease_out(ko))
    scale = lerp(1.14 if lay.get("stepped") else 1.04, 1.0, ki)
    dy = lerp(0.16, 0, ki) * lay["size"] - tm["drift_em_per_s"] * lay["size"] * (t - lay["t0"]) - (1 - ko) * 0.12 * lay["size"]
    return alpha, scale, dy, tt


def draw_type(layer_im, lay, t, colour, xoff=0.0):
    st = type_state(lay, t)
    if not st:
        return
    alpha, scale, dy, tt = st
    spr = word_sprite(lay, colour)
    if lay.get("underline"):
        pad, uy, ux1 = _spr[(lay["id"], colour, "ul")]
        k = ease_out((tt - lay["t0"] - 0.25) / 0.45)
        if k > 0:
            spr = spr.copy()
            ImageDraw.Draw(spr).line([(pad, uy), (lerp(pad, ux1, k), uy)], fill=PAL[lay["underline"]] + (255,), width=6)
    paste(layer_im, spr, lay["x"] + xoff, lay["y"] + dy, alpha=alpha, scale=scale)


# ---------------------------------------------------------------- captions (clean, above grain)
CAPF = font("sans", "medium", ST["captions"]["size_px"])
_cap = {}


def caption_sprite(text, max_w):
    key = (text, max_w)
    if key not in _cap:
        d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        lines, cur = [], []
        for wd in text.split(" "):                     # greedy wrap to the available width
            trial = " ".join(cur + [wd])
            if cur and d0.textlength(trial, font=CAPF) > max_w:
                lines.append(" ".join(cur)); cur = [wd]
            else:
                cur.append(wd)
        lines.append(" ".join(cur))
        asc, desc = CAPF.getmetrics()
        lh = int((asc + desc) * 1.08)
        tw = int(max(d0.textlength(l, font=CAPF) for l in lines))
        pad = 34
        im = Image.new("RGBA", (tw + 2 * pad, lh * len(lines) + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lines):
            d.text((pad + (tw - d0.textlength(l, font=CAPF)) / 2, pad + i * lh), l, font=CAPF, fill=PAL["cream"] + (255,))
        a = im.getchannel("A").filter(ImageFilter.GaussianBlur(11)).point(lambda v: min(255, int(v * ST["captions"]["shadow"] * 1.6)))
        sh = Image.new("RGBA", im.size, (8, 6, 5, 0))
        sh.putalpha(a)
        _cap[key] = Image.alpha_composite(sh, im)
    return _cap[key]


def split_windows():
    """Intervals where a split panel is on screen (scene + its exit into the next presenter shot)."""
    out = []
    for i, s in enumerate(PJ["scenes"]):
        if s["kind"] == "split":
            out.append((s["t0"], s["t1"] + ST["split"]["exit_s"]))
    return out


SPLITS = split_windows()


def draw_captions(im, t, pw):
    c_st = ST["captions"]
    cx = pw / 2                                           # centre glides with the presenter panel
    for c in PJ["captions"]:
        if c["t0"] <= t < c["t1"]:
            # line breaks are fixed for the whole chunk (no re-wrap while a panel moves)
            near_split = any(c["t0"] < b and c["t1"] > a for a, b in SPLITS)
            max_w = c_st["split_max_w"] if near_split else c_st["max_w"]
            k = ease_out((t - c["t0"]) / (5 / FPS))
            paste(im, caption_sprite(c["text"], max_w), cx, c_st["y"] + (1 - k) * 10, alpha=k)


# ---------------------------------------------------------------- film pass
_gr = np.random.default_rng(0)


def film(img, n):
    b = ST["bloom"]
    lum = img @ LUMA
    bright = np.clip((lum - b["threshold"]) / (1 - b["threshold"]), 0, 1)[..., None] * img
    small = Image.fromarray((bright * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(b["radius_px"] / 4))
    bl = np.asarray(small.resize((W, H), Image.BILINEAR), np.float32) / 255
    img = img + b["strength"] * bl
    g = ST["grain"]
    rng = np.random.default_rng(1000 + n)                 # fresh grain on every output frame
    noise = rng.standard_normal((H, W)).astype(np.float32)
    if g["size_px"] > 1:
        noise = soften(noise, clamp(0.25 * (g["size_px"] - 0.5) / 0.65, 0, 0.3))
        noise /= noise.std() + 1e-6
    lum = np.clip(img @ LUMA, 0, 1)
    wgt = 0.55 + 1.8 * lum * (1 - lum)                    # strongest in midtones
    img = img + (g["amplitude"] / 255) * (noise * wgt)[..., None]
    return np.clip(img, 0, 1)


# ---------------------------------------------------------------- frame
def frame_at(n, src):
    t = n / FPS
    s = scene_at(t)
    src_im = Image.fromarray(src)
    canvas = None
    occl = None                                            # presenter cut-out for text-behind
    insert_panel = None
    if s["kind"] == "fullscreen":
        canvas = archival(tickets_frame(t, s["t0"]), t, s["t0"], s["t1"]).convert("RGB")
    else:
        scale, ox, pw, e = presenter_state(t)
        vis = max(1, int(math.ceil(pw)))                     # only the visible presenter panel
        box = presenter_box(scale, ox, vis)
        pres = np.asarray(src_im.resize((vis, H), Image.BICUBIC, box=box))
        canvas = Image.new("RGB", (W, H), PAL["charcoal"])
        canvas.paste(to_im(grade_presenter(pres)), (0, 0))
        if pw < W - 0.5:                                    # split: insert panel slides in from the right
            sc_split = s if s["kind"] == "split" else PJ["scenes"][PJ["scenes"].index(s) - 1]
            odx = (1 - e) * AR["parallax_px"]                # contents trail the panel edge
            raw = receipt_panel(t, odx) if sc_split["insert"] == "receipt" else ledger_panel(t, odx)
            panel = archival(raw, t, sc_split["t0"], sc_split["t1"] + ST["split"]["exit_s"])
            insert_panel = (panel, int(round(pw)))
        else:
            m = mask_at(n).resize((W, H), Image.BICUBIC, box=presenter_box(scale, ox, W))
            occl = (canvas.copy(), m)
        # dissolve from the full-screen collage back into the presenter
        if s.get("enter_dissolve") and t - s["t0"] < s["enter_dissolve"]:
            prev = PJ["scenes"][PJ["scenes"].index(s) - 1]
            k = ease_io((t - s["t0"]) / s["enter_dissolve"])
            canvas = Image.blend(archival(tickets_frame(t, prev["t0"]), t, prev["t0"], prev["t1"]).convert("RGB"), canvas, k)
    im = canvas.convert("RGBA")
    if insert_panel:
        panel, x = insert_panel
        pnl = panel.copy()
        for lay in PJ["emphasis"]:
            if lay.get("panel") == "insert":
                draw_type(pnl, lay, t, PAL["cream"])          # clean type above the footage treatment
        sw = AR["seam_shadow_px"]                             # the panel casts a soft shadow on the presenter
        g = np.linspace(0, AR["seam_shadow_alpha"], sw) ** 1.6
        band = Image.fromarray(np.tile((g * 255).astype(np.uint8), (H, 1)), "L")
        sh = Image.new("RGBA", (sw, H), (8, 7, 6, 255))
        sh.putalpha(band)
        im.alpha_composite(sh, (max(0, x - sw), 0)) if x - sw >= 0 else None
        im.alpha_composite(pnl.crop((0, 0, min(PW, W - x), H)), (x, 0))
    # emphasis words in the presenter frame (behind the subject when flagged)
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for lay in PJ["emphasis"]:
        if lay.get("panel") != "insert":
            draw_type(tl, lay, t, PAL["cream"])
    if tl.getbbox():
        if occl:
            fg, m = occl
            tla = np.asarray(tl.getchannel("A"), np.float32) / 255
            tla = tla * (1 - np.asarray(m, np.float32) / 255)
            tl.putalpha(Image.fromarray((tla * 255).astype(np.uint8)))
        im.alpha_composite(tl)
    img = np.asarray(im.convert("RGB"), np.float32) / 255
    img = film(img, n)
    out = to_im(img).convert("RGBA")
    pw_now = presenter_state(t)[2] if s["kind"] != "fullscreen" else W
    draw_captions(out, t, pw_now)
    return out.convert("RGB")


def source_frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()


def main():
    if sys.argv[2] == "--stills":
        out, times = sys.argv[3], [float(x) for x in sys.argv[4:]]
        os.makedirs(out, exist_ok=True)
        want = {int(round(x * FPS)): x for x in times}
        for n, fr in enumerate(source_frames()):
            if n in want:
                frame_at(n, fr).save(f"{out}/t{want[n]:05.2f}.png")
        return
    out = sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    audio = sys.argv[3] if len(sys.argv) > 3 else None
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "256k"]
    else:                                                   # original sound, stream-copied untouched
        cmd += ["-i", SRC, "-map", "0:v", "-map", "1:a", "-c:a", "copy"]
    cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-x264-params", "keyint=60:min-keyint=30",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
            "-frames:v", str(NF), "-movflags", "+faststart", out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    for fr in source_frames():
        if n >= NF:
            break
        enc.stdin.write(frame_at(n, fr).tobytes())
        n += 1
        if n % 60 == 0:
            print(f"frame {n}/{NF}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", out, n)


if __name__ == "__main__":
    main()
