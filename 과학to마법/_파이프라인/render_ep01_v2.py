import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = 'fonts/public/static/'
IC = '/home/claude/assets/node_modules/@lobehub/fluent-emoji-3d/assets/'
PH = '/home/claude/assets/photos/'
_fc = {}
def F(size, w='Bold'):
    k = (int(size), w)
    if k not in _fc: _fc[k] = ImageFont.truetype(f'{FD}Pretendard-{w}.otf', int(size))
    return _fc[k]
GOLD = (255, 205, 80); WHITE = (245, 245, 255); BLUE = (80, 190, 255); RED = (255, 90, 90)
YEL = (255, 220, 70); GREEN = (90, 225, 140); DIM = (150, 150, 190)

R = json.load(open('tl2_raw.json')); T = R['tempo']; DUR = R['dur_raw'] / T
MAP = R['map']
def o2t(tau):  # original recording time -> output time
    for rs, re_, out in MAP:
        if rs <= tau < re_: return (out + tau - rs) / T
    best = min((p for p in MAP if p[0] >= tau), key=lambda p: p[0] - tau, default=MAP[-1])
    return best[2] / T

SUBS = [(92.98, "지금 귀에 꽂고 있는 그게 바로"), (95.28, "그 마법 아이템이에요"),
 (1.30, "판타지 4서클 마법"), (2.95, "사일런스!"), (4.86, "주변 소리를 완전히 지워버리는 마법"),
 (9.14, "현대 과학으로 가능할까?"), (11.79, "판정!"), (13.11, "일부 가능"),
 (16.81, "소리는 공기가 밀렸다 당겨지는 파동"), (20.67, "여기에 똑같은 모양을"), (22.58, "정반대로 뒤집어 겹치면"),
 (26.33, "둘이 서로를 지워서 0!"), (29.08, "이걸 상쇄 간섭이라고 해요"),
 (33.09, "사실 여러분 귀에 이미"), (34.73, "이 마법이 걸려 있어요"), (37.46, "바로 노이즈캔슬링 이어폰!"),
 (40.79, "바깥 소리를 마이크로 듣고"), (42.74, "정반대 소리를 순식간에 만들어"), (44.6, "귀 안에서 지우는 거죠"),
 (47.29, "사일런스 인챈트가 걸린"), (48.6, "마법 아이템인 셈"),
 (51.44, "그런데 왜 '일부'만?"), (53.94, "귀처럼 좁은 곳은 쉽지만"),
 (56.14, "넓은 공간에선"), (57.54, "한 곳에서 지운 소리가"), (58.9, "다른 곳에선 오히려 커져요"),
 (63.13, "게다가"), (64.14, "목소리 같은 높은 소리는"), (66.11, "파장이 수십 cm도 안 돼서"),
 (68.58, "조금만 어긋나도 실패!"), (71.60, "반면 엔진 같은 낮은 소리는"), (74.24, "파장이 몇 m라 훨씬 쉬워요"),
 (77.83, "그래서 실제로 창문에"), (80.06, "작은 스피커를 여러 개 달아"), (82.01, "바깥 소음을 줄이는 연구도 있어요"),
 (84.24, "결론!"), (86.67, "사일런스는 저음 한정"), (89.24, "좁은 공간 한정으로 이미 현실!"),
 (97.59, "다음엔 어떤 마법을 판정할까요?"), (99.89, "댓글로 주문을 걸어주세요")]
SUBT = sorted([(o2t(a), s) for a, s in SUBS])
SUBT = [(a, SUBT[i + 1][0] if i + 1 < len(SUBT) else DUR, s) for i, (a, s) in enumerate(SUBT)]
HL = ["상쇄 간섭", "일부 가능", "노이즈캔슬링", "사일런스", "저음", "좁은 공간", "마법 아이템", "파장", "0!", "정반대", "실패", "현실"]

