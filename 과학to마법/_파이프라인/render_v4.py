"""과학to마법 렌더러 v3 — 레퍼런스 분석 반영
- 결론(판정) 3~4초 안, 마나 게이지(상단, 카운트다운 대체), 키네틱 자막(1~2단어 팝)
- 밝은 단색 배경 / 어두운 마법 배경 교차, 피사체 크게, 색 규칙(소음=빨강, 반대소리=파랑)
- 스쿼시&스트레치 팝, 휩 전환, 임팩트 셰이크, 마나 계산기 인터루드, 마법 재료 카드
"""
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = 'fonts/public/static/'
IC = '/home/claude/assets/node_modules/@lobehub/fluent-emoji-3d/assets/'
PH = '/home/claude/assets/photos/'
_fc = {}
def F(size, w='Black'):
    k = (int(size), w)
    if k not in _fc: _fc[k] = ImageFont.truetype(f'{FD}Pretendard-{w}.otf', int(size))
    return _fc[k]
WHITE = (255, 255, 255); INK = (18, 16, 40); GOLD = (255, 205, 80); YEL = (255, 222, 60)
NOISE = (255, 72, 72); ANTI = (50, 150, 255); GREEN = (40, 200, 120); MANA = (90, 170, 255)

# ---------- timeline ----------
R = json.load(open('tl2_raw.json')); MAP = R['map']
T = 1.16; INS_LEN = 4.2
def base(tau):
    for rs, re_, out in MAP:
        if rs <= tau < re_: return (out + tau - rs) / T
    best = min((p for p in MAP if p[0] >= tau), key=lambda p: p[0] - tau, default=MAP[-1])
    return best[2] / T
INS_AT = base(97.59) - 0.12
def o2t(tau):
    t = base(tau); return t + INS_LEN if t >= INS_AT else t
DUR = R['dur_raw'] / T + INS_LEN

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
S0 = sorted([(o2t(a), s) for a, s in SUBS])
CHUNKS = [(a, S0[i + 1][0] if i + 1 < len(S0) else DUR, s) for i, (a, s) in enumerate(S0)]
CHUNKS = [(a, (INS_AT if a < INS_AT < b else b), s) for a, b, s in CHUNKS]
# kinetic phrases: 1~2 words, <= 8 chars
PHR = []
for a, b, s in CHUNKS:
    ws = s.split(' '); groups = []; cur = ''
    for w in ws:
        if cur and len((cur + w).replace(' ', '')) > 7: groups.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    groups.append(cur)
    tot = sum(len(g.replace(' ', '')) for g in groups); t0 = a
    for g in groups:
        d = (b - a) * len(g.replace(' ', '')) / tot; PHR.append((t0, t0 + d, g)); t0 += d
KEY = ["상쇄 간섭", "일부 가능", "노이즈캔슬링", "사일런스", "저음", "좁은", "마법 아이템", "파장", "0!", "정반대로", "정반대", "실패!", "현실!", "4서클", "판정!", "결론!", "이어폰!"]

BEATS = [(92.98, 'hook'), (1.30, 'wizard'), (2.95, 'title'), (4.86, 'mute'), (9.14, 'question'), (11.79, 'verdict'),
 (16.81, 'wave1'), (20.67, 'wave2'), (26.33, 'cancel'), (29.08, 'keyword'), (33.09, 'ear'), (37.46, 'products'),
 (40.79, 'mic'), (42.74, 'chip'), (44.6, 'ear_quiet'), (47.29, 'itemcard'), (51.44, 'why'), (53.94, 'ear_ok'),
 (56.14, 'interference'), (63.13, 'voice_wave'), (68.58, 'fail'), (71.60, 'engine'), (74.24, 'engine_ok'),
 (77.83, 'window'), (84.24, 'verdict2'), (86.67, 'low_ok'), (89.24, 'narrow_ok'), (97.59, 'cta')]
BT = sorted([(o2t(a), k) for a, k in BEATS] + [(INS_AT, 'manacalc')]); BT[0] = (0.0, BT[0][1])
STAMP_T = [o2t(13.11), o2t(84.24)]
MC_REVEAL = INS_AT + 2.3

BG = {'hook': 'dark', 'wizard': 'dark', 'title': 'dark', 'mute': (255, 107, 107), 'question': (77, 150, 255), 'verdict': 'dark',
      'wave1': (77, 150, 255), 'wave2': (77, 150, 255), 'cancel': (46, 196, 182), 'keyword': (255, 205, 60), 'ear': (120, 220, 170),
      'products': (255, 205, 60), 'mic': (255, 120, 90), 'chip': (46, 196, 182), 'ear_quiet': (120, 220, 170), 'itemcard': 'dark',
      'why': (255, 205, 60), 'ear_ok': (120, 220, 170), 'interference': 'dark', 'voice_wave': (255, 120, 90), 'fail': (235, 60, 60),
      'engine': (77, 150, 255), 'engine_ok': (120, 220, 170), 'window': (46, 196, 182), 'verdict2': 'dark', 'low_ok': (120, 220, 170),
      'narrow_ok': (255, 205, 60), 'manacalc': 'dark', 'cta': 'dark'}

