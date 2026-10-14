"""QC: audio lag of the narration in the output vs the source, and per-frame
video alignment of the speaker segments vs the source (reframed identically)."""
import subprocess, sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import SEGMENTS, FPS, W, H, FACE  # noqa

src, out = sys.argv[1], sys.argv[2]

def pcm(path, sr=8000):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)

a, b = pcm(src), pcm(out)
n = min(len(a), len(b))
for name, (s, e) in {"whole": (0, 19.0), "0-6s": (0, 6), "6-12s": (6, 12), "12-19s": (12, 19)}.items():
    x, y = a[int(s * 8000):int(e * 8000)], b[int(s * 8000):int(e * 8000)]
    lags = range(-80, 81)
    c = [np.dot(x[80:-80], y[80 + L:len(y) - 80 + L]) for L in lags]
    best = lags[int(np.argmax(c))]
    corr = np.corrcoef(x[80:-80], y[80 + best:len(y) - 80 + best])[0, 1]
    print(f"audio {name:7s}: best lag {best/8:+.2f} ms  corr {corr:.3f}")

def frames(path, w=108, h=192):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={w}:{h}", "-f", "rawvideo",
                        "-pix_fmt", "gray", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)

S, O = frames(src), frames(out)
print("frames src/out:", len(S), len(O))
# Motion-signature sync: per-frame motion energy (mean |frame diff|) is insensitive
# to grade, grain and zoom; cross-correlate it per speaker segment.
def motion(F):
    return np.abs(np.diff(F[:, 20:150], axis=0)).mean(axis=(1, 2))

ms, mo = motion(S), motion(O)
for seg in SEGMENTS:
    if seg["kind"] != "speaker":
        continue
    a0, a1 = int(seg["start"] * FPS) + 8, min(int(seg["end"] * FPS), len(ms)) - 4
    best = max(range(-4, 5), key=lambda L: np.corrcoef(ms[a0 + L:a1 + L], mo[a0:a1])[0, 1])
    print(f"motion {seg['id']}: best lag {best:+d} frames, r={np.corrcoef(ms[a0 + best:a1 + best], mo[a0:a1])[0, 1]:.3f}")