BEATS = [(92.98, 'hook'), (1.30, 'wizard'), (2.95, 'title'), (4.86, 'mute'), (9.14, 'question'), (11.79, 'verdict'),
 (16.81, 'wave1'), (20.67, 'wave2'), (26.33, 'cancel'), (29.08, 'keyword'), (33.09, 'ear'), (37.46, 'products'),
 (40.79, 'mic'), (42.74, 'chip'), (44.6, 'ear_quiet'), (47.29, 'itemcard'), (51.44, 'why'), (53.94, 'ear_ok'),
 (56.14, 'interference'), (63.13, 'voice_wave'), (68.58, 'fail'), (71.60, 'engine'), (74.24, 'engine_ok'),
 (77.83, 'window'), (84.24, 'verdict2'), (86.67, 'low_ok'), (89.24, 'narrow_ok'), (97.59, 'cta')]
BT = sorted([(o2t(a), k) for a, k in BEATS]); BT[0] = (0.0, BT[0][1])
STAMP_T = [o2t(13.11), o2t(84.24)]

def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
def back(x):  # overshoot pop
    x = max(0., min(1., x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def A(c, a): return tuple(c[:3]) + (int(255 * max(0, min(1, a))),)

# ---------- assets ----------
_ic = {}
def icon_img(code):
    if code not in _ic: _ic[code] = Image.open(IC + code + '.webp').convert('RGBA')
    return _ic[code]
def photo_img(name, wpx, border=10, rad=36):
    key = (name, wpx)
    if key in _ic: return _ic[key]
    im = Image.open(PH + name + '.jpg').convert('RGB'); h = int(im.height * wpx / im.width)
    im = im.resize((wpx, h), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (wpx, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, wpx - 1, h - 1], rad, fill=255); im.putalpha(m)
    out = Image.new('RGBA', (wpx + 2 * border + 60, h + 2 * border + 60), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).rounded_rectangle([30 + 10, 30 + 18, 30 + wpx + 2 * border + 10, 30 + h + 2 * border + 18], rad + border, fill=150)
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(out).rounded_rectangle([30, 30, 30 + wpx + 2 * border, 30 + h + 2 * border], rad + border, fill=(255, 255, 255, 255))
    out.alpha_composite(im, (30 + border, 30 + border)); _ic[key] = out; return out

S = 2; SY, SH = 300, 1080   # scene layer local coords 0..1080 x 0..1080 -> global y 300..1380
class L:
    def __init__(s): s.im = Image.new('RGBA', (W * S, SH * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def line(s, pts, fill, w): s.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint='curve')
    def circ(s, c, r, outline=None, fill=None, w=3):
        x, y = c; s.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=outline, fill=fill, width=int(w * S))
    def rrect(s, b, r, outline=None, fill=None, w=3): s.d.rounded_rectangle([v * S for v in b], r * S, outline=outline, fill=fill, width=int(w * S))
    def text(s, xy, txt, size, fill, wt='Black', stroke=0, anchor='mm'):
        s.d.text((xy[0] * S, xy[1] * S), txt, font=F(size * S, wt), fill=fill, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=(0, 0, 0))
    def paste(s, im, c, scale=1.0, alpha=1.0, rot=0):
        if scale <= 0.02 or alpha <= 0.01: return
        w, h = int(im.width * scale * S), int(im.height * scale * S)
        if w < 2 or h < 2: return
        x = im.resize((w, h), Image.BICUBIC)
        if rot: x = x.rotate(rot, resample=Image.BICUBIC, expand=True)
        if alpha < 1: x.putalpha(x.getchannel('A').point(lambda v: int(v * alpha)))
        s.im.alpha_composite(x, (int(c[0] * S - x.width / 2), int(c[1] * S - x.height / 2)))
    def icon(s, code, c, size, ts, delay=0, bob=True, alpha=1.0, t=0, pop=True):
        k = ts - delay
        if k < 0: return
        sc = back(k / 0.28) if pop else 1
        dy = 8 * math.sin(t * 3 + c[0]) if bob else 0
        s.paste(icon_img(code), (c[0], c[1] + dy), size / 256 * sc, alpha)
    def photo(s, name, c, wpx, ts, delay=0, rot=0, slam=True):
        k = ts - delay
        if k < 0: return
        sc = 1 + 0.35 * (1 - ease(k / 0.2)) if slam else 1
        s.paste(photo_img(name, wpx), c, sc / 1, min(1, k / 0.08), rot)
    def done(s): return s.im.resize((W, SH), Image.LANCZOS)

def wave(L_, y, amp, k, ph, col, w=8, x0=80, x1=1000, alpha=1.0, n=240):
    xs = np.linspace(x0, x1, n); ys = y - amp * np.sin(k * (xs - x0) - ph)
    L_.line(list(zip(xs, ys)), A(col, alpha), w)

def magic_circle(L_, c, r, t, alpha=1.0, col=GOLD):
    L_.circ(c, r, outline=A(col, alpha), w=5); L_.circ(c, r * 0.84, outline=A(col, alpha * 0.7), w=3)
    for k in range(12):
        a = t * 0.6 + k * math.pi / 6; L_.circ((c[0] + r * 0.92 * math.cos(a), c[1] + r * 0.92 * math.sin(a)), 8, fill=A(col, alpha))
    for sgn, off in ((1, 0), (-1, math.pi / 3)):
        pts = [(c[0] + r * 0.84 * math.cos(sgn * t * 0.4 + off + j * 2 * math.pi / 3), c[1] + r * 0.84 * math.sin(sgn * t * 0.4 + off + j * 2 * math.pi / 3)) for j in range(4)]
        L_.line(pts, A(col, alpha * 0.6), 4)

def sparkles(L_, t, ts, n=6, cx=540, cy=540, rad=380):
    for i in range(n):
        a = i * 2 * math.pi / n + t * 0.5; r = rad + 30 * math.sin(t * 2 + i)
        L_.icon('2728', (cx + r * math.cos(a), cy + r * math.sin(a)), 90, ts, delay=0.05 * i, bob=False, alpha=0.5 + 0.5 * abs(math.sin(t * 3 + i)))

def badge(L_, txt, c, ts, col=GOLD, size=64):
    a = ease(ts / 0.2); f = F(size * S, 'Black'); tw = L_.d.textlength(txt, font=f) / S
    L_.rrect([c[0] - tw / 2 - 34, c[1] - size * 0.72, c[0] + tw / 2 + 34, c[1] + size * 0.72], size * 0.72, fill=A((15, 12, 40), 0.85 * a), outline=A(col, a), w=5)
    L_.text(c, txt, size, A(col, a))

def stamp(img, text, cx, cy, ts, size=150, col=YEL, rot=-8):
    if ts < 0: return
    sc = 1 + 0.9 * (1 - ease(ts / 0.18)); f = F(size, 'Black')
    tmp = Image.new('RGBA', (1000, 360), (0, 0, 0, 0)); dd = ImageDraw.Draw(tmp); tw = dd.textlength(text, font=f)
    dd.rounded_rectangle([500 - tw / 2 - 44, 180 - size * 0.78, 500 + tw / 2 + 44, 180 + size * 0.78], 30, outline=col, width=14, fill=(20, 16, 40, 200))
    dd.text((500, 186), text, font=f, fill=col, anchor='mm')
    tmp = tmp.rotate(rot, resample=Image.BICUBIC).resize((int(1000 * sc), int(360 * sc)), Image.BICUBIC)
    img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))