CH = '/home/claude/assets/char/'
_ch = {}
def char_img(pose):
    if pose not in _ch: _ch[pose] = Image.open(CH + pose + '.png').convert('RGBA')
    return _ch[pose]
_pip = {}
def pip_img(pose, d=230):
    if (pose, d) not in _pip:
        im = char_img(pose).crop((150, 200, 750, 800)).resize((d, d), Image.LANCZOS)
        m = Image.new('L', (d, d), 0); ImageDraw.Draw(m).ellipse([0, 0, d - 1, d - 1], fill=255)
        bg = Image.new('RGBA', (d, d), (92, 70, 170, 255)); bg.alpha_composite(im); bg.putalpha(m)
        out = Image.new('RGBA', (d + 18, d + 18), (0, 0, 0, 0)); ImageDraw.Draw(out).ellipse([0, 0, d + 17, d + 17], fill=(233, 185, 73, 255))
        out.alpha_composite(bg, (9, 9)); _pip[(pose, d)] = out
    return _pip[(pose, d)]
PIP = {'hook': 'smug', 'title': 'smug', 'mute': 'smug_talk', 'question': 'smug', 'wave1': 'smug', 'wave2': 'smug', 'cancel': 'shock',
       'keyword': 'pout', 'ear': 'smug', 'products': 'shock', 'mic': 'pout', 'chip': 'pout', 'ear_quiet': 'pout', 'itemcard': 'angry',
       'why': 'smug', 'ear_ok': 'pout', 'interference': 'ohoho', 'voice_wave': 'smug', 'fail': 'ohoho', 'engine': 'pout', 'engine_ok': 'angry',
       'window': 'shock', 'verdict2': 'smug', 'low_ok': 'pout', 'narrow_ok': 'angry', 'verdict': 'smug'}
PIP_C = (925, 345)

