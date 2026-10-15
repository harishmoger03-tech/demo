"""Copy the auditioned SFX picks out of the Video-Skills pack, normalise each to a
common reference, and measure its peak (transient) offset for frame locking.

Reference: -16 LUFS integrated, capped so the true peak stays <= -1 dBTP. Files too
short for LUFS (< 0.4 s) are peak-normalised to -3 dBFS. Family levels from the
ue-sound-design skill (-12 / -6 / -5 dB) are then applied in the composition.

Usage: python3 -I scripts/prep_sfx.py <Sfx Pack dir> <out dir> <manifest.json>
"""
import json, os, subprocess, sys
import numpy as np

PICKS = {  # id: (folder/file, trim_seconds or None)
    "swipe_right":      ("Wooosh Transition/Swipe Right.wav", None),
    "swoosh_transition":("Wooosh Transition/Swoosh_Transition_Sound_Effect_mp3.mp3", None),
    "wind_wipe_high":   ("Wooosh Transition/Wind Wipe High.wav", None),
    "whoosh_18":        ("Woosh/Whoosh 18.wav", None),
    "eene_5_running_by":("Woosh/EEnE Whoosh 5 running by.wav", None),
    "mouth_pop":        ("SFX/Mouth Pop.wav", None),
    "ui_10":            ("Ui sfx/Ui 10.mp3", None),
    "ui_6":             ("Ui sfx/Ui 6.wav", None),
    "data_04":          ("SFX/Data 04.wav", 1.0),
    "camera_shutter":   ("SFX/Camera Shutter.mp3", None),
    "swish_boom":       ("Ui sfx/Swish Boom.mp3", None),
    "scifi_click_6":    ("Ui sfx/SCI FI CLICK 6.MP3", None),
    "success_bell":     ("Ui sfx/freesound_community-success_bell-6776.mp3", 2.0),
    "eene_6_jet_stop":  ("Woosh/EEnE Whoosh 6 jet stop.wav", None),
    "whoosh_back":      ("Wooosh Transition/Whoosh Back.wav", None),
    "bell_transition":  ("SFX/Bell Transition.wav", None),
    "impact_mid_bass":  ("SFX/Impact Mid Bass.wav", 2.5),
    "deep_impact":      ("SFX/Deep Impact.wav", 2.5),
    "impact_cinematic": ("SFX/Impact Cinematic.wav", 2.5),
}
SR = 48000


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace").stderr
    j = json.loads(r[r.rindex("{"):])
    return float(j["input_i"]), float(j["input_tp"])


def main():
    src, out, man = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    manifest = {}
    for sid, (rel, trim) in PICKS.items():
        p = os.path.join(src, rel)
        tmp = os.path.join(out, f"_{sid}.wav")
        af = f"atrim=0:{trim},afade=t=out:st={trim - 0.15}:d=0.15," if trim else ""
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-af", af + "aresample=48000", "-ac", "2",
                        "-c:a", "pcm_s16le", tmp], check=True)
        il, tp = measure(tmp)
        if il == float("-inf") or il < -70:
            x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", tmp, "-f", "f32le", "-"],
                                             capture_output=True).stdout, np.float32)
            gain = -3 - 20 * np.log10(np.abs(x).max() + 1e-9)
        else:
            gain = min(-16 - il, -1 - tp)
        dst = os.path.join(out, f"{sid}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={gain:.2f}dB",
                        "-c:a", "pcm_s16le", dst], check=True)
        os.remove(tmp)
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", dst, "-ac", "1", "-f", "f32le", "-"],
                                         capture_output=True).stdout, np.float32)
        hop = SR // 100
        env = np.sqrt((x[: len(x) // hop * hop].reshape(-1, hop) ** 2).mean(1))
        manifest[sid] = {"source": rel, "file": f"sfx/{sid}.wav", "duration": round(len(x) / SR, 3),
                         "peak": round(int(env.argmax()) / 100, 3), "gain_db": round(float(gain), 2),
                         "source_lufs": il, "trim": trim}
        print(f"{sid:20s} dur {len(x)/SR:5.2f}s peak@{env.argmax()/100:5.2f}s gain {gain:+6.1f} dB  <- {rel}")
    json.dump(manifest, open(man, "w"), indent=1)


if __name__ == "__main__":
    main()
