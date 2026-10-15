# Raw.mp4: editorial film cut

An editorial cut of `source/Raw.mp4` made with the **editorial-film-edit** skill. The speech, clip order, length (19.00 s), 1080×1920 format and original sound are unchanged.

| File | What it is |
|---|---|
| `out/Raw_Editorial_Film.mp4` | **Final.** H.264 CRF 21, 30 fps, original voice plus soft paper/print foley (AAC 48 kHz) |
| `out/Raw_Editorial_Film_no_foley.mp4` | Same picture, with the original audio stream copied bit-for-bit |
| `style.json` | Portable look: palette, three font roles, grain, bloom, grades, type motion, split, captions. No timecodes or media. |
| `project.json` | This video only: scenes, inserts, emphasis words, captions, foley cues |
| `scripts/render.py` | Frame renderer: picture → words → presenter cut-out → bloom → grain → captions |
| `scripts/masks.py` | Per-frame presenter matte (U²-Net human segmentation, offline) → `work/masks/` |
| `scripts/foley.py` | Foley stem, mixed under the untouched original sound → `work/mix.wav` |
| `scripts/qc_sync.py` | Picture-sync check against the source |
| `build.sh` | Rebuilds everything |

## What the edit does

| Time (s) | Scene | Treatment |
|---|---|---|
| 0.00–3.20 | Presenter | Soft, bright colour; slow push. Editorial serif *alag-alag* → *expensive.* sit **behind her crown** via the presenter matte; *expensive.* enters in 15 fps steps. |
| 3.20–7.68 | **Split** (presenter + receipt) | Insert slides in from the right (0.40 s) and reframes her to the left panel. A thermal receipt prints CHATGPT PLUS / CLAUDE / GEMINI / CANVA PRO on each spoken name (stepped typewriter). Then a rule, TOTAL and a muted-red ink ring, as the cost adds up. *cost* appears in serif on the panel. |
| 7.68–8.90 | Presenter | Split slides out (0.34 s); **ZYADA** in heavy sans behind her head. |
| 8.90–12.30 | Full-screen collage | Starts exactly on the source's first baked cut (frame 267). Ochre paper with muted-red registration marks; four cream ticket stubs (ChatGPT, Netflix, Prime, Crunchyroll) drop in stop-motion at 10 fps on each spoken name. |
| 12.30–14.87 | Presenter | Short dissolve back. *discounted* behind her crown, with a muted-red rule drawing under it. |
| 14.87–16.86 | **Split** (presenter + ledger) | Enters exactly on the second baked cut (frame 446). An index card lists all seven services; red ticks land one by one on "check karna". *ek jagah* appears on the panel. |
| 16.86–19.00 | Presenter | Split slides out; *paise bachte* behind her crown to the end. |

- **Captions.** Phrase captions in the sans role, above the grain, sit low and clear of the face. Their line breaks are fixed per phrase, and they glide with the presenter panel during splits.
- **Uncaptioned spans.** Two short unclear spans stay uncaptioned (8.90–9.48 and 18.25–18.93); the audio there is untouched.
- **Type roles.** Exactly three families: **Inter** (sans), **Instrument Serif** italic (editorial serif) and **IBM Plex Mono** (mono).
- **Film finish.** The grain is fresh and monochrome on every frame, weighted to the midtones. The bloom is soft (threshold 0.68). Paper texture stays static on its sheet.
- **Grade.** The presenter is graded clean colour; the inserts are bright, neutral B&W with ochre and muted-red accents only.

## Sources and rights

- **Footage:** `source/Raw.mp4`, supplied by the user. All collage elements (receipt, tickets, ledger, paper, marks) are drawn in code for this project; there is no third-party imagery.
- **Fonts:**
  - Instrument Serif: SIL OFL, `assets/fonts/LICENSE-InstrumentSerif-OFL.txt`, via @fontsource.
  - IBM Plex Mono: SIL OFL, `assets/fonts/LICENSE-IBMPlexMono-OFL.txt`, via @fontsource.
  - Inter: SIL OFL, from the system package.
- **Foley:** four files from the user's Video-Skills `Sfx Pack/SFX`, copied to `assets/sfx/`. They are paper shake, click, mechanical and lighter click, all at −19 to −22 dB, about 18 LU under the voice.
- **Presenter matte:** `u2net_human_seg.onnx` from the rembg GitHub release (not bundled; `build.sh` downloads it when the masks need regenerating).

## Rebuild

```bash
./build.sh            # foley + render + delivery encodes (uses existing work/masks)
MASKS=1 ./build.sh    # also regenerate the presenter masks (downloads the 176 MB model)
```

Needs ffmpeg, Python 3 with numpy and Pillow; onnxruntime only for masks.
