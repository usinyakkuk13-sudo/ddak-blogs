"""문명 이기 지수 샘플 #1 — 휴대폰 (무음 내레이션 · 자막 주도)"""
import math, json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render4 as R
W, H, FPS, S, SY, SH = R.W, R.H, R.FPS, R.S, R.SY, R.SH
INK, WHITE, YEL, GOLD = R.INK, R.WHITE, R.YEL, R.GOLD
ease, eout, squash, A, F, kword, stamp = R.ease, R.eout, R.squash, R.A, R.F, R.kword, R.stamp
CH = '/home/claude/assets/char/'

# (beat, duration, caption, bg)
SEP = (214, 178, 128); SEP2 = (196, 150, 98)
BEATS = [('hook', 2.8, "지금 손에 든 그거, 1983년엔 얼마였을까?", 'dark'),
         ('intro', 2.6, "세계 최초 휴대폰, 다이나택", SEP),
         ('brick', 3.0, "무게 약 800g, 일명 벽돌폰", SEP2),
         ('specs', 3.0, "충전 10시간, 통화는 30분", SEP),
         ('price', 2.4, "가격은 3,995달러", SEP2),
         ('quiz', 3.8, "지금 돈으로 얼마일까?", 'dark'),
         ('reveal', 3.2, "정답 ③ 약 1,800만 원, 경차 한 대 값!", 'dark'),
         ('but', 2.4, "근데 이건 '전화'만 되는 물건", (255, 120, 90)),
         ('replace', 4.4, "스마트폰은 카메라·캠코더·계산기·녹음기까지 다 삼켰죠", (77, 150, 255)),
         ('replace_price', 3.2, "1991년 전단지 기준, 지금 돈 약 1,000만 원어치", (46, 196, 182)),
         ('sum', 3.2, "합치면 2,800만 원어치를 40만 원대 폰 하나로", (120, 220, 170)),
         ('score', 3.6, "문명 이기 점수 70배!", 'dark'),
         ('cta', 3.4, "다음 감정 물건은 댓글로!", 'dark')]
BT = []; t0 = 0.0
for k, d, c, bg in BEATS: BT.append((t0, k, d, c, bg)); t0 += d
DUR = t0
KEY = ["1983년", "다이나택", "벽돌폰", "800g", "10시간", "30분", "3,995달러", "1,800만 원", "③", "'전화'", "1,000만 원어치", "2,800만 원어치", "40만 원대", "70배!", "댓글로!"]
PHR = []
for s0, k, d, c, bg in BT:
    ws = c.split(' '); groups = []; cur = ''
    for w in ws:
        if cur and len((cur + w).replace(' ', '')) > 8: groups.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    groups.append(cur); tot = sum(len(g.replace(' ', '')) for g in groups); a = s0 + 0.1
    for g in groups:
        dd = (d - 0.15) * len(g.replace(' ', '')) / tot; PHR.append((a, a + dd, g)); a += dd
def bt(kind): return next(b for b in BT if b[1] == kind)[0]
REVEAL = bt('reveal'); SCORE_T = bt('score') + 0.5

_ap = {}
def ap(pose):
    if pose not in _ap: _ap[pose] = Image.open(CH + f'ap_{pose}.png').convert('RGBA')
    return _ap[pose]
_pip = {}
def pip_img(pose, d=230):
    if pose not in _pip:
        im = ap(pose).crop((150, 230, 750, 830)).resize((d, d), Image.LANCZOS)
        m = Image.new('L', (d, d), 0); ImageDraw.Draw(m).ellipse([0, 0, d - 1, d - 1], fill=255)
        bg = Image.new('RGBA', (d, d), (60, 120, 190, 255)); bg.alpha_composite(im); bg.putalpha(m)
        out = Image.new('RGBA', (d + 18, d + 18), (0, 0, 0, 0)); ImageDraw.Draw(out).ellipse([0, 0, d + 17, d + 17], fill=GOLD + (255,))
        out.alpha_composite(bg, (9, 9)); _pip[pose] = out
    return _pip[pose]
PIP = {'hook': 'loupe', 'brick': 'laugh', 'specs': 'talk', 'price': 'loupe', 'but': 'loupe', 'replace': 'talk',
       'replace_price': 'shock'}

