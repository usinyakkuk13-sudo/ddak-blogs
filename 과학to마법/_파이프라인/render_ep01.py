import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, TEMPO = 1080, 1920, 30, 1.1
FD = 'fonts/public/static/'
_fc = {}
def F(size, w='Bold'):
    k = (size, w)
    if k not in _fc: _fc[k] = ImageFont.truetype(f'{FD}Pretendard-{w}.otf', size)
    return _fc[k]

GOLD = (255, 205, 80); WHITE = (245, 245, 255); BLUE = (80, 190, 255); RED = (255, 90, 90)
YEL = (255, 220, 70); GREEN = (90, 220, 140); DIM = (150, 150, 190); BG1 = (8, 8, 24); BG2 = (22, 18, 52)

SUBS = [
 "판타지 4서클 마법, 사일런스.", "주변의 소리를 완전히 지워버리는 마법이죠.",
 "현대 과학으로 가능할까요?", "판정.", "일부 가능.",
 "소리는 공기가 밀렸다 당겨지는 파동입니다.", "여기에 똑같은 모양을 정반대로 뒤집은 파동을 겹치면",
 "둘이 서로를 지워서 0이 됩니다.", "이걸 상쇄 간섭이라고 해요.",
 "사실 여러분 귀에 이미 이 마법이 걸려 있습니다. 네, 바로 노이즈캔슬링 이어폰이요. 바깥 소리를 마이크로 듣고 정반대 소리를 순식간에 만들어 귀 안에서 지우는 거죠.",
 "사일런스 인챈트가 걸린 마법 아이템인 셈입니다.",
 "그런데 왜 일부만 가능할까요?", "귀처럼 좁은 곳은 쉽지만", "넓은 공간에서는 한 곳에서 지운 소리가 다른 곳에선 오히려 커집니다.",
 "게다가", "목소리처럼 높은 소리는 파장이 수십 센티미터도 안 돼서", "조금만 어긋나도 실패해요.",
 "반면 엔진 같은 낮은 소리는 파장이 몇 미터라 훨씬 쉽습니다.",
 "그래서 실제로 창문에 작은 스피커를 여러 개 달아 바깥 소음을 줄이는 연구까지 나와 있어요.",
 "결론.", "사일런스는 저음 한정,", "좁은 공간 한정으로 이미 현실입니다.",
 "지금 귀에 꽂고 있는 그게 바로 그 마법 아이템이에요.",
 "다음엔 어떤 마법을 판정해 볼까요? 댓글로 주문을 걸어주세요."]
HL = ["상쇄 간섭", "일부 가능", "노이즈캔슬링", "사일런스", "저음", "좁은 공간", "마법 아이템", "파장", "0이", "정반대"]

raw = json.load(open('tl_raw.json'))
DUR = raw['dur'] / TEMPO
SEG = [dict(s, s=s['s'] / TEMPO, e=s['e'] / TEMPO) for s in raw['tl']]
LINES = {}
for s in SEG: LINES.setdefault(s['line'], []).append(s)
LSTART = {l: v[0]['s'] for l, v in LINES.items()}
def line_at(t):
    cur = 1
    for l in sorted(LSTART):
        if t >= LSTART[l] - 0.15: cur = l
    return cur

# ---------- subtitles: chunk segments ----------
def chunks(text, maxc=26):
    words = text.split(' '); out = []; cur = ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > maxc: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    if cur: out.append(cur)
    return out
SUBT = []
for s, txt in zip(SEG, SUBS):
    cs = chunks(txt); tot = sum(len(c) for c in cs); t0 = s['s']
    for c in cs:
        d = (s['e'] - s['s']) * len(c) / tot
        SUBT.append((t0, t0 + d, c)); t0 += d

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def seg(i): return SEG[i]['s'], SEG[i]['e']

# ---------- drawing helpers ----------
def text_c(d, xy, s, f, fill, stroke=0, sfill=(0, 0, 0), anchor='mm'):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

