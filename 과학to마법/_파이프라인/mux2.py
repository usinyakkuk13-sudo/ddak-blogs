import json, numpy as np, soundfile as sf, subprocess
sr = 48000
v, _ = sf.read('voice2.wav', dtype='float32')
if v.ndim > 1: v = v.mean(1)
x = json.load(open('sfx2.json')); n = max(int(x['dur'] * sr) + sr // 2, len(v))
voice = np.zeros(n, np.float32); voice[:len(v)] = v
fx = np.zeros(n, np.float32); bed = np.zeros(n, np.float32)
rng = np.random.default_rng(7)
def add(buf, sig, t, g):
    i = int(t * sr)
    if i >= n: return
    buf[i:i + len(sig)] += g * sig[:n - i]
def bp_noise(dur, f0, f1):
    m = int(dur * sr); w = rng.normal(size=m).astype(np.float32)
    W = np.fft.rfft(w); fr = np.fft.rfftfreq(m, 1 / sr)
    W *= ((fr > f0) & (fr < f1)); return np.fft.irfft(W, m).astype(np.float32)
# whoosh: rising band noise with swell envelope
wl = 0.22; tt = np.arange(int(wl * sr)) / sr
whoosh = bp_noise(wl, 600, 6000) * np.sin(np.pi * tt / wl) ** 2; whoosh /= np.abs(whoosh).max()
t3 = np.arange(int(0.35 * sr)) / sr
thump = (np.sin(2 * np.pi * 65 * t3) * np.exp(-t3 * 12) + 0.25 * rng.normal(size=t3.size) * np.exp(-t3 * 40)).astype(np.float32)
tc = np.arange(int(0.9 * sr)) / sr
chime = (sum(np.sin(2 * np.pi * f * tc) * np.exp(-tc * d) for f, d in ((1046, 5), (1568, 6), (2093, 8))) / 3).astype(np.float32)
for t in x['cuts']: add(fx, whoosh, max(0, t - 0.12), 0.16)
for t in x['stamp']: add(fx, thump, t, 0.5)
for t in x['chime']: add(fx, chime, t, 0.14)
# beat bed: 118 bpm kick + offbeat hat + soft bass pulse
bpm = 118; beat = 60 / bpm; tk = np.arange(int(0.25 * sr)) / sr
kick = (np.sin(2 * np.pi * (50 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 14)).astype(np.float32)
hat = bp_noise(0.05, 6000, 14000) * np.exp(-np.arange(int(0.05 * sr)) / sr * 70); hat /= np.abs(hat).max()
k = 0; t = 0.0
while t < x['dur'] - 0.5:
    add(bed, kick, t, 0.55); add(bed, hat, t + beat / 2, 0.18)
    if k % 4 == 2: add(bed, hat, t + beat * 0.75, 0.1)
    t += beat; k += 1
fade = np.ones(n, np.float32); fl = int(1.0 * sr); fade[-fl:] = np.linspace(1, 0, fl)
# duck bed under voice
env = np.convolve(np.abs(voice), np.ones(int(0.05 * sr)) / int(0.05 * sr), 'same'); duck = 1 - 0.45 * np.clip(env / 0.08, 0, 1)
mix = voice + fx + bed * 0.22 * duck * fade
pk = np.abs(mix).max()
if pk > 0.95: mix *= 0.95 / pk
sf.write('mix2.wav', mix, sr)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'video2.mp4', '-i', 'mix2.wav', '-af', 'loudnorm=I=-14:TP=-1.2:LRA=9',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', 'EP01_4서클_사일런스_v2.mp4'], check=True)
print('ok')
