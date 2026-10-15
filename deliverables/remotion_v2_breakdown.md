# Raw.mp4 v2 (Remotion) — analysis and cue sheet

Status: **analysis only, nothing placed yet** (protocol B1 step 1). Source: `source/Raw.mp4`, 1080×1920, 30 fps, 18.999 s, plus a 0.5 s held-frame fade. Narration timings come from `deliverables/transcript.md` and are unchanged.

Frame numbers are at 30 fps (`f` = frame). **MOVEMENT** → whoosh, **EVENT** → texture, **BUILD** → riser or hit.

## Structure

| Seg | Time (frame) | Roll | Spoken | Picture plan (inspiration board #) |
|---|---|---|---|---|
| V1 | 0.00–3.20 (0–96) | A | "Har cheez ke liye alag-alag subscription lena kaafi expensive ho gaya hai." | Hook: speaker stays on screen. Slow push-in 1.00→1.06. |
| G1 | 3.20–7.68 (96–230) | B | "ChatGPT Plus, Claude, Gemini ya Canva Pro — sabka cost jodte-jodte" | Speaker darkened and blurred behind. Glass app tiles glow in on each name (#49, #50, #7). At 6.25 they stack, then a neon cost curve draws upward (#2, #9, #36). No numbers, so no invented prices. |
| V2 | 7.68–9.50 (230–285) | A | "kaafi zyada ho jaata hai." [unclear ~8.9–9.48] | Punch-in 1.12 on her reaction. |
| G2 | 9.50–12.30 (285–369) | B | "ChatGPT aur Netflix, Prime aur Crunchyroll jaisi" | 2×2 blue-glow tile grid (#41, #49), one tile per name, slow group push. |
| V3 | 12.30–14.74 (369–442) | A | "premium subscription wahaan discounted rates advertised hain." | Speaker, plus an on-screen pill at 13.44: a glowing toggle or price pill with a falling curve (#24, #52, #45), over a darkened/blurred band. |
| G3 | 14.74–16.86 (442–506) | B | "Isliye options ek jagah check karna aasaan ho jaata hai," | Orbit hub (#59): scattered tiles converge into one centre, then a glowing checklist ticks down (#64). |
| V4 | 16.86–19.50 (506–585) | A | "jahaan aapke paise bachte hain." [unclear 18.25–18.93] | Payoff on the speaker, slow push-in, fade to black. |

## Cue sheet

| Time (frame) | What happens on screen | Class | Candidate from `Sfx Pack` (shortlist to audition) |
|---|---|---|---|
| ~1.60 (48) | Fastest point of the slow V1 push-in | MOVEMENT (slow drift) | Wind Whoosh Mid · Wind Wipe High · MA Air Transitions 05 |
| 2.32 (70) | "expensive" keyword caption pop | EVENT (text pop) | UI Popup · Mouth Pop · soft UI pop |
| 3.20 (96) | Hook → body: A→B blur transition | MOVEMENT (scene transition) + BUILD | Whoosh: Swipe Right · Whoosh 21 · EEnE 4 long. Hit: Bass Impact · Deep Impact |
| 3.28 / 4.24 / 4.80 / 5.52 (98 / 127 / 144 / 166) | Tiles 1–4 glow in on each name | EVENT (assets in sequence, one per element) | Ui 1–10 · SCI FI CLICK 4/5/6 |
| 6.25 (188) | Tiles slide into a stack | MOVEMENT (slide) | EEnE Whoosh 1/2/3 · Whoosh 18 · MA Punchy |
| 6.72 → 7.60 (202 → 228) | Cost curve draws upward (pulses at 7.36, 7.60) | EVENT (write-out) | Digital Data Counters · Data 04 · magiaz gear noise |
| 7.68 (230) | B→A cut to her reaction | EVENT (clip transition) or BUILD | Camera Shutter · Camera Flash 3/4 |
| 9.50 (285) | A→B transition into grid | MOVEMENT (scene transition) + BUILD | Whoosh 6 · Wind Flash · Swoosh Transition |
| 9.52 / 10.40 / 10.96 / 11.44 (286 / 312 / 329 / 343) | Grid tiles pop on each name | EVENT (UI pop, one per element) | Ui 1–10 · UI Popup |
| 9.5 → 12.3 | Slow group push | MOVEMENT (slow drift) | Wind Whoosh Mid · Air Transitions 04 |
| 12.30 (369) | B→A cut | EVENT (clip transition) | Camera Flash 3/4 |
| 13.44 (403) | On-screen pill reveal ("discounted rates") | EVENT (new UI revealed) — **proposed loudest moment** | Swish Boom · Impact Cinematic · SCI FI CLICK |
| 14.74 (442) | A→B transition into orbit | MOVEMENT (scene transition) + BUILD | Whoosh Back (swells into the cut) · Drum Woosh |
| 14.80 → 15.55 (444 → 467) | Tiles converge into the hub | MOVEMENT (slide) | EEnE 5 running by · Data_Whoosh |
| 15.68 → 16.24 (470 → 487) | 7 ticks cascade | EVENT (sequence, one per element) | SCI FI CLICK 4/5/6 · Click · Ui 6 |
| 16.86 (506) | B→A to the payoff | EVENT or BUILD | Camera Shutter · Bell Transition |
| 17.62 (529) | "paise bachte" — conclusion | EVENT (conclusion) | success bell · AirplaneChime · iPhone Notification |
| 19.00–19.50 (570–585) | Fade to black | — | (silence or tail) |

## Gaps against the rules

- **No risers in the library.** The rules want at least 2 sharp bass + 2 metallic risers. The only build-ups are Whoosh Back (0.94 s), Bell Transition (1.12 s) and EEnE 6 jet stop (1.59 s).
- **"~5 s after the hook".** The hook ends at 3.20, and the next segment changes are at 7.68 and 9.50. My reading is that the first riser resolves on the 3.20 hook-to-body cut.
- **Music.** It goes under A-roll only. A-roll here is just four short blocks (3.2 s, 1.8 s, 2.4 s, 2.6 s), so a bed cutting in and out would sound choppy. Joseph supplies tracks, and none is in the repo.
- **Captions.** The brief (sans + script fonts, placement, colour, animation) isn't in `docs/brief/`.
- **AI B-roll.** Higgsfield has 0 credits (free plan), and its API servers are blocked by this environment's network policy.
- **Loudness.** The library ranges from about −34 to 0 LUFS, so every file gets normalised to a common reference before the brief's dB levels are applied.