GX, GY = np.meshgrid(np.linspace(-1, 1, 216), np.linspace(0, 1.6, 180))
SRC = [(-0.22, 0.05), (0.22, 0.05)]
R1 = np.hypot(GX - SRC[0][0], GY - SRC[0][1]); R2 = np.hypot(GX - SRC[1][0], GY - SRC[1][1])

# ---------- background ----------
rng = np.random.default_rng(3)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), rng.uniform(0, 6.28)) for _ in range(80)]
yy, xx = np.mgrid[0:H, 0:W]
BASE = np.zeros((H, W, 3), np.float32); g = (yy / H)[..., None]
BASE[:] = np.array([8, 8, 24]) * (1 - g) + np.array([20, 14, 46]) * g
PAL = [(90, 60, 200), (30, 120, 200), (200, 70, 120), (40, 160, 140), (210, 140, 40), (120, 60, 190)]
GLOW = []
for c in PAL:
    d = np.sqrt(((xx - 540) / 700) ** 2 + ((yy - 840) / 800) ** 2); m = np.clip(1 - d, 0, 1)[..., None] ** 2
    GLOW.append(Image.fromarray(np.clip(BASE + np.array(c) * 0.55 * m, 0, 255).astype(np.uint8)))

def background(t, bi):
    a = GLOW[bi % len(GLOW)]; b = GLOW[(bi + 1) % len(GLOW)]
    img = a.copy(); d = ImageDraw.Draw(img)
    for x, y, r, ph in STARS:
        al = 0.5 + 0.5 * math.sin(t * 1.3 + ph); c = int(90 + 120 * al); y2 = (y - t * 20 * r) % H
        d.ellipse([x - r, y2 - r, x + r, y2 + r], fill=(c, c, min(255, c + 40)))
    d.rounded_rectangle([370, 150, 710, 214], 32, fill=(15, 12, 40), outline=GOLD, width=3)
    d.text((540, 182), "4서클 · 사일런스", font=F(36, 'Black'), fill=GOLD, anchor='mm')
    return img

