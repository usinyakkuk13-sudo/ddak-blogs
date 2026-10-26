import json, numpy as np, soundfile as sf, subprocess
sr = 48000
x = json.load(open('sfx3.json'))
v, _ = sf.read('voice3a.wav', dtype='float32')
if v.ndim > 1: v = v.mean(1)
i0 = int(x['ins'] * sr)
v = np.concatenate([v[:i0], np.zeros(int(x['ins_len'] * sr), np.float32), v[i0:]])
n = max(int(x['dur'] * sr) + sr // 3, len(v))
voice = np.zeros(n, np.float32); voice[:len(v)] = v
fx = np.zeros(n, np.float32); bed = np.zeros(n, np.float32)
rng = np.random.default_rng(7)
def add(buf, sig, t, g):
    i = int(t * sr)
    if i >= n or i < 0: return
    buf[i:i + len(sig)] += g * sig[:n - i]
def bp_noise(dur, f0, f1):
    m = int(dur * sr); w = rng.normal(size=m).astype(np.float32)
    W = np.fft.rfft(w); fr = np.fft.rfftfreq(m, 1 / sr); W *= ((fr > f0) & (fr < f1)); return np.fft.irfft(W, m).astype(np.float32)
def tone(f, dur, dec):
    t = np.arange(int(dur * sr)) / sr; return (np.sin(2 * np.pi * f * t) * np.exp(-t * dec)).astype(np.float32)
wl = 0.22; tt = np.arange(int(wl * sr)) / sr
whoosh = bp_noise(wl, 600, 6000) * np.sin(np.pi * tt / wl) ** 2; whoosh /= np.abs(whoosh).max()
t3 = np.arange(int(0.4 * sr)) / sr
impact = (np.sin(2 * np.pi * (45 + 80 * np.exp(-t3 * 25)) * t3) * np.exp(-t3 * 9) + 0.3 * rng.normal(size=t3.size) * np.exp(-t3 * 35)).astype(np.float32)
chime = (tone(1046, 0.9, 5) + tone(1568, 0.9, 6) + tone(2093, 0.9, 8)) / 3
tick = tone(2600, 0.03, 120)
ding = (tone(1760, 1.0, 4) + 0.6 * tone(2637, 1.0, 5)) / 1.6
for t in x['cuts']: add(fx, whoosh, max(0, t - 0.12), 0.17)
for t in x['stamp']: add(fx, impact, t, 0.6)
for t in x['chime']: add(fx, chime, t, 0.15)
# mana calc: drain whirr, number roll ticks, ding + rising sparkle on refill
ins = x['ins']; td = np.arange(int(1.2 * sr)) / sr
drain = (np.sin(2 * np.pi * np.cumsum(900 - 600 * td / 1.2) / sr) * 0.6).astype(np.float32) * np.linspace(1, 0.3, td.size)
add(fx, drain, ins + 0.1, 0.12)
r0, r1 = x['roll']; k = r0
while k < r1: add(fx, tick, k, 0.25); k += 0.035
add(fx, ding, r1, 0.3)
for j, f in enumerate([880, 1109, 1319, 1760]): add(fx, tone(f, 0.4, 7), r1 + 0.05 + j * 0.06, 0.12)
# beat bed 118bpm
bpm = 118; beat = 60 / bpm; tk = np.arange(int(0.25 * sr)) / sr
kick = (np.sin(2 * np.pi * (50 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 14)).astype(np.float32)
hat = bp_noise(0.05, 6000, 14000) * np.exp(-np.arange(int(0.05 * sr)) / sr * 70); hat /= np.abs(hat).max()
t = 0.0; c = 0
while t < x['dur'] - 0.4:
    add(bed, kick, t, 0.55); add(bed, hat, t + beat / 2, 0.18)
    if c % 4 == 2: add(bed, hat, t + beat * 0.75, 0.1)
    t += beat; c += 1
fade = np.ones(n, np.float32); fl = int(0.8 * sr); fade[-fl:] = np.linspace(1, 0, fl)
env = np.convolve(np.abs(voice), np.ones(int(0.05 * sr)) / int(0.05 * sr), 'same'); duck = 1 - 0.45 * np.clip(env / 0.08, 0, 1)
mix = voice + fx + bed * 0.24 * duck * fade
pk = np.abs(mix).max()
if pk > 0.95: mix *= 0.95 / pk
sf.write('mix3.wav', mix, sr)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'video3.mp4', '-i', 'mix3.wav', '-af', 'loudnorm=I=-14:TP=-1.2:LRA=9',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', '사일런스_v3.mp4'], check=True)
print('ok')