def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
def eout(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def back(x): x = max(0., min(1., x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def squash(k, dur=0.32):  # returns (sx, sy) squash & stretch on appear
    if k < 0: return 0, 0
    p = min(1, k / dur); s = back(p)
    wob = math.sin(p * math.pi * 2.2) * (1 - p) * 0.22
    return s * (1 + wob), s * (1 - wob)
def A(c, a): return tuple(c[:3]) + (int(255 * max(0, min(1, a))),)

# ---------- assets ----------
_ic = {}
def icon_img(code):
    if code not in _ic: _ic[code] = Image.open(IC + code + '.webp').convert('RGBA')
    return _ic[code]
def photo_img(name, wpx, border=12, rad=40):
    key = (name, wpx)
    if key in _ic: return _ic[key]
    im = Image.open(PH + name + '.jpg').convert('RGB'); h = int(im.height * wpx / im.width)
    im = im.resize((wpx, h), Image.LANCZOS).convert('RGBA')
    m = Image.new('L', (wpx, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, wpx - 1, h - 1], rad, fill=255); im.putalpha(m)
    out = Image.new('RGBA', (wpx + 2 * border + 80, h + 2 * border + 80), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).rounded_rectangle([52, 64, 52 + wpx + 2 * border, 64 + h + 2 * border], rad + border, fill=170)
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    ImageDraw.Draw(out).rounded_rectangle([40, 40, 40 + wpx + 2 * border, 40 + h + 2 * border], rad + border, fill=(255, 255, 255, 255))
    out.alpha_composite(im, (40 + border, 40 + border)); _ic[key] = out; return out

S = 2; SY, SH = 250, 1080
class L:
    def __init__(s): s.im = Image.new('RGBA', (W * S, SH * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def line(s, pts, fill, w): s.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint='curve')
    def circ(s, c, r, outline=None, fill=None, w=3):
        x, y = c; s.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=outline, fill=fill, width=int(w * S))
    def rrect(s, b, r, outline=None, fill=None, w=3): s.d.rounded_rectangle([v * S for v in b], r * S, outline=outline, fill=fill, width=int(w * S))
    def text(s, xy, txt, size, fill, wt='Black', stroke=0, sfill=INK, anchor='mm'):
        s.d.text((xy[0] * S, xy[1] * S), txt, font=F(size * S, wt), fill=fill, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=sfill)
    def paste(s, im, c, sx=1.0, sy=None, alpha=1.0, rot=0):
        sy = sx if sy is None else sy
        if sx <= 0.02 or sy <= 0.02 or alpha <= 0.01: return
        w, h = int(im.width * sx * S), int(im.height * sy * S)
        if w < 2 or h < 2: return
        x = im.resize((w, h), Image.BICUBIC)
        if rot: x = x.rotate(rot, resample=Image.BICUBIC, expand=True)
        if alpha < 1: x.putalpha(x.getchannel('A').point(lambda v: int(v * alpha)))
        s.im.alpha_composite(x, (int(c[0] * S - x.width / 2), int(c[1] * S - x.height / 2)))
    def icon(s, code, c, size, ts, delay=0, bob=True, alpha=1.0, t=0, rot=0):
        k = ts - delay
        if k < 0: return
        sx, sy = squash(k); dy = 10 * math.sin(t * 3.2 + c[0]) if bob else 0
        s.paste(icon_img(code), (c[0], c[1] + dy + (1 - sy) * size * 0.25), size / 256 * sx, size / 256 * sy, alpha, rot)
    def photo(s, name, c, wpx, ts, delay=0, rot=0):
        k = ts - delay
        if k < 0: return
        sx, sy = squash(k, 0.28); s.paste(photo_img(name, wpx), c, sx * 0.94 + 0.06, sy * 0.94 + 0.06, min(1, k / 0.06), rot)
    def done(s): return s.im.resize((W, SH), Image.LANCZOS)

def wave(L_, y, amp, k, ph, col, w=12, x0=70, x1=1010, alpha=1.0, n=260, outline=True):
    xs = np.linspace(x0, x1, n); ys = y - amp * np.sin(k * (xs - x0) - ph); pts = list(zip(xs, ys))
    if outline: L_.line(pts, A(INK, alpha * 0.85), w + 10)
    L_.line(pts, A(col, alpha), w)

def magic_circle(L_, c, r, t, alpha=1.0, col=GOLD):
    L_.circ(c, r, outline=A(col, alpha), w=6); L_.circ(c, r * 0.84, outline=A(col, alpha * 0.7), w=3)
    for k in range(12):
        a = t * 0.6 + k * math.pi / 6; L_.circ((c[0] + r * 0.92 * math.cos(a), c[1] + r * 0.92 * math.sin(a)), 9, fill=A(col, alpha))
    for sgn, off in ((1, 0), (-1, math.pi / 3)):
        pts = [(c[0] + r * 0.84 * math.cos(sgn * t * 0.4 + off + j * 2 * math.pi / 3), c[1] + r * 0.84 * math.sin(sgn * t * 0.4 + off + j * 2 * math.pi / 3)) for j in range(4)]
        L_.line(pts, A(col, alpha * 0.6), 4)

def sparkles(L_, t, ts, n=6, cx=540, cy=540, rad=400):
    for i in range(n):
        a = i * 2 * math.pi / n + t * 0.6; r = rad + 30 * math.sin(t * 2 + i)
        L_.icon('2728', (cx + r * math.cos(a), cy + r * math.sin(a)), 100, ts, delay=0.04 * i, bob=False, alpha=0.55 + 0.45 * abs(math.sin(t * 3 + i)))

def kword(L_, txt, c, size, ts, col=YEL, delay=0, rot=0, stroke=10):
    k = ts - delay
    if k < 0: return
    sx, sy = squash(k, 0.25); f = F(size * S, 'Black'); d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    bb = d0.textbbox((0, 0), txt, font=f, stroke_width=stroke * S); w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=col, stroke_width=stroke * S, stroke_fill=INK)
    w2, h2 = int(w * sx), int(h * sy)
    if w2 < 2 or h2 < 2: return
    im = im.resize((w2, h2), Image.BICUBIC)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    L_.im.alpha_composite(im, (int(c[0] * S - im.width / 2), int(c[1] * S - im.height / 2)))

def stamp_img(text, size, col, rot):
    f = F(size, 'Black'); tmp = Image.new('RGBA', (1100, 400), (0, 0, 0, 0)); dd = ImageDraw.Draw(tmp); tw = dd.textlength(text, font=f)
    dd.rounded_rectangle([550 - tw / 2 - 50, 200 - size * 0.8, 550 + tw / 2 + 50, 200 + size * 0.8], 34, outline=col, width=16, fill=(25, 18, 50, 235))
    dd.text((550, 206), text, font=f, fill=col, anchor='mm'); return tmp.rotate(rot, resample=Image.BICUBIC)
def stamp(img, text, cx, cy, ts, size=160, col=YEL, rot=-8):
    if ts < 0: return
    p = min(1, ts / 0.16); sc = 1 + 1.2 * (1 - eout(p)); sy = sc * (1 - 0.18 * math.sin(min(1, ts / 0.3) * math.pi) * (ts > 0.16))
    s = stamp_img(text, size, col, rot).resize((int(1100 * sc), int(400 * sy)), Image.BICUBIC)
    img.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

GX, GY = np.meshgrid(np.linspace(-1, 1, 216), np.linspace(0, 1.6, 180))
SRC = [(-0.22, 0.05), (0.22, 0.05)]
R1 = np.hypot(GX - SRC[0][0], GY - SRC[0][1]); R2 = np.hypot(GX - SRC[1][0], GY - SRC[1][1])

# ---------- backgrounds ----------
rng = np.random.default_rng(3)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), rng.uniform(0, 6.28)) for _ in range(80)]
yy, xx = np.mgrid[0:H, 0:W]
dark = np.zeros((H, W, 3), np.float32); g = (yy / H)[..., None]
dark[:] = np.array([12, 8, 34]) * (1 - g) + np.array([34, 16, 64]) * g
rad = np.clip(1 - np.sqrt(((xx - 540) / 650) ** 2 + ((yy - 820) / 760) ** 2), 0, 1)[..., None] ** 2
DARK = Image.fromarray(np.clip(dark + np.array([120, 70, 220]) * 0.45 * rad, 0, 255).astype(np.uint8))
dots = ((xx % 36 < 3) & (yy % 36 < 3))[..., None]
_bgc = {}
def bright(col):
    if col not in _bgc:
        c = np.array(col, np.float32); a = c * (0.86 + 0.24 * rad) ; a = np.where(dots, a * 0.92, a)
        _bgc[col] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _bgc[col]