# ---------- scenes ----------
def scene(t):
    bi = max(i for i, (s, _) in enumerate(BT) if t >= s - 1e-6); s0, kind = BT[bi]; ts = t - s0
    Lr = L(); post = []; C = (540, 520)
    if kind == 'hook':
        sparkles(Lr, t, ts, 8, 540, 500, 420)
        Lr.photo('airpods', (540, 500), 760, ts, rot=-4)
        badge(Lr, "🪄 마법 아이템?".replace("🪄 ", ""), (540, 930), ts - 0.4)
        Lr.icon('1fa84', (870, 860), 170, ts, delay=0.4, t=t)
    elif kind == 'wizard':
        magic_circle(Lr, C, 400, t, ease(ts / 0.3)); Lr.icon('1f9d9', C, 430, ts, t=t)
        badge(Lr, "4서클", (540, 980), ts - 0.1)
    elif kind == 'title':
        magic_circle(Lr, C, 400, t, 0.5); Lr.icon('1f507', (540, 430), 380, ts, t=t)
        Lr.text((540, 820), "SILENCE", 150, A(GOLD, ease(ts / 0.15)), stroke=4)
    elif kind == 'mute':
        k = ease((ts - 0.9) / 0.25)
        Lr.icon('1f50a', (300, 520), 340, ts, t=t, alpha=1 - 0.6 * k)
        Lr.text((540, 520), "→", 140, A(WHITE, 1))
        Lr.icon('1f507', (790, 520), 340, ts, delay=0.9, t=t)
        if 0.9 < ts < 1.3: Lr.icon('1f4a5', (790, 520), 520, ts, delay=0.9, bob=False, alpha=1 - (ts - 0.9) / 0.4)
    elif kind == 'question':
        Lr.icon('1f9ea', (330, 520), 380, ts, t=t); Lr.icon('1f914', (760, 470), 340, ts, delay=0.25, t=t)
        Lr.text((760, 760), "?", 200, A(YEL, ease((ts - 0.3) / 0.2)))
    elif kind == 'verdict':
        st = STAMP_T[0] - t
        Lr.icon('2696-fe0f' if False else '1f3af', (540, 420), 360, ts, t=t, alpha=1 if st > 0 else 0.35)
        post.append(lambda img: stamp(img, "일부 가능", 540, SY + 560, -st))
    elif kind == 'wave1':
        Lr.icon('1f62e', (180, 520), 260, ts, t=t)
        wave(Lr, 520, 150, 0.03, t * 9, BLUE, 12, 330, 1020, ease(ts / 0.3))
    elif kind == 'wave2':
        wave(Lr, 330, 130, 0.03, t * 9, BLUE, 11, 80, 1000)
        a2 = ease((ts - 0.5) / 0.4)
        wave(Lr, 740, 130 * a2, 0.03, t * 9 + math.pi, RED, 11, 80, 1000, a2)
        Lr.icon('1f504', (540, 535), 150, ts, delay=0.5, bob=False)
    elif kind == 'cancel':
        p = ease((ts - 0.25) / 0.9)
        wave(Lr, 220, 100, 0.03, t * 9, BLUE, 9); wave(Lr, 430, 100, 0.03, t * 9 + math.pi, RED, 9)
        Lr.text((70, 325), "+", 90, A(WHITE, 1)); Lr.text((70, 580), "=", 90, A(WHITE, 1))
        xs = np.linspace(80, 1000, 240); ys = 720 - 100 * (1 - p) * np.sin(0.03 * (xs - 80) - t * 9)
        Lr.line(list(zip(xs, ys)), A(YEL, 1), 13)
        Lr.text((540, 920), "0", 200 * (0.6 + 0.4 * back((ts - 1.0) / 0.25)), A(YEL, ease((ts - 1.0) / 0.15)))
    elif kind == 'keyword':
        sparkles(Lr, t, ts, 6, 540, 520, 400)
        Lr.text((540, 470), "상쇄", 210 * (0.6 + 0.4 * back(ts / 0.25)), A(YEL, ease(ts / 0.12)), stroke=4)
        Lr.text((540, 690), "간섭", 210 * (0.6 + 0.4 * back((ts - 0.1) / 0.25)), A(YEL, ease((ts - 0.1) / 0.12)), stroke=4)
    elif kind == 'ear':
        Lr.circ(C, 260 + 20 * math.sin(t * 4), fill=A((255, 220, 120), 0.18)); Lr.icon('1f442', C, 440, ts, t=t)
        sparkles(Lr, t, ts, 5, 540, 520, 360)
    elif kind == 'products':
        Lr.photo('airpods_case', (330, 470), 520, ts, rot=6)
        Lr.photo('buds', (770, 590), 380, ts, delay=0.35, rot=-7)
        badge(Lr, "노캔 = 마법 아이템", (540, 1000), ts - 0.5, size=56)
    elif kind == 'mic':
        Lr.icon('1f3a4', (700, 520), 330, ts, t=t)
        for i in range(4):
            r = ((t * 260 + i * 90) % 360); Lr.d.arc([(120 + r - 160) * S, 360 * S, (120 + r) * S, 680 * S], -55, 55, fill=A(BLUE, 1 - r / 360), width=9 * S)
    elif kind == 'chip':
        Lr.icon('2699-fe0f', (250, 420), 300, ts, t=t)
        wave(Lr, 800, 110, 0.035, t * 9 + math.pi, RED, 11, 80, 1000, ease((ts - 0.2) / 0.3))
        Lr.icon('26a1', (700, 420), 230, ts, delay=0.15, t=t)
    elif kind == 'ear_quiet':
        Lr.icon('1f442', (380, 520), 400, ts, t=t); Lr.icon('1f507', (780, 420), 260, ts, delay=0.3, t=t)
        Lr.icon('2728', (780, 700), 150, ts, delay=0.45, t=t)
    elif kind == 'itemcard':
        a = ease(ts / 0.25); y0 = 160 + 80 * (1 - a)
        Lr.rrect([110, y0, 970, y0 + 760], 40, fill=A((16, 12, 44), 0.95 * a), outline=A(GOLD, a), w=7)
        Lr.text((540, y0 + 80), "★★★ 희귀 아이템", 58, A(GOLD, a))
        if ts > 0.1: Lr.photo('airpods', (540, y0 + 360), 600, ts - 0.1, slam=False)
        Lr.icon('1f507', (240, y0 + 650), 130, ts, delay=0.35, bob=False); Lr.text((330, y0 + 650), "사일런스 +1", 62, A(WHITE, ease((ts - 0.35) / 0.2)), anchor='lm')
        sparkles(Lr, t, ts, 6, 540, y0 + 380, 470)
    elif kind == 'why':
        Lr.icon('1f914', C, 470, ts, t=t); Lr.text((850, 260), "?", 180, A(YEL, ease((ts - 0.2) / 0.2)), stroke=3)
    elif kind == 'ear_ok':
        Lr.icon('1f442', (400, 520), 400, ts, t=t); Lr.icon('2705', (790, 520), 280, ts, delay=0.3, t=t)
    elif kind == 'interference':
        a = ease(ts / 0.3)
        Iq = np.cos(22 * (R1 - R2) / 2) ** 2; v = Iq * (0.85 + 0.15 * np.sin(22 * (R1 + R2) / 2 - t * 9))
        col = np.stack([40 + 215 * v, 30 + 150 * v, 70 + 30 * v], -1)
        m = Image.fromarray(col.clip(0, 255).astype(np.uint8)).resize((940 * S, 720 * S), Image.BICUBIC).convert('RGBA')
        mk = Image.new('L', m.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, m.width, m.height], 40 * S, fill=int(255 * a)); m.putalpha(mk)
        Lr.im.alpha_composite(m, (70 * S, 120 * S))
        for sx, sy in SRC: Lr.icon('1f50a', (540 + sx * 470, 120 + sy * 450), 110, ts, bob=False)
        Lr.icon('1f4e2', (540, 620), 150, ts, delay=1.2, bob=False); Lr.icon('1f507', (360, 760), 130, ts, delay=1.0, bob=False)
    elif kind == 'voice_wave':
        Lr.icon('1f62e', (190, 330), 250, ts, t=t)
        wave(Lr, 330, 90, 0.11, t * 14, BLUE, 8, 340, 1010, ease(ts / 0.3))
        Lr.icon('1f4cf', (300, 760), 200, ts, delay=0.6, t=t); Lr.text((640, 760), "~11cm", 120, A(BLUE, ease((ts - 0.7) / 0.2)), stroke=3)
    elif kind == 'fail':
        sh = 18 * math.sin(ts * 60) * max(0, 1 - ts / 0.5)
        Lr.icon('274c', (540 + sh, 520), 520, ts, bob=False)
    elif kind == 'engine':
        Lr.icon('2708-fe0f', (300, 380), 300, ts, t=t); Lr.icon('1f697', (760, 400), 280, ts, delay=0.2, t=t)
        wave(Lr, 780, 150, 0.006, t * 3, GREEN, 13, 60, 1020, ease((ts - 0.3) / 0.3))
    elif kind == 'engine_ok':
        Lr.photo('bose', (540, 430), 700, ts, rot=-3)
        Lr.text((420, 860), "~3.4m", 120, A(GREEN, ease((ts - 0.3) / 0.2)), stroke=3); Lr.icon('2705', (820, 860), 200, ts, delay=0.45, t=t)
    elif kind == 'window':
        Lr.icon('1fa9f', (540, 500), 480, ts, t=t)
        for i, (x, y) in enumerate([(260, 260), (820, 260), (260, 740), (820, 740), (540, 180), (540, 830)]):
            Lr.icon('1f50a', (x, y), 120, ts, delay=0.6 + 0.08 * i, bob=False)
        Lr.icon('1f3d9-fe0f', (160, 950), 170, ts, delay=0.2, t=t); Lr.icon('1f9ea', (920, 950), 160, ts, delay=1.4, t=t)
    elif kind == 'verdict2':
        magic_circle(Lr, C, 400, t, 0.4)
        post.append(lambda img: stamp(img, "판정", 540, SY + 520, ts, size=170, rot=0))
    elif kind == 'low_ok':
        Lr.icon('2708-fe0f', (280, 420), 260, ts, t=t); Lr.icon('1f697', (580, 420), 240, ts, delay=0.15, t=t); Lr.icon('2705', (860, 420), 220, ts, delay=0.3, t=t)
        badge(Lr, "저음 ✔".replace(" ✔", ""), (540, 800), ts - 0.2, col=GREEN, size=90)
    elif kind == 'narrow_ok':
        Lr.photo('airpods_case', (330, 470), 440, ts, rot=5); Lr.photo('buds', (760, 520), 330, ts, delay=0.2, rot=-6)
        Lr.icon('2705', (540, 900), 220, ts, delay=0.4, t=t); sparkles(Lr, t, ts, 6, 540, 520, 440)
    elif kind == 'cta':
        magic_circle(Lr, (540, 430), 330, t, 0.45); Lr.icon('1f9d9', (540, 430), 340, ts, t=t)
        Lr.icon('1f4ac', (840, 250), 200, ts, delay=0.3, t=t); Lr.text((840, 240), "?", 100, A((40, 40, 60), ease((ts - 0.4) / 0.2)))
        a = ease((ts - 0.8) / 0.2)
        Lr.rrect([360, 880, 720, 990], 55, fill=A((235, 40, 40), a)); Lr.text((540, 935), "구독", 64, A(WHITE, a))
    # punch-in on every cut
    z = 1 + 0.10 * (1 - ease(ts / 0.18))
    return Lr.done(), post, bi, z, ts

