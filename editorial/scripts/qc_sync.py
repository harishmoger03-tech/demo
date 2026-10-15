"""QC: per-scene motion-signature lag between the source and the presenter scenes of the
render (insensitive to grade, grain, push-in and type). Usage: qc_sync.py <project> <render.mp4>"""
import json, subprocess, sys
import numpy as np
PJ = json.load(open(f"{sys.argv[1]}/project.json"))
def frames(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", "fps=30,scale=108:192", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, 192, 108).astype(np.float32)
S, O = frames(PJ["source"] if PJ["source"].startswith("/") else f"{sys.argv[1]}/{PJ['source']}"), frames(sys.argv[2])
# presenter region only (left half covers splits too), rows above captions
ms = np.abs(np.diff(S[:, 20:140, 5:50], axis=0)).mean(axis=(1, 2))
mo = np.abs(np.diff(O[:, 20:140, 5:50], axis=0)).mean(axis=(1, 2))
for s in PJ["scenes"]:
    if s["kind"] == "fullscreen":
        continue
    a0, a1 = int(s["t0"] * 30) + 6, min(int(s["t1"] * 30), len(mo)) - 3
    best = max(range(-4, 5), key=lambda L: np.corrcoef(ms[a0 + L:a1 + L], mo[a0:a1])[0, 1])
    print(f"{s['id']}: best lag {best:+d} frames  r={np.corrcoef(ms[a0+best:a1+best], mo[a0:a1])[0,1]:.3f}")