def background(t, kind):
    st = BG.get(kind, 'dark')
    if st == 'dark':
        img = DARK.copy(); d = ImageDraw.Draw(img)
        for x, y, r, ph in STARS:
            al = 0.5 + 0.5 * math.sin(t * 1.3 + ph); c = int(110 + 120 * al); y2 = (y - t * 22 * r) % H
            d.ellipse([x - r, y2 - r, x + r, y2 + r], fill=(c, c, min(255, c + 30)))
        return img
    return bright(st).copy()

def mana_level(t):
    if INS_AT <= t < INS_AT + INS_LEN:
        k = t - INS_AT
        if k < 1.2: return max(0.04, (1 - 0.8 * INS_AT / DUR) * (1 - ease(k / 1.2)))
        return 0.04 + 0.96 * eout((k - MC_REVEAL + INS_AT) / 0.35) if k >= MC_REVEAL - INS_AT else 0.04
    base_ = 1 - 0.8 * min(t, INS_AT) / DUR
    return 1.0 if t >= INS_AT + INS_LEN else base_

def hud(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, 120, 330, 186], 33, fill=INK)
    d.text((195, 153), "과학to마법", font=F(36), fill=GOLD, anchor='mm')
    x0, x1, y0, y1 = 560, 1010, 132, 176; lv = mana_level(t)
    d.rounded_rectangle([x0 - 92, y0 - 12, x1 + 10, y1 + 12], 34, fill=INK)
    d.text((x0 - 50, (y0 + y1) / 2 + 1), "MP", font=F(34), fill=MANA, anchor='mm')
    d.rounded_rectangle([x0, y0, x1, y1], 22, fill=(40, 40, 80))
    if lv > 0.01: d.rounded_rectangle([x0, y0, x0 + (x1 - x0) * lv, y1], 22, fill=MANA)
    d.rounded_rectangle([x0 + 8, y0 + 6, x0 + max(10, (x1 - x0) * lv) - 8, y0 + 16], 6, fill=(200, 230, 255))

# ---------- scenes ----------
def beat_at(t):
    bi = max(i for i, (s, _) in enumerate(BT) if t >= s - 1e-6); return bi, BT[bi][0], BT[bi][1]