def draw_sub(img, t):
    cur = [c for a, b, c in SUBT if a - 0.03 <= t < b]
    if not cur: return
    s = cur[-1]; f = F(72, 'Black'); d = ImageDraw.Draw(img)
    lines = [s]
    if d.textlength(s, font=f) > 940 and ' ' in s:
        sp = [i for i, ch in enumerate(s) if ch == ' ']; mid = min(sp, key=lambda i: abs(i - len(s) / 2)); lines = [s[:mid], s[mid + 1:]]
    y0 = 1500 - (len(lines) - 1) * 46
    for k, ln in enumerate(lines):
        runs = []; i = 0
        while i < len(ln):
            hit = next((h for h in HL if ln.startswith(h, i)), None)
            if hit: runs.append((hit, YEL)); i += len(hit)
            else:
                if runs and runs[-1][1] == WHITE: runs[-1] = (runs[-1][0] + ln[i], WHITE)
                else: runs.append((ln[i], WHITE))
                i += 1
        tw = sum(d.textlength(r, font=f) for r, _ in runs); x = 540 - tw / 2; y = y0 + k * 92
        for r, col in runs:
            d.text((x, y), r, font=f, fill=col, anchor='lm', stroke_width=8, stroke_fill=(0, 0, 0)); x += d.textlength(r, font=f)

