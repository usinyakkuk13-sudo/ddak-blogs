import json, numpy as np, soundfile as sf, subprocess
v, sr = sf.read('voice.wav', dtype='float32')
if v.ndim > 1: v = v.mean(1)
x = json.load(open('sfx.json')); n = int(x['dur'] * sr) + sr
out = np.zeros(max(n, len(v)), np.float32); out[:len(v)] += v
def add(sig, t, g):
    i = int(t * sr); out[i:i + len(sig)] += g * sig[:len(out) - i]
tt = np.arange(int(0.35 * sr)) / sr
thump = (np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 14) + 0.3 * np.random.default_rng(1).normal(size=tt.size) * np.exp(-tt * 40)).astype(np.float32)
tc = np.arange(int(0.9 * sr)) / sr
chime = sum(np.sin(2 * np.pi * f * tc) * np.exp(-tc * d) for f, d in ((1046, 5), (1568, 6), (2093, 8))).astype(np.float32) / 3
for t in x['stamp']: add(thump, t, 0.35)
for t in x['chime']: add(chime, t, 0.12)
peak = np.abs(out).max(); out = out / max(peak, 1e-6) * 0.89 if peak > 0.89 else out
sf.write('mix.wav', out, sr)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'video.mp4', '-i', 'mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'EP01_4서클_사일런스.mp4'], check=True)
print('ok')