def scene(t):
    bi, s0, kind = beat_at(t); ts = t - s0; Lr = L(); post = []; C = (540, 520)
    if kind == 'hook':
        sparkles(Lr, t, ts, 8, 540, 500, 440)
        Lr.photo('airpods', (540, 470), 860, ts, rot=-5)
        Lr.icon('1fa84', (880, 860), 220, ts, delay=0.35, t=t, rot=-15)
        kword(Lr, "마법 아이템?", (420, 900), 92, ts, delay=0.5, rot=4)
    elif kind == 'wizard':
        magic_circle(Lr, C, 430, t, ease(ts / 0.25)); sx, sy = squash(ts, 0.3)
        Lr.paste(char_img('cast'), (540, 600), 0.78 * sx, 0.78 * sy)
        kword(Lr, "4서클", (250, 110), 120, ts, delay=0.15, col=GOLD, rot=-6)
    elif kind == 'title':
        magic_circle(Lr, C, 430, t, 0.6); Lr.icon('1f507', (540, 420), 480, ts, t=t)
        kword(Lr, "SILENCE", (540, 870), 170, ts, col=GOLD, stroke=12)
    elif kind == 'mute':
        k = ease((ts - 0.8) / 0.2)
        Lr.icon('1f50a', (280, 520), 420, ts, t=t, alpha=1 - 0.7 * k)
        Lr.icon('1f449', (540, 520), 160, ts, delay=0.4, bob=False)
        Lr.icon('1f507', (810, 520), 420, ts, delay=0.8, t=t)
        if 0.8 < ts < 1.2: Lr.icon('1f4a5', (810, 520), 640, ts, delay=0.8, bob=False, alpha=1 - (ts - 0.8) / 0.4)
    elif kind == 'question':
        Lr.icon('1f9ea', (330, 540), 460, ts, t=t, rot=10); Lr.icon('1f914', (770, 470), 420, ts, delay=0.2, t=t)
        kword(Lr, "?", (790, 820), 260, ts, delay=0.35, col=WHITE, stroke=14)
    elif kind == 'verdict':
        st = STAMP_T[0] - t
        Lr.icon('1f9d9', (540, 470), 520, ts, t=t, alpha=1 if st > 0 else 0.3)
        post.append(lambda img: stamp(img, "일부 가능", 540, SY + 560, -st, size=180))
    elif kind == 'wave1':
        Lr.icon('1f62e', (170, 300), 280, ts, t=t)
        wave(Lr, 560, 190, 0.026, t * 9, NOISE, 16, 60, 1020, ease(ts / 0.25))
        kword(Lr, "소리 = 파동", (540, 900), 100, ts, delay=0.4, col=WHITE)
    elif kind == 'wave2':
        wave(Lr, 330, 160, 0.026, t * 9, NOISE, 15)
        a2 = ease((ts - 0.45) / 0.35)
        if a2 > 0: wave(Lr, 760, 160 * a2, 0.026, t * 9 + math.pi, ANTI, 15, alpha=a2)
        Lr.icon('1f504', (540, 545), 170, ts, delay=0.45, bob=False)
    elif kind == 'cancel':
        p = ease((ts - 0.25) / 0.8)
        wave(Lr, 200, 110 * (1 - 0.3 * p), 0.026, t * 9, NOISE, 12, alpha=1 - 0.5 * p)
        wave(Lr, 430, 110 * (1 - 0.3 * p), 0.026, t * 9 + math.pi, ANTI, 12, alpha=1 - 0.5 * p)
        xs = np.linspace(70, 1010, 260); ys = 640 - 110 * (1 - p) * np.sin(0.026 * (xs - 70) - t * 9)
        Lr.line(list(zip(xs, ys)), A(INK, 0.9), 26); Lr.line(list(zip(xs, ys)), A(WHITE, 1), 16)
        kword(Lr, "0", (540, 900), 300, ts, delay=0.95, col=YEL, stroke=16)
    elif kind == 'keyword':
        sparkles(Lr, t, ts, 6, 540, 520, 430)
        kword(Lr, "상쇄", (540, 410), 260, ts, col=WHITE, stroke=16, rot=-4)
        kword(Lr, "간섭", (540, 680), 260, ts, delay=0.12, col=WHITE, stroke=16, rot=3)
    elif kind == 'ear':
        Lr.circ(C, 300 + 24 * math.sin(t * 4), fill=A(WHITE, 0.35)); Lr.icon('1f442', C, 560, ts, t=t)
        sparkles(Lr, t, ts, 5, 540, 520, 380)
    elif kind == 'products':
        Lr.photo('airpods_case', (330, 430), 600, ts, rot=7)
        Lr.photo('buds', (790, 600), 430, ts, delay=0.3, rot=-8)
        kword(Lr, "노캔 이어폰!", (540, 990), 110, ts, delay=0.45, col=WHITE, rot=-3)
    elif kind == 'mic':
        Lr.icon('1f3a4', (740, 520), 430, ts, t=t, rot=-12)
        for i in range(4):
            r = ((t * 280 + i * 95) % 380); a = 1 - r / 380
            Lr.d.arc([(90 + r - 170) * S, 330 * S, (90 + r) * S, 710 * S], -55, 55, fill=A(INK, a * 0.8), width=22 * S)
            Lr.d.arc([(90 + r - 170) * S, 330 * S, (90 + r) * S, 710 * S], -55, 55, fill=A(NOISE, a), width=12 * S)
    elif kind == 'chip':
        Lr.icon('2699-fe0f', (260, 360), 360, ts, t=t); Lr.icon('26a1', (720, 340), 300, ts, delay=0.12, t=t)
        a = ease((ts - 0.2) / 0.3)
        if a > 0: wave(Lr, 800, 130, 0.03, t * 9 + math.pi, ANTI, 15, alpha=a)
    elif kind == 'ear_quiet':
        Lr.icon('1f442', (370, 520), 520, ts, t=t); Lr.icon('1f507', (800, 400), 320, ts, delay=0.25, t=t)
        Lr.icon('2728', (800, 720), 200, ts, delay=0.4, t=t)
    elif kind == 'itemcard':
        a = ease(ts / 0.2); y0 = 120 + 90 * (1 - eout(ts / 0.3))
        Lr.rrect([90, y0, 990, y0 + 820], 46, fill=A((24, 16, 56), 0.97 * a), outline=A(GOLD, a), w=8)
        kword(Lr, "★★★ 희귀", (540, y0 + 90), 80, ts, col=GOLD, stroke=6)
        if ts > 0.1: Lr.photo('airpods', (540, y0 + 400), 680, ts - 0.1)
        Lr.icon('1f507', (250, y0 + 720), 150, ts, delay=0.3, bob=False)
        kword(Lr, "사일런스 +1", (600, y0 + 720), 84, ts, delay=0.35, col=WHITE, stroke=6)
        sparkles(Lr, t, ts, 6, 540, y0 + 420, 500)
    elif kind == 'why':
        Lr.icon('1f914', C, 600, ts, t=t); kword(Lr, "일부?", (790, 230), 150, ts, delay=0.2, col=WHITE, rot=8)
    elif kind == 'ear_ok':
        Lr.icon('1f442', (380, 520), 500, ts, t=t); Lr.icon('2705', (800, 520), 340, ts, delay=0.25, t=t)
    elif kind == 'interference':
        a = ease(ts / 0.25)
        Iq = np.cos(22 * (R1 - R2) / 2) ** 2; v = Iq * (0.85 + 0.15 * np.sin(22 * (R1 + R2) / 2 - t * 9))
        col = np.stack([40 + 215 * v, 20 + 90 * v, 60 + 40 * (1 - v)], -1)
        m = Image.fromarray(col.clip(0, 255).astype(np.uint8)).resize((960 * S, 760 * S), Image.BICUBIC).convert('RGBA')
        mk = Image.new('L', m.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, m.width, m.height], 44 * S, fill=int(255 * a)); m.putalpha(mk)
        Lr.im.alpha_composite(m, (60 * S, 90 * S))
        for sx, sy in SRC: Lr.icon('1f50a', (540 + sx * 480, 90 + sy * 470), 130, ts, bob=False)
        Lr.icon('1f4e2', (540, 610), 190, ts, delay=1.0, bob=False); Lr.icon('1f507', (330, 760), 160, ts, delay=0.8, bob=False)
    elif kind == 'voice_wave':
        Lr.icon('1f62e', (180, 300), 290, ts, t=t)
        wave(Lr, 330, 100, 0.11, t * 14, NOISE, 10, 340, 1020, ease(ts / 0.25))
        Lr.icon('1f4cf', (260, 760), 260, ts, delay=0.5, t=t, rot=-20)
        kword(Lr, "~20cm", (680, 760), 150, ts, delay=0.6, col=WHITE)
    elif kind == 'fail':
        sh = 26 * math.sin(ts * 70) * max(0, 1 - ts / 0.5)
        Lr.icon('274c', (540 + sh, 500), 640, ts, bob=False)
    elif kind == 'engine':
        Lr.icon('2708-fe0f', (290, 330), 380, ts, t=t, rot=-8); Lr.icon('1f697', (780, 360), 340, ts, delay=0.15, t=t)
        a = ease((ts - 0.25) / 0.3)
        if a > 0: wave(Lr, 790, 170, 0.0062, t * 3, NOISE, 18, 50, 1030, a)
    elif kind == 'engine_ok':
        Lr.photo('bose', (540, 420), 800, ts, rot=-4)
        kword(Lr, "~3.4m", (420, 880), 160, ts, delay=0.25, col=WHITE); Lr.icon('2705', (850, 880), 230, ts, delay=0.4, t=t)
    elif kind == 'window':
        Lr.icon('1fa9f', (540, 500), 560, ts, t=t)
        for i, (x, y) in enumerate([(220, 230), (860, 230), (220, 770), (860, 770), (540, 140), (540, 880)]):
            Lr.icon('1f50a', (x, y), 140, ts, delay=0.5 + 0.07 * i, bob=False)
        Lr.icon('1f9ea', (930, 980), 170, ts, delay=1.3, t=t)
    elif kind == 'verdict2':
        magic_circle(Lr, C, 430, t, 0.5)
        post.append(lambda img: stamp(img, "판정", 540, SY + 520, ts, size=200, rot=0))
    elif kind == 'low_ok':
        Lr.icon('2708-fe0f', (250, 400), 320, ts, t=t); Lr.icon('1f697', (560, 420), 290, ts, delay=0.12, t=t); Lr.icon('2705', (860, 410), 260, ts, delay=0.25, t=t)
        kword(Lr, "저음 OK", (540, 820), 150, ts, delay=0.2, col=WHITE)
    elif kind == 'narrow_ok':
        Lr.photo('airpods_case', (320, 450), 500, ts, rot=6); Lr.photo('buds', (780, 500), 380, ts, delay=0.15, rot=-7)
        Lr.icon('2705', (540, 920), 260, ts, delay=0.35, t=t); sparkles(Lr, t, ts, 6, 540, 520, 460)
    elif kind == 'manacalc':
        Lr.icon('1f9ee', (190, 110), 170, ts, t=t)
        kword(Lr, "마나 계산기", (600, 110), 110, ts, delay=0.05, col=GOLD)
        kword(Lr, "사일런스 6시간 유지 = ?", (540, 270), 76, ts, delay=0.2, col=WHITE)
        OPTS = [("① 1원도 안 듦", 1), ("② 100원", 0), ("③ 1만 원", 0)]
        rev = ts >= 2.3
        for i, (o, ok) in enumerate(OPTS):
            k = ts - 0.4 - 0.15 * i
            if k < 0 or (rev and not ok): continue
            y = 420 + i * 125; a = 1.0 if not rev or ok else 0.35
            fillc = (40, 170, 100) if (rev and ok) else (255, 255, 255)
            sx, sy = squash(k, 0.22); w = 560 * sx
            Lr.rrect([540 - w / 2, y - 50 * sy, 540 + w / 2, y + 50 * sy], 50, fill=A(fillc, a), outline=A(INK, a), w=6)
            Lr.text((540, y), o, 58, A(WHITE if (rev and ok) else INK, a))
            if rev and ok: Lr.icon('2705', (870, y), 120, ts - 2.3, bob=False)
        if 1.8 <= ts < 2.3:
            k = ts - 1.8; val = 0.1 + 9999 * (1 - eout(min(1, k / 0.5)))
            Lr.d.text((540 * S, 820 * S), f"{val:,.1f}원", font=F(150 * S), fill=YEL, anchor='mm', stroke_width=14 * S, stroke_fill=INK)
        elif rev:
            kword(Lr, "0.1원", (430, 840), 190, ts - 2.3, col=YEL, stroke=16)
        pose = 'shock' if rev else 'smug_talk'
        sx, sy = squash(ts - (2.3 if rev else 0), 0.25)
        Lr.paste(char_img(pose), (880, 930), 0.42 * sx, 0.42 * sy)
        if ts > 3.0: post.append(lambda img: stamp(img, "마나 효율 갑", 470, SY + 1010, ts - 3.0, size=90, col=GOLD, rot=-6))
    elif kind == 'cta':
        a = ease(ts / 0.2)
        Lr.rrect([110, 30, 970, 560], 40, fill=A((24, 16, 56), 0.95 * a), outline=A(GOLD, a), w=6)
        kword(Lr, "오늘의 마법 재료", (540, 105), 64, ts, col=GOLD, stroke=5)
        if ts > 0.1: Lr.photo('airpods_case', (540, 355), 330, ts - 0.1, rot=3)
        sx, sy = squash(ts - 0.15, 0.3)
        if ts > 0.15: Lr.paste(char_img('earbud'), (300, 840), 0.44 * sx, 0.44 * sy)
        b = ease((ts - 0.7) / 0.2)
        Lr.rrect([660, 760, 960, 860], 50, fill=A((235, 40, 40), b)); Lr.text((810, 810), "구독", 60, A(WHITE, b))
    return Lr.done(), post, bi, s0, kind, ts

