"""Export the EDL (markdown) and captions (SRT) from scripts/edl.py.

Usage: python3 -I scripts/export_docs.py <deliverables_dir>
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import CAPTIONS, SEGMENTS, SFX  # noqa: E402

KIND = {
    "speaker": "Speaker (original footage)",
    "mg_ai_stack": "B-roll · motion graphic: AI-tool subscription cards → cost pile + ₹ meter",
    "mg_stream_grid": "B-roll · motion graphic: 2×2 subscription grid",
    "mg_one_place": "B-roll · motion graphic: options gathered into one panel, checked",
}
TRANS = {None: "Open on speaker", "blur": "Blur-dissolve into plate", "dissolve": "Cross-dissolve"}


def ts(t, srt=False):
    m, s = divmod(t, 60)
    if srt:
        ms = int(round((s - int(s)) * 1000))
        return f"00:{int(m):02d}:{int(s):02d},{ms:03d}"
    return f"{int(m):02d}:{s:05.2f}"


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)

    with open(f"{out}/captions.srt", "w") as f:
        for i, (a, b, text, _) in enumerate(CAPTIONS, 1):
            f.write(f"{i}\n{ts(a, True)} --> {ts(b, True)}\n{text}\n\n")

    L = ["# Edit decision list — Raw_Cinematic_Broll_9x16.mp4", "",
         "Generated from `scripts/edl.py` (the same data the renderer uses). Times are on the source "
         "timeline; the narration is never moved or retimed. Output: 1080×1920, 30 fps, 19.50 s "
         "(18.999 s of source + 0.5 s held-frame fade to black).", "",
         "## Picture", "",
         "| # | In → Out | Spoken phrase | What's on screen | Camera / animation | Transition in | Asset status |",
         "|---|---|---|---|---|---|---|"]
    for s in SEGMENTS:
        tr = s["trans_in"]
        trs = TRANS[tr[0] if tr else None] + (f" ({tr[1]:.2f} s)" if tr else "")
        status = "Source footage" if s["kind"] == "speaker" else "Generated locally (code), rendered"
        L.append(f"| {s['id']} | {ts(s['start'])} → {ts(s['end'])} | {s['spoken']} | {KIND[s['kind']]} — "
                 f"{s['meaning']} | {s['move']} | {trs} | {status} |")

    L += ["", "## Captions (exact spoken words, romanised)", "",
          "Gold = highlighted keyword. A time means the word turns gold as it is spoken (anchored to an ASR "
          "token); “phrase” means gold for the whole caption.", "",
          "| # | In → Out | Caption | Highlights |", "|---|---|---|---|"]
    for i, (a, b, text, hl) in enumerate(CAPTIONS, 1):
        h = ", ".join(f"{w} @ {at:.2f}" if at is not None else f"{w} (phrase)" for w, at in hl) or "—"
        L.append(f"| {i} | {ts(a)} → {ts(b)} | {text} | {h} |")
    L += ["", "Not captioned (unclear in every ASR pass; audio untouched): 08.90–09.48 and 18.25–18.93 "
          "(the source cuts off mid-phrase).", "",
          "## Sound", "",
          "| Time | Cue | Peak | Purpose |", "|---|---|---|---|",
          "| 00:00.00 → 19.50 | Original narration (primary) | −1.5 dBTP ceiling | Static +3.8 dB (−19.8 → −16 LUFS), "
          "70 Hz high-pass, no compression; 60 ms fade on the source's hard cut at 19.0 s |",
          "| 00:00.00 → 19.50 | Synthesised music bed, 96 BPM: Am9 · Fmaj7 · Dm7 · E7sus → Fmaj7 · G6 · Fmaj7 · "
          "Cmaj9 | ≈ −31.6 LUFS after ducking | Minor colour while the cost adds up, resolving to C major on "
          "“paise bachte hain”. Pluck arpeggio enters with the first graphic (3.2 s). Side-chain ducked by the voice; "
          "fades in 0–0.6 s, out over the last 1 s |"]
    for name, at, peak, why in SFX:
        L.append(f"| {ts(at)} | {name} | {peak} dBFS | {why} |")
    open(f"{out}/edit_decision_list.md", "w").write("\n".join(L) + "\n")
    print("docs ok")


if __name__ == "__main__":
    main()
