"""Synthesise the music bed and sound effects (no third-party audio), then mix with
the untouched original narration.

Usage: python3 -I scripts/audio.py <source.mp4> <workdir>
Writes <workdir>/music.wav, <workdir>/sfx.wav and <workdir>/mix.wav (48 kHz stereo).
"""
import os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import OUT_DUR, SFX, SRC_DUR  # noqa: E402

SR = 48000
N = int(round(OUT_DUR * SR))
rng = np.random.default_rng(7)


def db(x):
    return 10 ** (x / 20)


def write_wav(path, x):
    """Write float stereo (n, 2) as 24-bit-safe float WAV via ffmpeg."""
    x = np.asarray(x, np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-c:a", "pcm_f32le", path], input=x.tobytes(), check=True)


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):          # short signals only
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def fft_lowpass(x, fc, slope=2.0):
    """Gentle zero-phase low-pass in the frequency domain (for long signals)."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    g = 1 / np.sqrt(1 + (f / fc) ** (2 * slope))
    return np.fft.irfft(X * (g[:, None] if x.ndim == 2 else g), n=x.shape[0], axis=0)


def reverb(x, seconds=2.2, mix=0.28):
    """Convolution with a synthetic, decorrelated stereo exponential tail."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * 6.9 / seconds)
    ir = np.stack([rng.standard_normal(n) * env, rng.standard_normal(n) * env], 1)
    ir = fft_lowpass(ir, 5000, 1.0)
    ir /= np.sqrt((ir ** 2).sum(0))
    L = x.shape[0] + n
    nfft = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft, axis=0) * np.fft.rfft(ir, nfft, axis=0), nfft, axis=0)[: x.shape[0]]
    return (1 - mix) * x + mix * wet


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------- music
# 96 BPM, one chord per bar (2.5 s). Minor colour while the cost "adds up",
# lifting through F–G and resolving to C major on "paise bachte hain".
BAR = 2.5
CHORDS = [  # (bass midi, [pad midi notes])
    (45, [57, 60, 64, 67, 71]),   # Am9
    (41, [57, 60, 64, 65]),       # Fmaj7
    (38, [57, 60, 62, 65]),       # Dm7
    (40, [57, 59, 64, 68]),       # E7sus→E (tension under 'kaafi zyada')
    (41, [57, 60, 64, 65]),       # Fmaj7
    (43, [59, 62, 67, 69]),       # G6
    (41, [57, 60, 64, 65]),       # Fmaj7
    (36, [55, 59, 62, 64, 67]),   # Cmaj9 (resolve)
    (36, [55, 59, 62, 64, 67]),   # (tail)
]