def draw_kinetic(img, t):
    cur = [p for p in PHR if p[0] - 0.02 <= t < p[1]]
    if not cur: return
    a, b, s = cur[-1]; k = t - a; sx, sy = squash(k, 0.18)
    f = F(112); d0 = ImageDraw.Draw(img); runs = []; i = 0
    while i < len(s):
        hit = next((h for h in KEY if s.startswith(h, i)), None)
        if hit: runs.append((hit, YEL)); i += len(hit)
        else:
            if runs and runs[-1][1] == WHITE: runs[-1] = (runs[-1][0] + s[i], WHITE)
            else: runs.append((s[i], WHITE))
            i += 1
    tw = sum(d0.textlength(r, font=f) for r, _ in runs) + 60; th = 190
    im = Image.new('RGBA', (int(tw), th), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 30
    for r, col in runs:
        d.text((x, th / 2), r, font=f, fill=col, anchor='lm', stroke_width=12, stroke_fill=INK); x += d.textlength(r, font=f)
    sc = min(1.0, 980 / tw)
    im = im.resize((max(2, int(tw * sc * sx)), max(2, int(th * sc * sy))), Image.BICUBIC)
    rot = [-3, 2, -1, 3][hash(s) % 4]; im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(im, (int(540 - im.width / 2), int(1470 - im.height / 2)))

def draw_pip(img, t, kind, ts):
    if kind not in PIP: return
    pose = PIP[kind]; k = ts
    if kind == 'verdict' and t >= STAMP_T[0]: pose, k = 'shock', t - STAMP_T[0]
    im = pip_img(pose); sx, sy = squash(k, 0.25) if k < 0.3 else (1, 1)
    if sx <= 0.05: return
    bob = 6 * math.sin(t * 2.5)
    im2 = im.resize((max(2, int(im.width * sx)), max(2, int(im.height * sy))), Image.BICUBIC)
    img.alpha_composite(im2, (int(PIP_C[0] - im2.width / 2), int(PIP_C[1] + bob - im2.height / 2)))

def bubble(img, text, x, y, k, tail='down', size=50):
    if k < 0: return
    sx, sy = squash(k, 0.2); f = F(size); d0 = ImageDraw.Draw(img)
    tw = d0.textlength(text, font=f); w, h = tw + 70, size + 50
    im = Image.new('RGBA', (int(w) + 40, int(h) + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 10, 20 + w, 10 + h], 34, fill=(255, 255, 255, 250), outline=INK, width=6)
    tx = {'down': 20 + w * 0.7, 'left': 40, 'right': w - 10}[tail]
    d.polygon([(tx - 16, 8 + h), (tx + 16, 8 + h), (tx + 4, 8 + h + 34)], fill=(255, 255, 255, 250), outline=INK)
    d.line([(tx - 16, 10 + h - 3), (tx + 16, 10 + h - 3)], fill=(255, 255, 255), width=8)
    d.text((20 + w / 2, 10 + h / 2 + 2), text, font=f, fill=INK, anchor='mm')
    im = im.resize((max(2, int(im.width * sx)), max(2, int(im.height * sy))), Image.BICUBIC)
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

def _bt(kind): return next(a for a, k in BT if k == kind)
BUBBLES = [(_bt('wizard') + 0.15, 1.0, "조용히 해, 평민들!", 600, SY + 190, 'down'),
           (STAMP_T[0] + 0.25, 1.4, "…일부?", 760, 545, 'right'),
           (_bt('itemcard') + 0.35, 2.0, "내 마법이 이어폰이라고?!", 640, 545, 'right'),
           (_bt('fail') + 0.1, 1.2, "오호호호!", 760, 545, 'right'),
           (INS_AT + 0.6, 1.15, "당연히 1만 원이겠지?", 640, SY + 800, 'down'),
           (INS_AT + 2.45, 1.7, "내 4서클이… 0.1원?!", 640, SY + 570, 'down'),
           (_bt('cta') + 0.5, 3.0, "흥, 인정해 주지.", 700, SY + 720, 'left')]
def draw_bubbles(img, t):
    for st, dur, txt, x, y, tail in BUBBLES:
        if st <= t < st + dur: bubble(img, txt, x, y, t - st, tail)

def frame(t):
    sc, post, bi, s0, kind, ts = scene(t)
    img = background(t, kind).convert('RGBA')
    # whip-in on alternate cuts, punch zoom on others
    if t > 0.1 and ts < 0.16 and bi % 2 == 1:
        dx = int(420 * (1 - eout(ts / 0.16))); bl = sc.filter(ImageFilter.BoxBlur(int(14 * (1 - ts / 0.16)) + 1))
        img.alpha_composite(bl, (dx, SY))
    else:
        z = 1 + 0.12 * (1 - eout(ts / 0.2)) if t > 0.1 else 1
        if z > 1.001:
            w, h = int(W * z), int(SH * z); sc = sc.resize((w, h), Image.BICUBIC).crop(((w - W) // 2, (h - SH) // 2, (w - W) // 2 + W, (h - SH) // 2 + SH))
        img.alpha_composite(sc, (0, SY))
    for p in post: p(img)
    hud(img, t); draw_pip(img, t, kind, ts); draw_bubbles(img, t); draw_kinetic(img, t)
    # impact shake on stamps
    sh = 0
    for st in STAMP_T + [INS_AT + 3.0]:
        if 0 <= t - st < 0.3: sh = 16 * math.sin((t - st) * 80) * (1 - (t - st) / 0.3)
    if sh: img = img.transform(img.size, Image.AFFINE, (1, 0, sh, 0, 1, sh * 0.6), resample=Image.BILINEAR)
    if t > 0.1 and ts < 0.06 and bi % 2 == 0:
        img = Image.blend(img, Image.new('RGBA', img.size, (255, 255, 255, 255)), 0.4 * (1 - ts / 0.06))
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'v4_{tt}.png')
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'info':
        print(round(DUR, 2), round(INS_AT, 2)); print([(round(a, 2), k) for a, k in BT]); sys.exit()
    n = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', 'video4.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0: print(i, n, flush=True)
    p.stdin.close(); p.wait()
    json.dump({'cuts': [a for a, _ in BT[1:]], 'stamp': STAMP_T + [INS_AT + 3.0], 'chime': [o2t(47.29), 0.05], 'ins': INS_AT, 'ins_len': INS_LEN,
               'roll': [INS_AT + 1.8, INS_AT + 2.3], 'dur': DUR, 'tempo': T}, open('sfx4.json', 'w'))
    with open('EP_사일런스.srt', 'w') as f:
        def tsf(x): return f"{int(x//3600):02}:{int(x%3600//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        for k, (a, b, c) in enumerate(CHUNKS, 1): f.write(f"{k}\n{tsf(a)} --> {tsf(b)}\n{c}\n\n")
    print('done')
