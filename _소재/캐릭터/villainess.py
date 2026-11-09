"""오리지널 캐릭터: 악역 영애 '아스트라' (과학to마법 등장인물)
SVG 생성 → resvg 로 PNG. 표정/포즈 파라미터.
"""
import json, subprocess, sys, os
OUT = os.path.dirname(os.path.abspath(__file__))
LINE = '#3A2E5C'; SKIN = '#FFE6D8'; SKIN_SH = '#F6CDB9'; HAIR = '#E4DDF6'; HAIR_SH = '#B8ABDF'; HAIR_HL = '#FFFFFF'
DRESS = '#2B2156'; DRESS2 = '#3E2F7A'; GOLD = '#E9B949'; GEM = '#D9334A'; IRIS = '#7B4BD6'; IRIS_D = '#4A2A99'

def drill(cx, top, n=5, flip=1):
    s = []
    # side lock falling from head to drill
    s.append(f'<path d="M{cx + flip * 40},{top - 230} Q{cx - flip * 20},{top - 120} {cx},{top - 10}" fill="none" stroke="{LINE}" stroke-width="64" stroke-linecap="round"/>')
    s.append(f'<path d="M{cx + flip * 40},{top - 230} Q{cx - flip * 20},{top - 120} {cx},{top - 10}" fill="none" stroke="{HAIR}" stroke-width="54" stroke-linecap="round"/>')
    for i in range(n):
        y = top + i * 40; rx = 50 - i * 7; ry = 26 - i * 1.5
        s.append(f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="{HAIR}" stroke="{LINE}" stroke-width="5"/>')
        s.append(f'<path d="M{cx - rx + 6},{y - 6} Q{cx},{y + ry + 2} {cx + rx - 4},{y + 4}" fill="none" stroke="{HAIR_SH}" stroke-width="6" stroke-linecap="round"/>')
        s.append(f'<path d="M{cx - rx * 0.5},{y - ry * 0.55} Q{cx},{y - ry * 0.9} {cx + rx * 0.4},{y - ry * 0.6}" fill="none" stroke="{HAIR_HL}" stroke-width="4" stroke-linecap="round" opacity="0.85"/>')
    s.append(f'<path d="M{cx},{top + n * 40 - 14} q{4 * flip},18 {-6 * flip},30" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
    return ''.join(s)

def eye(cx, cy, kind, look, flip):
    s = []
    if kind == 'happy':
        return f'<path d="M{cx - 30},{cy + 6} Q{cx},{cy - 26} {cx + 30},{cy + 6}" fill="none" stroke="{LINE}" stroke-width="8" stroke-linecap="round"/>'
    if kind == 'smug':   # half-lidded, looking sideways
        s.append(f'<ellipse cx="{cx}" cy="{cy + 6}" rx="34" ry="26" fill="#fff"/>')
        s.append(f'<clipPath id="c{cx}"><ellipse cx="{cx}" cy="{cy + 6}" rx="34" ry="26"/></clipPath>')
        s.append(f'<g clip-path="url(#c{cx})"><circle cx="{cx + look}" cy="{cy + 10}" r="22" fill="{IRIS}"/><circle cx="{cx + look}" cy="{cy + 14}" r="11" fill="{IRIS_D}"/>'
                 f'<circle cx="{cx + look - 8}" cy="{cy + 2}" r="6" fill="#fff"/><rect x="{cx - 40}" y="{cy - 30}" width="80" height="26" fill="{SKIN}"/></g>')
        s.append(f'<path d="M{cx - 38},{cy - 2} L{cx + 38},{cy - 6 + 6 * flip}" stroke="{LINE}" stroke-width="9" stroke-linecap="round"/>')
        s.append(f'<path d="M{cx + 34 * flip},{cy - 4} l{12 * flip},-8" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
        s.append(f'<path d="M{cx - 26},{cy + 30} Q{cx},{cy + 36} {cx + 26},{cy + 30}" fill="none" stroke="{LINE}" stroke-width="3" opacity="0.5"/>')
        return ''.join(s)
    if kind == 'wide':   # shocked
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="34" ry="38" fill="#fff" stroke="{LINE}" stroke-width="6"/>')
        s.append(f'<circle cx="{cx}" cy="{cy + 2}" r="11" fill="{IRIS_D}"/><circle cx="{cx - 4}" cy="{cy - 3}" r="4" fill="#fff"/>')
        return ''.join(s)
    if kind == 'angry':
        s.append(f'<ellipse cx="{cx}" cy="{cy + 8}" rx="32" ry="22" fill="#fff"/>')
        s.append(f'<clipPath id="a{cx}"><ellipse cx="{cx}" cy="{cy + 8}" rx="32" ry="22"/></clipPath>')
        s.append(f'<g clip-path="url(#a{cx})"><circle cx="{cx}" cy="{cy + 10}" r="18" fill="{IRIS}"/><circle cx="{cx}" cy="{cy + 12}" r="8" fill="{IRIS_D}"/><circle cx="{cx - 5}" cy="{cy + 4}" r="5" fill="#fff"/></g>')
        s.append(f'<path d="M{cx - 36},{cy - 6 - 10 * flip} L{cx + 36},{cy - 6 + 10 * flip}" stroke="{LINE}" stroke-width="10" stroke-linecap="round"/>')
        return ''.join(s)
    # normal (open, confident)
    s.append(f'<ellipse cx="{cx}" cy="{cy + 4}" rx="33" ry="34" fill="#fff"/>')
    s.append(f'<circle cx="{cx + look * 0.5}" cy="{cy + 8}" r="24" fill="{IRIS}"/><circle cx="{cx + look * 0.5}" cy="{cy + 12}" r="12" fill="{IRIS_D}"/>')
    s.append(f'<circle cx="{cx + look * 0.5 - 9}" cy="{cy - 2}" r="7" fill="#fff"/><circle cx="{cx + look * 0.5 + 9}" cy="{cy + 18}" r="3" fill="#fff"/>')
    s.append(f'<path d="M{cx - 38},{cy - 18} Q{cx},{cy - 38} {cx + 38},{cy - 16}" fill="none" stroke="{LINE}" stroke-width="9" stroke-linecap="round"/>')
    s.append(f'<path d="M{cx + 34 * flip},{cy - 18} l{12 * flip},-10" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
    return ''.join(s)

def brows(kind):
    if kind == 'raised':
        return (f'<path d="M205,330 Q240,312 272,326" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M328,318 Q362,296 396,312" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
    if kind == 'angry':
        return (f'<path d="M205,322 L272,342" stroke="{LINE}" stroke-width="8" stroke-linecap="round"/>'
                f'<path d="M328,342 L396,322" stroke="{LINE}" stroke-width="8" stroke-linecap="round"/>')
    if kind == 'worried':
        return (f'<path d="M205,336 L272,318" stroke="{LINE}" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M328,318 L396,336" stroke="{LINE}" stroke-width="7" stroke-linecap="round"/>')
    return (f'<path d="M207,334 Q240,322 272,332" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M328,332 Q362,320 394,332" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')

def mouth(kind):
    if kind == 'smirk':
        return f'<path d="M282,488 Q305,500 330,478" fill="none" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>'
    if kind == 'laugh':   # ohohoho
        return (f'<path d="M272,478 Q300,470 330,476 Q326,516 300,520 Q276,516 272,478 Z" fill="#9A2B45" stroke="{LINE}" stroke-width="5"/>'
                f'<path d="M282,506 Q300,498 318,506 Q300,518 282,506Z" fill="#F07C8E"/>')
    if kind == 'o':
        return f'<ellipse cx="300" cy="492" rx="16" ry="20" fill="#9A2B45" stroke="{LINE}" stroke-width="5"/>'
    if kind == 'grit':
        return (f'<rect x="270" y="478" width="60" height="24" rx="8" fill="#fff" stroke="{LINE}" stroke-width="5"/>'
                f'<path d="M285,480 v20 M300,480 v20 M315,480 v20" stroke="{LINE}" stroke-width="3"/>')
    if kind == 'talk':
        return f'<path d="M280,482 Q300,476 322,482 Q314,504 300,505 Q286,504 280,482Z" fill="#9A2B45" stroke="{LINE}" stroke-width="5"/>'
    return f'<path d="M286,488 Q300,494 316,486" fill="none" stroke="{LINE}" stroke-width="5" stroke-linecap="round"/>'

def svg(eyes='smug', mouth_k='smirk', brow='raised', arm='none', blush=False, sweat=False, look=10, sparkle=False):
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">']
    # back hair
    p.append(f'<path d="M150,300 Q120,560 170,700 L430,700 Q480,560 450,300 Q440,170 300,165 Q160,170 150,300Z" fill="{HAIR_SH}" stroke="{LINE}" stroke-width="5"/>')
    # body / dress
    p.append(f'<path d="M120,800 Q130,650 220,615 L380,615 Q470,650 480,800Z" fill="{DRESS}" stroke="{LINE}" stroke-width="5"/>')
    p.append(f'<path d="M220,615 L300,700 L380,615" fill="{DRESS2}" stroke="{LINE}" stroke-width="5"/>')
    p.append(f'<path d="M205,620 Q300,660 395,620" fill="none" stroke="{GOLD}" stroke-width="9"/>')
    p.append(f'<circle cx="300" cy="664" r="17" fill="{GEM}" stroke="{GOLD}" stroke-width="6"/>')
    # high collar ruff
    p.append(f'<path d="M232,600 L250,560 L270,598 L290,556 L310,598 L330,556 L350,598 L368,560 L380,600Z" fill="#fff" stroke="{LINE}" stroke-width="4"/>')
    # neck
    p.append(f'<rect x="272" y="520" width="56" height="70" fill="{SKIN_SH}" stroke="{LINE}" stroke-width="4"/>')
    # drills (behind face edges)
    p.append(drill(150, 560, 5, 1)); p.append(drill(450, 560, 5, -1))
    # face
    p.append(f'<path d="M172,330 Q168,500 300,560 Q432,500 428,330 Q428,195 300,195 Q172,195 172,330Z" fill="{SKIN}" stroke="{LINE}" stroke-width="6"/>')
    # bangs (side-swept)
    p.append(f'<path d="M162,350 Q150,190 300,158 Q452,190 440,350 Q420,300 398,262 Q392,318 360,348 Q356,290 332,250 Q300,310 236,330 Q262,286 270,248 Q226,286 196,350 Q192,320 162,350Z" fill="{HAIR}" stroke="{LINE}" stroke-width="6" stroke-linejoin="round"/>')
    p.append(f'<path d="M210,236 Q300,186 392,222" fill="none" stroke="{HAIR_HL}" stroke-width="10" stroke-linecap="round" opacity="0.9"/>')
    p.append(f'<path d="M300,180 Q286,240 240,300 M330,200 Q330,250 352,300" fill="none" stroke="{HAIR_SH}" stroke-width="5" stroke-linecap="round"/>')
    # tiara
    p.append(f'<path d="M240,190 L255,150 L275,180 L300,130 L325,180 L345,150 L360,190 Q300,176 240,190Z" fill="{GOLD}" stroke="{LINE}" stroke-width="5"/>')
    p.append(f'<circle cx="300" cy="168" r="11" fill="#5AA9FF" stroke="{LINE}" stroke-width="3"/>')
    # face parts
    p.append(brows(brow)); p.append(eye(240, 400, eyes, look, -1)); p.append(eye(360, 400, eyes, look, 1))
    if blush: p.append('<ellipse cx="220" cy="456" rx="26" ry="12" fill="#FF8FA3" opacity="0.6"/><ellipse cx="380" cy="456" rx="26" ry="12" fill="#FF8FA3" opacity="0.6"/>')
    p.append(f'<path d="M298,440 l-6,16 l10,0" fill="none" stroke="{SKIN_SH}" stroke-width="4" stroke-linecap="round"/>')
    p.append(mouth(mouth_k))
    if sweat: p.append(f'<path d="M430,300 Q450,340 432,356 Q410,340 430,300Z" fill="#9AD7FF" stroke="{LINE}" stroke-width="4"/>')
    # arms / props
    if arm == 'fan':    # ohohoho pose: hand + folded fan at mouth
        p.append(f'<path d="M400,800 Q400,640 360,560" fill="none" stroke="{DRESS}" stroke-width="60" stroke-linecap="round"/>')
        p.append(f'<path d="M240,520 L340,440 L366,476 L262,548Z" fill="#fff" stroke="{LINE}" stroke-width="5"/>')
        p.append(f'<path d="M248,526 L346,450 M256,536 L354,462 M262,546 L360,472" stroke="{GOLD}" stroke-width="4"/>')
        p.append(f'<circle cx="355" cy="540" r="34" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/>')
    elif arm == 'wand':
        p.append(f'<path d="M420,800 Q470,620 500,470" fill="none" stroke="{DRESS}" stroke-width="62" stroke-linecap="round"/>')
        p.append(f'<path d="M500,470 L560,250" stroke="#6B4A2B" stroke-width="12" stroke-linecap="round"/>')
        p.append(f'<circle cx="505" cy="455" r="36" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/>')
        p.append(f'<path d="M560,205 l12,30 l32,2 l-25,20 l9,31 l-28,-18 l-28,18 l9,-31 l-25,-20 l32,-2Z" fill="{GOLD}" stroke="{LINE}" stroke-width="4"/>')
    elif arm == 'ear':  # earbud in
        p.append(f'<path d="M440,800 Q470,640 445,500" fill="none" stroke="{DRESS}" stroke-width="60" stroke-linecap="round"/>')
        p.append(f'<ellipse cx="438" cy="430" rx="20" ry="24" fill="#fff" stroke="{LINE}" stroke-width="5"/><rect x="430" y="440" width="15" height="48" rx="7" fill="#fff" stroke="{LINE}" stroke-width="5"/>')
        p.append(f'<circle cx="452" cy="478" r="32" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/>')
    if sparkle:
        for x, y, r in ((90, 200, 26), (520, 560, 22), (110, 560, 18)):
            p.append(f'<path d="M{x},{y - r} Q{x + 4},{y - 4} {x + r},{y} Q{x + 4},{y + 4} {x},{y + r} Q{x - 4},{y + 4} {x - r},{y} Q{x - 4},{y - 4} {x},{y - r}Z" fill="#FFE27A" stroke="{LINE}" stroke-width="3"/>')
    p.append('</svg>')
    return ''.join(p)

POSES = {
    'smug':      dict(eyes='smug', mouth_k='smirk', brow='raised'),
    'smug_talk': dict(eyes='smug', mouth_k='talk', brow='raised'),
    'ohoho':     dict(eyes='happy', mouth_k='laugh', brow='raised', arm='fan', blush=True),
    'cast':      dict(eyes='normal', mouth_k='talk', brow='raised', arm='wand', sparkle=True, look=4),
    'shock':     dict(eyes='wide', mouth_k='o', brow='worried', sweat=True),
    'angry':     dict(eyes='angry', mouth_k='grit', brow='angry'),
    'pout':      dict(eyes='smug', mouth_k='neutral', brow='worried', blush=True, look=-10),
    'earbud':    dict(eyes='happy', mouth_k='smirk', brow='raised', arm='ear', blush=True, sparkle=True),
}
if __name__ == '__main__':
    for k, kw in POSES.items():
        sv = os.path.join(OUT, f'{k}.svg'); open(sv, 'w').write(svg(**kw))
    js = "const {Resvg}=require('@resvg/resvg-js');const fs=require('fs');for(const f of process.argv.slice(1)){const r=new Resvg(fs.readFileSync(f,'utf8'),{fitTo:{mode:'width',value:900}});fs.writeFileSync(f.replace('.svg','.png'),r.render().asPng());}"
    subprocess.run(['node', '-e', js] + [os.path.join(OUT, f'{k}.svg') for k in POSES], check=True, cwd='/home/claude/assets')
    print('ok')
