import json, numpy as np, soundfile as sf
seg = json.load(open('asr.json'))
a, sr = sf.read('rec.wav', dtype='float32')
LINE = [1,1,2,2,2,3,3,4,4,5,5,6,6,6,7,7,7,7,8,9,9,9,9,10]
ORDER = [22] + list(range(0, 22)) + [23]
CUTS = [(35.78, 37.46)]  # filler "네." inside seg9
TH, MINP, KEEP = -46.0, 0.22, 0.09

def db_frames(x):
    hop = int(0.01 * sr); n = len(x) // hop
    f = x[:n * hop].reshape(n, hop)
    return 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9), hop

pieces = []  # (orig_s, orig_e) keep-ranges in order, with gap after
def keep_ranges(s, e):
    x = a[int(s * sr):int(e * sr)]
    d, hop = db_frames(x); quiet = d < TH
    rng = []; cur = s; i = 0; n = len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.01 >= MINP and i > 0 and j < n:
                ps, pe = s + i * 0.01, s + j * 0.01
                rng.append((cur, ps + KEEP / 2)); cur = pe - KEEP / 2
            i = j
        else: i += 1
    rng.append((cur, e))
    # apply manual cuts
    out = []
    for rs, re_ in rng:
        for cs, ce in CUTS:
            if rs < ce and re_ > cs:
                if rs < cs: out.append((rs, cs))
                rs = max(rs, ce)
        if re_ > rs: out.append((rs, re_))
    return out

audio = [np.zeros(int(0.12 * sr), np.float32)]; t = 0.12; tl = []; mp = []
for k, i in enumerate(ORDER):
    s, e = seg[i]['s'] - 0.06, seg[i]['e'] + 0.09
    st = t
    for rs, re_ in keep_ranges(s, e):
        x = a[int(rs * sr):int(re_ * sr)].copy(); f = int(0.008 * sr)
        x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        mp.append((rs, re_, t)); audio.append(x); t += len(x) / sr
    tl.append({'i': i, 'line': LINE[i], 's': st, 'e': t})
    if k < len(ORDER) - 1:
        nxt = ORDER[k + 1]
        g = 0.28 if k == 0 else (0.05 if LINE[nxt] == LINE[i] else 0.13)
        audio.append(np.zeros(int(g * sr), np.float32)); t += g
audio.append(np.zeros(int(0.5 * sr), np.float32)); t += 0.5
sf.write('tight2.wav', np.concatenate(audio), sr)
T = min(1.32, max(1.0, t / 56.5))
json.dump({'dur_raw': t, 'tempo': T, 'tl': tl, 'map': mp}, open('tl2_raw.json', 'w'))
print('raw', round(t, 2), 'tempo', round(T, 3), 'final', round(t / T, 2))