def draw_sub(img, t):
    cur = [c for a, b, c in SUBT if a - 0.05 <= t < b + 0.05]
    if not cur: return
    s = cur[-1]; f = F(64, 'Bold'); d = ImageDraw.Draw(img)
    lines = [s]
    if d.textlength(s, font=f) > 900 and ' ' in s:
        sp = [i for i, ch in enumerate(s) if ch == ' ']; mid = min(sp, key=lambda i: abs(i - len(s) / 2))
        lines = [s[:mid], s[mid + 1:]]
    y0 = 1430 - (len(lines) - 1) * 42
    for k, ln in enumerate(lines):
        # runs with highlight
        runs = []; i = 0
        while i < len(ln):
            hit = next((h for h in HL if ln.startswith(h, i)), None)
            if hit: runs.append((hit, YEL)); i += len(hit)
            else:
                if runs and runs[-1][1] == WHITE: runs[-1] = (runs[-1][0] + ln[i], WHITE)
                else: runs.append((ln[i], WHITE))
                i += 1
        tw = sum(d.textlength(r, font=f) for r, _ in runs); x = 540 - tw / 2; y = y0 + k * 84
        for r, col in runs:
            d.text((x, y), r, font=f, fill=col, anchor='lm', stroke_width=7, stroke_fill=(0, 0, 0))
            x += d.textlength(r, font=f)

rng = np.random.default_rng(3)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), rng.uniform(0, 6.28)) for _ in range(90)]
BASE = Image.new('RGB', (W, H))
g = np.linspace(0, 1, H)[:, None]
arr = (np.array(BG1)[None, None, :] * (1 - g[..., None]) + np.array(BG2)[None, None, :] * g[..., None])
BASE = Image.fromarray(np.repeat(arr, W, axis=1).astype(np.uint8))

def background(t):
    img = BASE.copy(); d = ImageDraw.Draw(img)
    for x, y, r, ph in STARS:
        a = 0.5 + 0.5 * math.sin(t * 1.3 + ph); c = int(90 + 120 * a)
        y2 = (y - t * 8 * r) % H
        d.ellipse([x - r, y2 - r, x + r, y2 + r], fill=(c, c, min(255, c + 40)))
    # header
    text_c(d, (540, 150), "과학 to 마법", F(40, 'SemiBold'), GOLD)
    text_c(d, (540, 222), "4서클 · 사일런스", F(72, 'Black'), WHITE, 4)
    d.rounded_rectangle([880, 120, 1010, 172], 26, outline=GOLD, width=3)
    text_c(d, (945, 146), "EP.01", F(30, 'Bold'), GOLD)
    return img

# scene layer: supersampled 2x, local coords 0..1080 x 0..900, pasted at y=380
SY, SH, S = 380, 900, 2
class L:
    def __init__(s): s.im = Image.new('RGBA', (W * S, SH * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def line(s, pts, fill, w): s.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint='curve')
    def circ(s, c, r, outline=None, fill=None, w=3):
        x, y = c; s.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=outline, fill=fill, width=int(w * S))
    def rrect(s, b, r, outline=None, fill=None, w=3):
        s.d.rounded_rectangle([v * S for v in b], r * S, outline=outline, fill=fill, width=int(w * S))
    def text(s, xy, txt, size, fill, wt='Bold', stroke=0, anchor='mm'):
        s.d.text((xy[0] * S, xy[1] * S), txt, font=F(size * S, wt), fill=fill, anchor=anchor, stroke_width=stroke * S, stroke_fill=(0, 0, 0))
    def done(s): return s.im.resize((W, SH), Image.LANCZOS)

def A(c, a): return tuple(c[:3]) + (int(255 * max(0, min(1, a))),)
def wave(L_, y, amp, k, ph, col, w=7, x0=90, x1=990, alpha=1.0, n=220):
    xs = np.linspace(x0, x1, n); ys = y - amp * np.sin(k * (xs - x0) - ph)
    L_.line(list(zip(xs, ys)), A(col, alpha), w)

