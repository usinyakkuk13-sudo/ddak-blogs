"""오리지널 캐릭터: 문명 감정사 할아버지 (문명 이기 지수 진행자)"""
import subprocess, os
OUT = os.path.dirname(os.path.abspath(__file__))
LINE = '#3B2A22'; SKIN = '#FFE0C8'; SKIN_SH = '#F2C3A6'; WH = '#F7F4EE'; WH_SH = '#D9D2C6'
VEST = '#7A4A2A'; SHIRT = '#FFFFFF'; TIE = '#C8323C'; GOLD = '#E3B54A'

def eyes(kind):
    if kind == 'happy':
        return ''.join(f'<path d="M{x - 24},{412} Q{x},{390} {x + 24},{412}" fill="none" stroke="{LINE}" stroke-width="8" stroke-linecap="round"/>' for x in (245, 355))
    if kind == 'shock':
        return ''.join(f'<circle cx="{x}" cy="402" r="20" fill="#fff" stroke="{LINE}" stroke-width="5"/><circle cx="{x}" cy="404" r="7" fill="{LINE}"/>' for x in (245, 355))
    if kind == 'squint':
        return ''.join(f'<path d="M{x - 22},{404} L{x + 22},{404}" stroke="{LINE}" stroke-width="8" stroke-linecap="round"/>' for x in (245, 355))
    return ''.join(f'<ellipse cx="{x}" cy="404" rx="12" ry="15" fill="{LINE}"/><circle cx="{x - 4}" cy="398" r="4" fill="#fff"/>' for x in (245, 355))