yy, xx = np.mgrid[0:H, 0:W]; g = (yy / H)[..., None]
rad = np.clip(1 - np.sqrt(((xx - 540) / 650) ** 2 + ((yy - 820) / 760) ** 2), 0, 1)[..., None] ** 2
DARKC = Image.fromarray(np.clip(np.array([20, 24, 40]) * (1 - g) + np.array([40, 30, 26]) * g + np.array([200, 150, 70]) * 0.35 * rad, 0, 255).astype(np.uint8))
def background(bg):
    return DARKC.copy() if bg == 'dark' else R.bright(bg).copy()

def gauge(t):  # 문명 지수 바: 0 → 1,800만(0.64) → 2,800만(1.0)
    if t < REVEAL: return 0.0
    if t < bt('replace_price'): return 0.64 * eout((t - REVEAL - 0.4) / 0.5)
    if t < bt('sum'): return 0.64 + 0.36 * eout((t - bt('replace_price') - 0.3) / 0.6)
    return 1.0
def hud(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, 120, 350, 186], 33, fill=INK); d.text((205, 153), "문명 감정소", font=F(36), fill=GOLD, anchor='mm')
    x0, x1, y0, y1 = 590, 1010, 132, 176; lv = gauge(t)
    d.rounded_rectangle([x0 - 120, y0 - 12, x1 + 10, y1 + 12], 34, fill=INK)
    d.text((x0 - 62, (y0 + y1) / 2 + 1), "문명", font=F(32), fill=GOLD, anchor='mm')
    d.rounded_rectangle([x0, y0, x1, y1], 22, fill=(60, 50, 40))
    if lv > 0.01: d.rounded_rectangle([x0, y0, x0 + (x1 - x0) * lv, y1], 22, fill=GOLD)