def magic_circle(L_, c, r, t, alpha=1.0):
    L_.circ(c, r, outline=A(GOLD, alpha), w=4); L_.circ(c, r * 0.84, outline=A(GOLD, alpha * 0.7), w=2)
    for k in range(12):
        a = t * 0.4 + k * math.pi / 6; x = c[0] + r * 0.92 * math.cos(a); y = c[1] + r * 0.92 * math.sin(a)
        L_.circ((x, y), 7, fill=A(GOLD, alpha))
    for sgn, off in ((1, 0), (-1, math.pi / 3)):
        pts = [(c[0] + r * 0.84 * math.cos(sgn * t * 0.25 + off + j * 2 * math.pi / 3), c[1] + r * 0.84 * math.sin(sgn * t * 0.25 + off + j * 2 * math.pi / 3)) for j in range(4)]
        L_.line(pts, A(GOLD, alpha * 0.6), 3)

def stamp(img, text, cx, cy, t_since, size=120, col=YEL, rot=-8):
    if t_since < 0: return
    sc = 1 + 0.7 * (1 - ease(t_since / 0.22))
    f = F(size, 'Black'); tmp = Image.new('RGBA', (900, 320), (0, 0, 0, 0)); dd = ImageDraw.Draw(tmp)
    tw = dd.textlength(text, font=f)
    dd.rounded_rectangle([450 - tw / 2 - 40, 160 - size * 0.75, 450 + tw / 2 + 40, 160 + size * 0.75], 28, outline=col, width=12)
    dd.text((450, 165), text, font=f, fill=col, anchor='mm')
    tmp = tmp.rotate(rot, resample=Image.BICUBIC, expand=False)
    tmp = tmp.resize((int(900 * sc), int(320 * sc)), Image.BICUBIC)
    img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))

def item_card(L_, t_since, title, rows, y=470, alpha_mul=1):
    if t_since < 0: return
    p = ease(t_since / 0.4); yy = y + (1 - p) * 120; a = p * alpha_mul
    L_.rrect([140, yy, 940, yy + 330], 26, outline=A(GOLD, a), fill=(14, 12, 40, int(235 * a)), w=5)
    L_.text((540, yy + 58), title, 52, A(GOLD, a), 'Black')
    L_.line([(190, yy + 102), (890, yy + 102)], A(GOLD, a * 0.5), 2)
    for k, (lab, val) in enumerate(rows):
        L_.text((200, yy + 155 + k * 62), lab, 38, A(DIM, a), 'SemiBold', anchor='lm')
        L_.text((400, yy + 155 + k * 62), val, 40, A(WHITE, a), 'Bold', anchor='lm')

# interference map precompute grid
GX, GY = np.meshgrid(np.linspace(-1, 1, 216), np.linspace(0, 1.6, 180))
SRC = [(-0.22, 0.05), (0.22, 0.05)]
R1 = np.hypot(GX - SRC[0][0], GY - SRC[0][1]); R2 = np.hypot(GX - SRC[1][0], GY - SRC[1][1])