def music():
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    xf = int(0.45 * SR)                       # chord crossfade
    for bi, (bass, notes) in enumerate(CHORDS):
        s0 = max(int((bi * BAR) * SR) - xf // 2, 0)
        s1 = min(int(((bi + 1) * BAR) * SR) + xf // 2, N)
        if s0 >= N:
            break
        n = s1 - s0
        tt = t[s0:s1]
        env = np.ones(n)
        a = min(xf, n)
        env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
        env[-a:] *= np.cos(np.linspace(0, np.pi / 2, a)) ** 2
        seg = np.zeros((n, 2))
        # warm pad: soft band-limited saws, detuned per channel
        for m in notes:
            for ch, det in ((0, -0.06), (1, 0.06)):
                f0 = midi(m + det)
                ph = rng.uniform(0, 2 * np.pi)
                saw = sum(np.sin(2 * np.pi * f0 * k * tt + ph * k) / k ** 1.35 for k in range(1, 9))
                seg[:, ch] += saw * 0.06
        # sub bass (sine, octave below the bass note)
        sub = np.sin(2 * np.pi * midi(bass) * tt) * 0.16 + np.sin(2 * np.pi * midi(bass + 12) * tt) * 0.05
        seg += sub[:, None]
        out[s0:s1] += seg * env[:, None]
    out = fft_lowpass(out, 1500, 1.5)
    # slow pad breathing
    out *= (0.85 + 0.15 * np.sin(2 * np.pi * t / (BAR * 2)))[:, None]

    # felt-piano style pluck arpeggio in 8ths, entering with the first graphic (3.2 s)
    step = BAR / 8
    k = 0
    for bi, (_, notes) in enumerate(CHORDS):
        pattern = [notes[i % len(notes)] + 12 for i in (0, 2, 1, 3, 0, 2, 3, 1)]
        for j, m in enumerate(pattern):
            st = bi * BAR + j * step
            if st < 3.2 or st > OUT_DUR - 0.3:
                continue
            i0 = int(st * SR)
            n = min(int(0.9 * SR), N - i0)
            tt = np.arange(n) / SR
            f0 = midi(m)
            tone = (np.sin(2 * np.pi * f0 * tt) + 0.25 * np.sin(4 * np.pi * f0 * tt)
                    + 0.08 * np.sin(6 * np.pi * f0 * tt))
            tone *= np.exp(-tt * 5.5) * (1 - np.exp(-tt * 400))
            vel = 0.075 * (1.0 if j % 2 == 0 else 0.7)
            pan = 0.5 + 0.28 * np.sin(k * 1.7)
            out[i0:i0 + n, 0] += tone * vel * (1 - pan)
            out[i0:i0 + n, 1] += tone * vel * pan
            k += 1
    out = reverb(out, 2.4, 0.32)
    # fade in 0–0.6 s, fade out over the final second (ends with the picture fade)
    fade = np.ones(N)
    fi = int(0.6 * SR)
    fade[:fi] = np.linspace(0, 1, fi) ** 2
    fo = int(1.0 * SR)
    fade[-fo:] = np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
    out *= fade[:, None]
    return out / np.abs(out).max()


# ------------------------------------------------------------------- sfx
def bandpass_sweep(n, f_from, f_to, q=1.4):
    """Noise through a time-varying 2-pole band-pass (state-variable filter)."""
    x = rng.standard_normal(n)
    fc = np.geomspace(f_from, f_to, n)
    y = np.empty(n)
    low = band = 0.0
    for i in range(n):
        f = 2 * np.sin(np.pi * fc[i] / SR)
        high = x[i] - low - band / q
        band += f * high
        low += f * band
        y[i] = band
    return y


def whoosh(dur=0.55):
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    up = bandpass_sweep(n, 250, 2600)
    env = np.where(tt < 0.62, (tt / 0.62) ** 2.2, np.exp(-(tt - 0.62) * 9))
    l = up * env
    r = np.roll(up, 37) * env            # slight width
    return np.stack([l, r], 1)


def impact_soft():
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    f = 42 + 48 * np.exp(-tt * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5)
    click = onepole_lp(rng.standard_normal(n), 1800) * np.exp(-tt * 70) * 0.6
    x = body + click
    return np.stack([x, x], 1)


def tick():
    n = int(0.08 * SR)
    tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt * 90) + 0.3 * rng.standard_normal(n) * np.exp(-tt * 160)
    return np.stack([x, x], 1)


def chime(root=72):
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    x = np.zeros(n)
    for m, a in ((root, 1.0), (root + 7, 0.55), (root + 12, 0.45), (root + 16, 0.25)):
        f = midi(m)
        x += a * (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 6))
    x *= np.exp(-tt * 2.6) * (1 - np.exp(-tt * 250))
    return np.stack([x, np.roll(x, 53)], 1)


def sfx_track():
    out = np.zeros((N + SR * 2, 2))
    for name, at, peak_db, _ in SFX:
        if name == "whoosh":
            s = whoosh()
        elif name == "whoosh_rev":
            s = whoosh()[::-1]
        elif name == "impact_soft":
            s = impact_soft()
        elif name == "tick":
            s = tick()
        elif name == "chime":
            s = chime(74 if at < 15 else 72)      # D over G6, C over Cmaj9
        s = s / np.abs(s).max() * db(peak_db)
        i0 = int(at * SR)
        out[i0:i0 + len(s)] += s
    out = reverb(out[:N], 1.6, 0.22)
    return out


# ------------------------------------------------------------------- mix
def main():
    src, wd = sys.argv[1], sys.argv[2]
    os.makedirs(wd, exist_ok=True)
    write_wav(f"{wd}/music.wav", music())
    write_wav(f"{wd}/sfx.wav", sfx_track())
    # Voice: original narration, static +3.8 dB (-19.8 → -16 LUFS), 70 Hz rumble
    # high-pass, 60 ms fade on the source's hard cut at 19.0 s, padded for the tail.
    # Music: bed at -12 dB (≈ -31.6 LUFS after ducking, ~15 LU under the voice),
    # side-chain ducked a further few dB while she speaks. True-peak safety
    # limiter at -1.5 dBFS on the sum only.
    fc = (
        f"[0:a]aresample={SR},highpass=f=70,volume=3.8dB,"
        f"afade=t=out:st={SRC_DUR - 0.06:.3f}:d=0.06,apad=whole_dur={OUT_DUR},asplit=2[v][sc];"
        f"[1:a]volume=-12dB[m];"
        f"[m][sc]sidechaincompress=threshold=0.05:ratio=3:attack=25:release=400:knee=4[md];"
        f"[2:a]volume=0dB[fx];"
        f"[v][md][fx]amix=inputs=3:normalize=0:duration=first,"
        f"alimiter=limit=0.84:attack=2:release=60:level=disabled,"
        f"atrim=0:{OUT_DUR}[out]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", f"{wd}/music.wav", "-i", f"{wd}/sfx.wav",
                    "-filter_complex", fc, "-map", "[out]", "-ac", "2", "-ar", str(SR),
                    "-c:a", "pcm_f32le", f"{wd}/mix.wav"], check=True)
    print("audio ok")


if __name__ == "__main__":
    main()