def scene(t):
    i = max(j for j, b in enumerate(BT) if t >= b[0] - 1e-6); s0, kind, dur, cap, bg = BT[i]; ts = t - s0
    Lr = R.L(); post = []
    if kind == 'hook':
        Lr.photo('brick_vs_smart', (540, 470), 900, ts, rot=-3)
        Lr.icon('2753', (900, 900), 200, ts, delay=0.5, t=t)
    elif kind == 'intro':
        sx, sy = squash(ts, 0.3); Lr.paste(ap('loupe'), (420, 600), 0.72 * sx, 0.72 * sy)
        Lr.photo('brick', (840, 470), 260, ts, delay=0.3, rot=8)
        kword(Lr, "1983", (840, 860), 150, ts, delay=0.1, col=WHITE, rot=-4)
    elif kind == 'brick':
        Lr.photo('brick', (330, 520), 330, ts, rot=-6); Lr.icon('1f9f1', (780, 380), 300, ts, delay=0.25, t=t)
        kword(Lr, "약 800g", (780, 700), 150, ts, delay=0.4, col=WHITE)
    elif kind == 'specs':
        Lr.icon('1f50b', (290, 400), 330, ts, t=t); kword(Lr, "10시간", (290, 720), 130, ts, delay=0.2, col=WHITE)
        Lr.icon('1f4de', (790, 400), 300, ts, delay=0.9, t=t); kword(Lr, "30분", (790, 720), 130, ts, delay=1.1, col=YEL)
    elif kind == 'price':
        Lr.icon('1f4b5', (540, 330), 340, ts, t=t)
        kword(Lr, "$3,995", (540, 720), 230, ts, delay=0.2, col=WHITE, stroke=16)
    elif kind in ('quiz', 'reveal'):
        kword(Lr, "지금 돈으로 얼마?", (540, 110), 96, ts if kind == 'quiz' else 1, col=GOLD)
        OPTS = [("① 500만 원", 0), ("② 1,000만 원", 0), ("③ 1,800만 원", 1)]; rev = kind == 'reveal'
        for j, (o, ok) in enumerate(OPTS):
            k = (ts - 0.3 - 0.15 * j) if not rev else 1
            if k < 0 or (rev and not ok): continue
            y = 290 + j * 130 if not rev else 290; sx, sy = squash(k, 0.22)
            fillc = (40, 170, 100) if rev else (255, 255, 255); w = 600 * sx
            Lr.rrect([540 - w / 2, y - 52 * sy, 540 + w / 2, y + 52 * sy], 52, fill=A(fillc, 1), outline=A(INK, 1), w=6)
            Lr.text((540, y), o, 62, A(WHITE if rev else INK, 1))
            if rev: Lr.icon('2705', (900, y), 120, ts, bob=False)
        if rev:
            if ts < 0.55:
                val = 18000000 + 81990000 * (1 - eout(ts / 0.55))
                Lr.d.text((540 * S, 560 * S), f"{val / 1e4:,.0f}만 원", font=F(140 * S), fill=YEL, anchor='mm', stroke_width=14 * S, stroke_fill=INK)
            else:
                kword(Lr, "약 1,800만 원", (540, 560), 140, ts - 0.55, col=YEL, stroke=14)
                Lr.icon('1f697', (300, 860), 260, ts, delay=0.9, t=t); kword(Lr, "= 경차 1대", (680, 860), 100, ts, delay=1.0, col=WHITE)
        pose = 'shock' if rev else 'talk'; sx, sy = squash(ts, 0.25)
        if not rev: Lr.paste(ap(pose), (880, 930), 0.4 * sx, 0.4 * sy)
    elif kind == 'but':
        Lr.icon('1f4de', (540, 420), 420, ts, t=t)
        kword(Lr, "전화만 됨", (540, 830), 140, ts, delay=0.3, col=WHITE, rot=-4)
    elif kind == 'replace':
        ICS = ['1f4f7', '1f3a5', '1f9ee', '23f0', '1f4bf', '1f4fc', '1f4fb', '1f4bb', '1f399-fe0f']
        for j, c in enumerate(ICS):
            x = 220 + (j % 3) * 320; y = 200 + (j // 3) * 280
            Lr.icon(c, (x, y), 200, ts, delay=0.25 * j, bob=False)
    elif kind == 'replace_price':
        Lr.icon('1f4f0', (540, 330), 300, ts, t=t); kword(Lr, "1991년 전단지", (540, 560), 96, ts, delay=0.15, col=WHITE)
        kword(Lr, "+ 약 1,000만 원", (540, 800), 140, ts, delay=0.5, col=YEL, stroke=14)
    elif kind == 'sum':
        kword(Lr, "2,800만 원어치", (540, 140), 120, ts, col=WHITE, stroke=12)
        Lr.icon('2b07-fe0f', (540, 340), 150, ts, delay=0.4, bob=False)
        Lr.photo('smart', (540, 650), 300, ts, delay=0.6, rot=4)
        kword(Lr, "40만 원대", (540, 990), 120, ts, delay=1.0, col=YEL, stroke=12)
    elif kind == 'score':
        sx, sy = squash(ts, 0.3); Lr.paste(ap('thumb'), (540, 640), 0.66 * sx, 0.66 * sy)
        R.sparkles(Lr, t, ts, 6, 540, 560, 460)
        post.append(lambda img: stamp(img, "문명 이기 ×70", 540, SY + 220, t - SCORE_T, size=130, col=GOLD, rot=-6))
    elif kind == 'cta':
        a = ease(ts / 0.2)
        Lr.rrect([110, 30, 970, 600], 40, fill=A((30, 26, 24), 0.95 * a), outline=A(GOLD, a), w=6)
        kword(Lr, "오늘의 문명템", (540, 105), 64, ts, col=GOLD, stroke=5)
        if ts > 0.1: Lr.photo('smart', (540, 360), 250, ts - 0.1, rot=3)
        sx, sy = squash(ts - 0.2, 0.3)
        if ts > 0.2: Lr.paste(ap('laugh'), (300, 860), 0.42 * sx, 0.42 * sy)
        b = ease((ts - 0.7) / 0.2)
        Lr.rrect([660, 780, 960, 880], 50, fill=A((235, 40, 40), b)); Lr.text((810, 830), "구독", 60, A(WHITE, b))
    z = 1 + 0.12 * (1 - eout(ts / 0.2)) if t > 0.1 else 1
    return Lr.done(), post, i, kind, ts, bg, z

BUBBLES = [(bt('intro') + 0.4, 1.9, "허허, 이게 그 벽돌폰이라네", 700, SY + 160, 'down'),
           (bt('quiz') + 0.8, 2.6, "자, 맞혀 보시게", 640, SY + 790, 'down'),
           (REVEAL + 0.7, 2.2, "내 땐 이게 차 한 대 값이었지…", 600, SY + 720, 'down'),
           (bt('cta') + 0.5, 2.8, "다음 물건 가져오시게!", 700, SY + 730, 'left')]

def draw_kinetic(img, t):
    cur = [p for p in PHR if p[0] - 0.02 <= t < p[1]]
    if not cur: return
    a, b, s = cur[-1]; k = t - a; sx, sy = squash(k, 0.18); f = F(104); d0 = ImageDraw.Draw(img); runs = []; i = 0
    while i < len(s):
        hit = next((h for h in KEY if s.startswith(h, i)), None)
        if hit: runs.append((hit, YEL)); i += len(hit)
        else:
            if runs and runs[-1][1] == WHITE: runs[-1] = (runs[-1][0] + s[i], WHITE)
            else: runs.append((s[i], WHITE))
            i += 1
    tw = sum(d0.textlength(r, font=f) for r, _ in runs) + 60; th = 180
    im = Image.new('RGBA', (int(tw), th), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 30
    for r, col in runs: d.text((x, th / 2), r, font=f, fill=col, anchor='lm', stroke_width=12, stroke_fill=INK); x += d.textlength(r, font=f)
    sc = min(1.0, 980 / tw); im = im.resize((max(2, int(tw * sc * sx)), max(2, int(th * sc * sy))), Image.BICUBIC)
    img.alpha_composite(im, (int(540 - im.width / 2), int(1470 - im.height / 2)))

def frame(t):
    sc, post, i, kind, ts, bg, z = scene(t)
    img = background(bg).convert('RGBA')
    if z > 1.001:
        w, h = int(W * z), int(SH * z); sc = sc.resize((w, h), Image.BICUBIC).crop(((w - W) // 2, (h - SH) // 2, (w - W) // 2 + W, (h - SH) // 2 + SH))
    img.alpha_composite(sc, (0, SY))
    for p in post: p(img)
    hud(img, t)
    if kind in PIP:
        pose = PIP[kind]; k = ts
        im = pip_img(pose); sx, sy = squash(k, 0.25) if k < 0.3 else (1, 1)
        if sx > 0.05:
            im2 = im.resize((max(2, int(im.width * sx)), max(2, int(im.height * sy))), Image.BICUBIC)
            img.alpha_composite(im2, (int(925 - im2.width / 2), int(345 + 6 * math.sin(t * 2.5) - im2.height / 2)))
    for st, dur, txt, x, y, tail in BUBBLES:
        if st <= t < st + dur: R.bubble(img, txt, x, y, t - st, tail)
    draw_kinetic(img, t)
    if 0 <= t - SCORE_T < 0.3:
        sh = 16 * math.sin((t - SCORE_T) * 80) * (1 - (t - SCORE_T) / 0.3)
        img = img.transform(img.size, Image.AFFINE, (1, 0, sh, 0, 1, sh * 0.6), resample=Image.BILINEAR)
    if t > 0.1 and ts < 0.06: img = Image.blend(img, Image.new('RGBA', img.size, (255, 255, 255, 255)), 0.35 * (1 - ts / 0.06))
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'civ_{tt}.png')
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'info':
        print(round(DUR, 2), [(round(b[0], 2), b[1]) for b in BT]); sys.exit()
    n = int(DUR * FPS)
    tmp = 'civ_video.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(frame(k / FPS).tobytes())
        if k % 300 == 0: print(k, n, flush=True)
    p.stdin.close(); p.wait()
    import os; os.replace(tmp, 'civ_video.mp4')
    json.dump({'cuts': [b[0] for b in BT[1:]], 'stamp': [SCORE_T], 'roll': [REVEAL, REVEAL + 0.55], 'chime': [bt('replace') + 0.25 * j for j in range(9)], 'dur': DUR}, open('civ_sfx.json', 'w'))
    print('done')
