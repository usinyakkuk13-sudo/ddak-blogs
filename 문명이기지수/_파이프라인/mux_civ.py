import json, numpy as np, soundfile as sf, subprocess
sr = 48000; x = json.load(open('civ_sfx.json')); n = int(x['dur'] * sr) + sr // 3
fx = np.zeros(n, np.float32); bed = np.zeros(n, np.float32); rng = np.random.default_rng(11)
def add(buf, sig, t, g):
    i = int(t * sr)
    if 0 <= i < n: buf[i:i + len(sig)] += g * sig[:n - i]
def bp_noise(dur, f0, f1):
    m = int(dur * sr); w = rng.normal(size=m).astype(np.float32); W = np.fft.rfft(w); fr = np.fft.rfftfreq(m, 1 / sr)
    W *= ((fr > f0) & (fr < f1)); return np.fft.irfft(W, m).astype(np.float32)
def tone(f, dur, dec):
    t = np.arange(int(dur * sr)) / sr; return (np.sin(2 * np.pi * f * t) * np.exp(-t * dec)).astype(np.float32)
wl = 0.22; tt = np.arange(int(wl * sr)) / sr
whoosh = bp_noise(wl, 600, 6000) * np.sin(np.pi * tt / wl) ** 2; whoosh /= np.abs(whoosh).max()
t3 = np.arange(int(0.4 * sr)) / sr
impact = (np.sin(2 * np.pi * (45 + 80 * np.exp(-t3 * 25)) * t3) * np.exp(-t3 * 9) + 0.3 * rng.normal(size=t3.size) * np.exp(-t3 * 35)).astype(np.float32)
tick = tone(2600, 0.03, 120); ding = (tone(1760, 1.0, 4) + 0.6 * tone(2637, 1.0, 5)) / 1.6; pop = tone(900, 0.12, 30)
for t in x['cuts']: add(fx, whoosh, max(0, t - 0.12), 0.2)
for t in x['stamp']: add(fx, impact, t, 0.7); add(fx, ding, t + 0.05, 0.3)
r0, r1 = x['roll']; k = r0
while k < r1: add(fx, tick, k, 0.3); k += 0.035
add(fx, ding, r1, 0.35)
for t in x['chime']: add(fx, pop, t, 0.25)
# lofi-ish bed: 100bpm kick/hat + warm chord pad
bpm = 100; beat = 60 / bpm; tk = np.arange(int(0.25 * sr)) / sr
kick = (np.sin(2 * np.pi * (50 + 60 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 14)).astype(np.float32)
hat = bp_noise(0.05, 6000, 14000) * np.exp(-np.arange(int(0.05 * sr)) / sr * 70); hat /= np.abs(hat).max()
t = 0.0; c = 0
while t < x['dur'] - 0.4:
    if c % 2 == 0: add(bed, kick, t, 0.6)
    add(bed, hat, t + beat / 2, 0.15); t += beat; c += 1
chords = [(220, 277.2, 329.6), (196, 246.9, 293.7), (174.6, 220, 261.6), (196, 246.9, 293.7)]
bar = beat * 4; t = 0.0; i = 0
while t < x['dur']:
    L = int(bar * sr); tt2 = np.arange(L) / sr; env = np.minimum(1, tt2 / 0.3) * np.minimum(1, (bar - tt2) / 0.3)
    sig = sum(np.sin(2 * np.pi * f * tt2) + 0.3 * np.sin(4 * np.pi * f * tt2) for f in chords[i % 4]) * env / 6
    add(bed, sig.astype(np.float32), t, 0.5); t += bar; i += 1
fade = np.ones(n, np.float32); fl = int(0.8 * sr); fade[-fl:] = np.linspace(1, 0, fl)
mix = fx + bed * 0.5 * fade; mix *= 0.9 / max(1e-6, np.abs(mix).max())
sf.write('civ_mix.wav', mix, sr)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'civ_video.mp4', '-i', 'civ_mix.wav', '-af', 'loudnorm=I=-15:TP=-1.2:LRA=9',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', '문명이기_01_휴대폰_샘플.mp4'], check=True)
print('ok')