def frame(t):
    sc, post, bi, z, ts = scene(t)
    img = background(t, bi).convert('RGBA')
    if z > 1.001:
        w, h = int(W * z), int(SH * z); sc = sc.resize((w, h), Image.BICUBIC).crop(((w - W) // 2, (h - SH) // 2, (w - W) // 2 + W, (h - SH) // 2 + SH))
    img.alpha_composite(sc, (0, SY))
    for p in post: p(img)
    if ts < 0.07 and t > 0.1:
        img = Image.blend(img, Image.new('RGBA', img.size, (255, 255, 255, 255)), 0.35 * (1 - ts / 0.07))
    draw_sub(img, t)
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'v2_{tt}.png')
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'info':
        print(round(DUR, 2)); print([(round(a, 2), k) for a, k in BT]); sys.exit()
    n = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', 'video2.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0: print(i, n, flush=True)
    p.stdin.close(); p.wait()
    json.dump({'cuts': [a for a, _ in BT[1:]], 'stamp': STAMP_T, 'chime': [o2t(47.29), o2t(92.98)], 'dur': DUR}, open('sfx2.json', 'w'))
    with open('EP01.srt', 'w') as f:
        def tsf(x): return f"{int(x//3600):02}:{int(x%3600//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        for k, (a, b, c) in enumerate(SUBT, 1): f.write(f"{k}\n{tsf(a)} --> {tsf(b)}\n{c}\n\n")
    print('done')