def svg(eye='normal', mouth='smile', brow='up', prop='none', glasses_up=False, sweat=False, sparkle=False):
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">']
    # body: shirt + vest + bow tie
    p.append(f'<path d="M110,800 Q120,640 220,610 L380,610 Q480,640 490,800Z" fill="{VEST}" stroke="{LINE}" stroke-width="5"/>')
    p.append(f'<path d="M250,610 L300,720 L350,610Z" fill="{SHIRT}" stroke="{LINE}" stroke-width="5"/>')
    p.append(f'<circle cx="300" cy="740" r="8" fill="{GOLD}" stroke="{LINE}" stroke-width="3"/><circle cx="300" cy="780" r="8" fill="{GOLD}" stroke="{LINE}" stroke-width="3"/>')
    p.append(f'<path d="M262,600 L300,622 L338,600 L338,646 L300,624 L262,646Z" fill="{TIE}" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>')
    p.append(f'<circle cx="300" cy="623" r="10" fill="{TIE}" stroke="{LINE}" stroke-width="4"/>')
    # pocket watch chain
    p.append(f'<path d="M380,700 Q420,730 440,700" fill="none" stroke="{GOLD}" stroke-width="5"/>')
    # neck + head
    p.append(f'<rect x="272" y="540" width="56" height="70" fill="{SKIN_SH}" stroke="{LINE}" stroke-width="4"/>')
    p.append(f'<ellipse cx="170" cy="420" rx="26" ry="36" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/><ellipse cx="430" cy="420" rx="26" ry="36" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/>')
    p.append(f'<path d="M178,360 Q170,560 300,580 Q430,560 422,360 Q420,220 300,215 Q180,220 178,360Z" fill="{SKIN}" stroke="{LINE}" stroke-width="6"/>')
    # bald shine + side white hair
    p.append(f'<ellipse cx="270" cy="265" rx="40" ry="16" fill="#fff" opacity="0.7"/>')
    for sx in (1, -1):
        cx = 300 - sx * 125
        p.append(f'<path d="M{cx + sx * 10},{300} Q{cx - sx * 40},{330} {cx - sx * 25},{380} Q{cx - sx * 50},{390} {cx - sx * 20},{420} Q{cx + sx * 5},{380} {cx + sx * 20},{330}Z" fill="{WH}" stroke="{LINE}" stroke-width="5"/>')
    # brows (bushy white)
    by = 352 if brow == 'up' else 368
    for x in (245, 355):
        p.append(f'<path d="M{x - 34},{by + 6} Q{x},{by - 16} {x + 34},{by + 6} Q{x},{by - 2} {x - 34},{by + 6}Z" fill="{WH}" stroke="{LINE}" stroke-width="4"/>')
    p.append(eyes(eye))
    # round glasses
    gy = 340 if glasses_up else 404
    for x in (245, 355):
        p.append(f'<circle cx="{x}" cy="{gy}" r="38" fill="#BFE3FF" fill-opacity="0.25" stroke="{GOLD}" stroke-width="6"/>')
    p.append(f'<path d="M283,{gy} Q300,{gy - 10} 317,{gy}" fill="none" stroke="{GOLD}" stroke-width="6"/>')
    # nose
    p.append(f'<ellipse cx="300" cy="455" rx="20" ry="16" fill="{SKIN_SH}" stroke="{LINE}" stroke-width="4"/>')
    # mustache + mouth
    if mouth == 'o':
        p.append(f'<ellipse cx="300" cy="515" rx="16" ry="20" fill="#7A2230" stroke="{LINE}" stroke-width="5"/>')
    elif mouth == 'talk':
        p.append(f'<path d="M278,505 Q300,500 322,505 Q316,530 300,532 Q284,530 278,505Z" fill="#7A2230" stroke="{LINE}" stroke-width="5"/>')
    elif mouth == 'laugh':
        p.append(f'<path d="M268,500 Q300,494 332,500 Q326,542 300,545 Q274,542 268,500Z" fill="#7A2230" stroke="{LINE}" stroke-width="5"/><path d="M282,530 Q300,522 318,530 Q300,542 282,530Z" fill="#F07C8E"/>')
    else:
        p.append(f'<path d="M280,512 Q300,524 320,512" fill="none" stroke="{LINE}" stroke-width="5" stroke-linecap="round"/>')
    p.append(f'<path d="M300,478 Q262,468 236,488 Q222,500 214,492 Q226,512 256,500 Q280,494 300,490 Q320,494 344,500 Q374,512 386,492 Q378,500 364,488 Q338,468 300,478Z" fill="{WH}" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>')
    if sweat: p.append(f'<path d="M420,320 Q440,360 422,376 Q400,360 420,320Z" fill="#9AD7FF" stroke="{LINE}" stroke-width="4"/>')
    if prop == 'loupe':
        p.append(f'<path d="M440,800 Q470,650 430,560" fill="none" stroke="{VEST}" stroke-width="60" stroke-linecap="round"/>')
        p.append(f'<path d="M420,540 L470,470" stroke="#5A3A22" stroke-width="18" stroke-linecap="round"/>')
        p.append(f'<circle cx="490" cy="440" r="56" fill="#CFEFFF" fill-opacity="0.45" stroke="{GOLD}" stroke-width="10"/>')
        p.append(f'<circle cx="430" cy="560" r="32" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/>')
    elif prop == 'thumb':
        p.append(f'<path d="M450,800 Q480,660 470,560" fill="none" stroke="{VEST}" stroke-width="60" stroke-linecap="round"/>')
        p.append(f'<rect x="440" y="520" width="64" height="58" rx="18" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/><rect x="458" y="470" width="24" height="60" rx="12" fill="{SKIN}" stroke="{LINE}" stroke-width="5"/>')
    if sparkle:
        for x, y, r in ((90, 220, 24), (520, 250, 20), (100, 600, 18)):
            p.append(f'<path d="M{x},{y - r} Q{x + 4},{y - 4} {x + r},{y} Q{x + 4},{y + 4} {x},{y + r} Q{x - 4},{y + 4} {x - r},{y} Q{x - 4},{y - 4} {x},{y - r}Z" fill="#FFE27A" stroke="{LINE}" stroke-width="3"/>')
    p.append('</svg>'); return ''.join(p)

POSES = {'smile': dict(), 'talk': dict(mouth='talk'), 'loupe': dict(eye='squint', mouth='smile', prop='loupe', brow='down'),
         'shock': dict(eye='shock', mouth='o', glasses_up=True, sweat=True), 'laugh': dict(eye='happy', mouth='laugh', sparkle=True),
         'thumb': dict(eye='happy', mouth='smile', prop='thumb', sparkle=True)}
if __name__ == '__main__':
    fs = []
    for k, kw in POSES.items():
        f = os.path.join(OUT, f'ap_{k}.svg'); open(f, 'w').write(svg(**kw)); fs.append(f)
    js = "const {Resvg}=require('@resvg/resvg-js');const fs=require('fs');for(const f of process.argv.slice(1)){const r=new Resvg(fs.readFileSync(f,'utf8'),{fitTo:{mode:'width',value:900}});fs.writeFileSync(f.replace('.svg','.png'),r.render().asPng());}"
    subprocess.run(['node', '-e', js] + fs, check=True, cwd='/home/claude/assets'); print('ok')
