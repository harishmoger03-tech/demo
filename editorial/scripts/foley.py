"""Soft paper / print foley from the Video-Skills SFX pack, mixed UNDER the untouched
original sound. Builds work/foley.wav (stem) and work/mix.wav (original + foley).

Usage: python3 -I scripts/foley.py <project_dir> assets/sfx   (files copied from Video-Skills 'Sfx Pack/SFX')
"""
import json, os, subprocess, sys
import numpy as np

root, pack = os.path.abspath(sys.argv[1]), sys.argv[2]
PJ = json.load(open(f"{root}/project.json"))
SR = 48000
PICKS = {  # foley id: (file in the SFX pack / assets/sfx, start, length)
    "paper_slide": ("Mountain Audio - Sheet of Paper Shake 5.wav", 0.15, 0.8),
    "paper_drop": ("Mountain Audio - Sheet of Paper Shake 5.wav", 0.35, 0.45),
    "print_tick": ("Click.wav", 0.0, 0.3),
    "print_feed": ("Mechanical 2.m4a", 0.45, 0.7),
    "pen_tick": ("Click Lighter.wav", 0.0, 0.25),
}


def load(rel, ss, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(dur), "-i", os.path.join(pack, rel),
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = len(x); f = min(int(0.03 * SR), n // 4)
    x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]
    return x / (np.abs(x).max() + 1e-9)          # peak-normalised; cue dB sets the level


dur = PJ["frames"] / PJ["fps"]
out = np.zeros((int(dur * SR) + SR, 2), np.float32)
cues = []
for c in PJ["foley"]:
    if c["sfx"] == "pen_tick":                    # one tick per ledger entry
        lc = PJ["ledger_check"]
        cues += [dict(c, t=lc["t"] + i * lc["step"]) for i in range(len(PJ["ledger"]))]
    else:
        cues.append(c)
cache = {}
for c in cues:
    if c["sfx"] not in cache:
        cache[c["sfx"]] = load(*PICKS[c["sfx"]])
    s = cache[c["sfx"]] * 10 ** (c["db"] / 20)
    peak = int(np.argmax(np.abs(s).sum(1)))      # lock the transient, not the clip start
    i0 = max(0, int(c["t"] * SR) - peak)
    out[i0:i0 + len(s)] += s[: len(out) - i0]
out = out[: int(dur * SR)]
os.makedirs(f"{root}/work", exist_ok=True)


def wav(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_f32le", path], input=x.tobytes(), check=True)


wav(f"{root}/work/foley.wav", out)
src = os.path.normpath(os.path.join(root, PJ["source"]))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", f"{root}/work/foley.wav", "-filter_complex",
                "[0:a]aresample=48000[v];[v][1:a]amix=inputs=2:normalize=0:duration=first[m]", "-map", "[m]",
                "-c:a", "pcm_f32le", f"{root}/work/mix.wav"], check=True)
print("foley cues", len(cues))