def scene(t):
    lyr = L(); ln = line_at(t); post = []  # post: functions drawing on full img after paste
    if ln == 1:
        lt = t - LSTART[1]; a = ease(lt / 0.4)
        magic_circle(lyr, (540, 380), 300, t, a)
        amp = 110 * (1 - ease((t - seg(1)[0]) / (seg(1)[1] - seg(1)[0])))
        wave(lyr, 380, max(amp, 0), 0.035, t * 8, BLUE, 8, 300, 780, a)
        lyr.text((540, 790), "SILENCE", 110, A(GOLD, a), 'Black')
    elif ln == 2:
        s2, _ = seg(2); s4, _ = seg(4)
        magic_circle(lyr, (540, 420), 260, t, 0.35)
        lyr.text((540, 200), "현대 과학으로", 70, A(WHITE, ease((t - s2) / 0.3)), 'Black')
        lyr.text((540, 290), "가능할까?", 70, A(WHITE, ease((t - s2) / 0.3)), 'Black')
        if t < s4: lyr.text((540, 520), "판정" + "." * (1 + int(t * 3) % 3), 80, A(DIM, 1), 'Black')
        post.append(lambda img: stamp(img, "일부 가능", 540, SY + 540, t - s4))
    elif ln in (3, 4):
        s6, _ = seg(6); s7, _ = seg(7); s8, _ = seg(8)
        k, ph = 0.03, t * 6
        if ln == 3:
            lyr.text((90, 140), "소리 = 공기의 압력 파동", 46, A(WHITE, 1), 'Bold', anchor='lm')
            wave(lyr, 330, 110, k, ph, BLUE, 8)
            a2 = ease((t - s6) / 0.5)
            lyr.text((90, 520), "정반대로 뒤집은 파동", 46, A(RED, a2), 'Bold', anchor='lm')
            wave(lyr, 690, 110 * a2, k, ph + math.pi, RED, 8, alpha=a2)
        else:
            p = ease((t - s7) / 1.4)
            wave(lyr, 150, 75, k, ph, BLUE, 6); lyr.text((60, 150), "+", 60, A(WHITE, 1), 'Black')
            wave(lyr, 340, 75, k, ph + math.pi, RED, 6); lyr.text((60, 450), "=", 60, A(WHITE, 1), 'Black')
            xs = np.linspace(90, 990, 220); ys = 560 - 75 * (1 - p) * np.sin(k * (xs - 90) - ph)
            lyr.line(list(zip(xs, ys)), A(YEL, 1), 9)
            lyr.text((990, 640), "0", 70, A(YEL, p), 'Black', anchor='rm')
            a3 = ease((t - s8) / 0.3)
            lyr.text((540, 800), "상쇄 간섭", 120, A(YEL, a3), 'Black', stroke=0)
    elif ln == 5:
        s9, e9 = seg(9); s10, _ = seg(10); fr = (t - s9) / (e9 - s9)
        steps = [(150, "바깥 소리", BLUE), (380, "마이크", WHITE), (620, "칩: 반대 소리\n계산", GOLD), (870, "스피커", RED)]
        lyr.text((540, 70), "노이즈캔슬링 이어폰 속 마법", 52, A(WHITE, 1), 'Black')
        for i, (x, lab, col) in enumerate(steps):
            a = ease((fr - (0.28 + i * 0.12)) / 0.08) if i else ease(fr / 0.1)
            if i == 0: wave(lyr, 330, 50, 0.08, t * 8, BLUE, 6, 70, 230, a)
            elif i == 2: lyr.rrect([x - 120, 260, x + 120, 400], 22, outline=A(col, a), w=5)
            else: lyr.circ((x, 330), 62, outline=A(col, a), w=5)
            lyr.d.multiline_text((x * S, 470 * S), lab, font=F(38 * S, 'Bold'), fill=A(col, a), anchor='mm', align='center', spacing=10)
            if i: lyr.line([(steps[i - 1][0] + 75 + (20 if i == 3 else 0), 330), (x - (130 if i == 2 else 72), 330)], A(DIM, a), 4)
        a4 = ease((fr - 0.72) / 0.1)
        wave(lyr, 650, 55, 0.035, t * 7, BLUE, 5, 120, 560, a4 * 0.9)
        wave(lyr, 650, 55, 0.035, t * 7 + math.pi, RED, 5, 120, 560, a4 * 0.9)
        lyr.line([(640, 650), (960, 650)], A(YEL, a4), 8); lyr.text((800, 600), "귀 안 = 조용", 40, A(YEL, a4), 'Bold')
        item_card(lyr, t - s10, "노이즈캔슬링 이어폰", [("등급", "★★★ 희귀"), ("효과", "사일런스 (저음) +1"), ("착용", "귀")], y=520)
    elif ln == 6:
        s12, _ = seg(12); s13, _ = seg(13)
        lyr.text((540, 70), "왜 '일부'만 가능할까?", 56, A(WHITE, 1), 'Black')
        if t < s13 + 0.4:
            a = ease((t - s12) / 0.3) * (1 - ease((t - s13) / 0.4))
            lyr.circ((540, 420), 150, outline=A(WHITE, a), w=5)
            lyr.circ((700, 420), 46, fill=A(GREEN, a * 0.35), outline=A(GREEN, a), w=5)
            lyr.text((540, 650), "귀처럼 좁은 곳 = 쉬움", 54, A(GREEN, a), 'Black')
        if t > s13:
            a = ease((t - s13 - 0.2) / 0.4)
            Iq = np.cos(22 * (R1 - R2) / 2) ** 2  # time-avg intensity pattern
            pulse = 0.85 + 0.15 * np.sin(22 * (R1 + R2) / 2 - t * 8)
            v = (Iq * pulse); col = np.stack([40 + 215 * v, 30 + 150 * v, 70 + 30 * v], -1)
            m = Image.fromarray(col.clip(0, 255).astype(np.uint8)).resize((900 * S, 600 * S), Image.BICUBIC).convert('RGBA')
            m.putalpha(int(255 * a)); lyr.im.alpha_composite(m, (90 * S, 150 * S))
            for sx, sy in SRC: lyr.circ((540 + sx * 450, 150 + sy * 375), 16, fill=A(WHITE, a))
            lyr.text((540, 820), "밝은 줄 = 더 시끄러움 · 어두운 줄 = 조용", 40, A(WHITE, a), 'Bold')
    elif ln == 7:
        s15, _ = seg(15); s16, _ = seg(16); s17, _ = seg(17)
        lyr.text((540, 70), "1미터 안에 들어가는 파동", 54, A(WHITE, 1), 'Black')
        rows = [(250, "목소리 3kHz", "≈ 11cm", 9 * 2 * math.pi / 900, s15, BLUE), (450, "목소리 1kHz", "≈ 34cm", 3 * 2 * math.pi / 900, s15 + 0.5, BLUE), (650, "엔진 100Hz", "≈ 3.4m", 0.3 * 2 * math.pi / 900, s17, GREEN)]
        for y, lab, wl, k, st, col in rows:
            a = ease((t - st) / 0.4)
            lyr.text((90, y - 85), lab, 42, A(col, a), 'Bold', anchor='lm'); lyr.text((990, y - 85), "파장 " + wl, 42, A(col, a), 'Bold', anchor='rm')
            wave(lyr, y, 45, k, t * 5 if col == BLUE else t * 1.5, col, 6, alpha=a)
        a = ease((t - s16) / 0.3) * (1 - ease((t - s17) / 0.3))
        lyr.rrect([250, 740, 830, 830], 20, fill=(60, 10, 20, int(220 * a)), outline=A(RED, a), w=4)
        lyr.text((540, 785), "조금만 어긋나도 실패 ✕", 44, A(RED, a), 'Black')
        a = ease((t - s17 - 0.6) / 0.4)
        lyr.rrect([250, 740, 830, 830], 20, fill=(10, 50, 30, int(220 * a)), outline=A(GREEN, a), w=4)
        lyr.text((540, 785), "길어서 맞추기 쉬움", 44, A(GREEN, a), 'Black')
        lyr.line([(90, 860), (990, 860)], A(DIM, 1), 3); lyr.text((540, 885), "← 1m →", 30, A(DIM, 1), 'SemiBold')
    elif ln == 8:
        lyr.text((540, 70), "연구 중: 소음 지우는 창문", 54, A(WHITE, 1), 'Black')
        bx = [400, 180, 680, 700]
        for k in range(6):
            r = ((t * 120 + k * 70) % 420)
            x = 60 + r * 0.8
            if x < 395: lyr.d.arc([(x - 140) * S, 300 * S, (x) * S, 580 * S], -60, 60, fill=A(BLUE, 0.9), width=6 * S)
            xo = 705 + ((t * 120 + k * 70) % 300)
            if xo < 1000: lyr.d.arc([(xo - 140) * S, 340 * S, xo * S, 540 * S], -60, 60, fill=A(BLUE, 0.25), width=4 * S)
        lyr.rrect(bx, 10, outline=A(WHITE, 1), w=8)
        lyr.line([(540, 180), (540, 700)], A(WHITE, 0.6), 4); lyr.line([(400, 440), (680, 440)], A(WHITE, 0.6), 4)
        for k in range(6):
            for x in (400, 680):
                y = 220 + k * 92; lyr.circ((x, y), 15, fill=A(GOLD, 1))
        lyr.text((180, 760), "바깥 소음", 40, A(BLUE, 1), 'Bold'); lyr.text((860, 760), "줄어든 소음", 40, A(DIM, 1), 'Bold')
        lyr.text((540, 830), "● 작은 스피커 여러 개", 38, A(GOLD, 1), 'Bold')
    elif ln == 9:
        s19, _ = seg(19); s20, _ = seg(20); s21, _ = seg(21); s22, _ = seg(22)
        a = ease((t - s20) / 0.3)
        lyr.rrect([110, 170, 970, 330], 26, fill=(10, 50, 30, int(230 * a)), outline=A(GREEN, a), w=5)
        lyr.text((170, 250), "O", 70, A(GREEN, a), 'Black'); lyr.text((240, 220), "저음 · 좁은 공간", 50, A(WHITE, a), 'Black', anchor='lm')
        lyr.text((240, 285), "→ 이미 현실", 40, A(GREEN, a), 'Bold', anchor='lm')
        a = ease((t - s21) / 0.3)
        lyr.rrect([110, 370, 970, 530], 26, fill=(60, 10, 20, int(230 * a)), outline=A(RED, a), w=5)
        lyr.text((170, 450), "X", 70, A(RED, a), 'Black'); lyr.text((240, 420), "넓은 공간 · 목소리", 50, A(WHITE, a), 'Black', anchor='lm')
        lyr.text((240, 485), "→ 아직 연구 단계", 40, A(RED, a), 'Bold', anchor='lm')
        a = ease((t - s22) / 0.4)
        lyr.text((540, 640), "그 마법 아이템 =", 50, A(WHITE, a), 'Bold'); lyr.text((540, 730), "노캔 이어폰", 92, A(GOLD, a), 'Black')
        post.append(lambda img: stamp(img, "판정: 일부 가능", 540, SY + 75, t - s19, size=64, rot=0))
    else:
        lt = t - LSTART[10]; a = ease(lt / 0.4)
        magic_circle(lyr, (540, 380), 280, t, a * 0.3)
        lyr.text((540, 330), "다음 마법은?", 110, A(WHITE, a), 'Black', stroke=3)
        lyr.text((540, 470), "댓글로 주문을 걸어주세요", 50, A(GOLD, a), 'Bold')
        lyr.rrect([380, 720, 700, 820], 50, fill=(230, 40, 40, int(255 * a)))
        lyr.text((540, 770), "구독", 56, A(WHITE, a), 'Black')
    return lyr.done(), post

def frame(t):
    img = background(t).convert('RGBA')
    sc, post = scene(t)
    img.alpha_composite(sc, (0, SY))
    for p in post: p(img)
    draw_sub(img, t)
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'still_{tt}.png')
        sys.exit()
    n = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', 'video.mp4'], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0: print(i, n, flush=True)
    p.stdin.close(); p.wait()
    # sfx times
    json.dump({'stamp': [seg(4)[0], seg(19)[0]], 'chime': [seg(10)[0], seg(22)[0]], 'dur': DUR}, open('sfx.json', 'w'))
    with open('ep01.srt', 'w') as f:
        def ts(x): return f"{int(x//3600):02}:{int(x%3600//60):02}:{int(x%60):02},{int((x%1)*1000):03}"
        for k, (a, b, c) in enumerate(SUBT, 1): f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{c}\n\n")
    print('done')
