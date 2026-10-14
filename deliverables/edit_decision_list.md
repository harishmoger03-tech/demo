# Edit decision list — Raw_Cinematic_Broll_9x16.mp4

Generated from `scripts/edl.py` (the same data the renderer uses). Times are on the source timeline; the narration is never moved or retimed. Output: 1080×1920, 30 fps, 19.50 s (18.999 s of source + 0.5 s held-frame fade to black).

## Picture

| # | In → Out | Spoken phrase | What's on screen | Camera / animation | Transition in | Asset status |
|---|---|---|---|---|---|---|
| V1 | 00:00.00 → 00:03.20 | Har cheez ke liye alag-alag subscription lena kaafi expensive ho gaya hai. | Speaker (original footage) — Hook: the problem statement — keep her face and delivery on screen. | Slow eased push-in 1.00→1.06 toward the face | Open on speaker | Source footage |
| G1 | 00:03.20 → 00:07.68 | ChatGPT Plus, Claude, Gemini ya Canva Pro — sabka cost jodte-jodte | B-roll · motion graphic: AI-tool subscription cards → cost pile + ₹ meter — The list of separate AI subscriptions; then the cost piling up. | Cards slide in on each spoken name (3.28 / 4.24 / 4.80 / 5.52); at 6.25 they collapse into a stacked pile and a gold meter fills on 'cost jodte-jodte' (6.72–7.60) | Blur-dissolve into plate (0.30 s) | Generated locally (code), rendered |
| V2 | 00:07.68 → 00:09.50 | kaafi zyada ho jaata hai. … [unclear ~8.9–9.48] | Speaker (original footage) — Emotional emphasis — return to her expression. Cut sits on the 7.68 s inter-word gap. | Medium close-up punch-in 1.12, near-static drift | Cross-dissolve (0.20 s) | Source footage |
| G2 | 00:09.50 → 00:12.30 | ChatGPT aur Netflix, Prime aur Crunchyroll jaisi | B-roll · motion graphic: 2×2 subscription grid — The premium subscriptions she lists, shown as a 2×2 grid. | Tiles pop in on each name (9.52 / 10.40 / 10.96 / 11.44); slow group push 1.00→1.03 | Blur-dissolve into plate (0.30 s) | Generated locally (code), rendered |
| V3 | 00:12.30 → 00:14.74 | premium subscription wahaan discounted rates advertised hain. | Speaker (original footage) — Key claim delivered by the speaker; a gold price-tag-with-down-arrow icon marks 'discounted rates'. | Slow push-in 1.03→1.09; tag icon pops in at 13.44 over the dark wall slats (top-right) | Cross-dissolve (0.20 s) | Source footage |
| G3 | 00:14.74 → 00:16.86 | Isliye options ek jagah check karna aasaan ho jaata hai, | B-roll · motion graphic: options gathered into one panel, checked — 'Options in one place': scattered chips gather into one panel; ticks on 'check'. | Chips converge 14.80–15.55 into one gold-outlined panel; check marks cascade from 15.68 | Blur-dissolve into plate (0.25 s) | Generated locally (code), rendered |
| V4 | 00:16.86 → 00:19.50 | jahaan aapke paise bachte hain. … [unclear, cut off at 18.93] | Speaker (original footage) — Payoff line on the speaker. Last source frame is held 0.5 s and faded to black. | Slow push-in 1.02→1.08; fade to black 19.00→19.50 | Cross-dissolve (0.20 s) | Source footage |

## Captions (exact spoken words, romanised)

Gold = highlighted keyword. A time means the word turns gold as it is spoken (anchored to an ASR token); “phrase” means gold for the whole caption.

| # | In → Out | Caption | Highlights |
|---|---|---|---|
| 1 | 00:00.10 → 00:01.24 | Har cheez ke liye alag-alag | — |
| 2 | 00:01.24 → 00:02.12 | subscription lena | — |
| 3 | 00:02.12 → 00:03.20 | kaafi expensive ho gaya hai. | expensive @ 2.32 |
| 4 | 00:03.24 → 00:04.20 | ChatGPT Plus, | — |
| 5 | 00:04.20 → 00:05.48 | Claude, Gemini ya | — |
| 6 | 00:05.48 → 00:06.18 | Canva Pro — | — |
| 7 | 00:06.18 → 00:07.68 | sabka cost jodte-jodte | cost @ 6.72 |
| 8 | 00:07.68 → 00:08.72 | kaafi zyada ho jaata hai. | zyada (phrase) |
| 9 | 00:09.50 → 00:10.92 | ChatGPT aur Netflix, | — |
| 10 | 00:10.92 → 00:12.28 | Prime aur Crunchyroll jaisi | — |
| 11 | 00:12.30 → 00:13.42 | premium subscription wahaan | — |
| 12 | 00:13.42 → 00:14.74 | discounted rates advertised hain. | discounted @ 13.44, rates @ 13.84 |
| 13 | 00:14.76 → 00:15.64 | Isliye options ek jagah | ek (phrase), jagah (phrase) |
| 14 | 00:15.64 → 00:16.74 | check karna aasaan ho jaata hai, | aasaan (phrase) |
| 15 | 00:16.96 → 00:18.16 | jahaan aapke paise bachte hain. | paise (phrase), bachte (phrase) |

Not captioned (unclear in every ASR pass; audio untouched): 08.90–09.48 and 18.25–18.93 (the source cuts off mid-phrase).

## Sound

| Time | Cue | Peak | Purpose |
|---|---|---|---|
| 00:00.00 → 19.50 | Original narration (primary) | −1.5 dBTP ceiling | Static +3.8 dB (−19.8 → −16 LUFS), 70 Hz high-pass, no compression; 60 ms fade on the source's hard cut at 19.0 s |
| 00:00.00 → 19.50 | Synthesised music bed, 96 BPM: Am9 · Fmaj7 · Dm7 · E7sus → Fmaj7 · G6 · Fmaj7 · Cmaj9 | ≈ −31.6 LUFS after ducking | Minor colour while the cost adds up, resolving to C major on “paise bachte hain”. Pluck arpeggio enters with the first graphic (3.2 s). Side-chain ducked by the voice; fades in 0–0.6 s, out over the last 1 s |
| 00:02.30 | impact_soft | -27 dBFS | Low, soft thump under 'expensive' |
| 00:03.02 | whoosh | -26 dBFS | Into the AI-tools graphic (peaks on the 3.20 cut) |
| 00:03.28 | tick | -36 dBFS | Card 1 |
| 00:04.24 | tick | -37 dBFS | Card 2 |
| 00:04.80 | tick | -37 dBFS | Card 3 |
| 00:05.52 | tick | -37 dBFS | Card 4 |
| 00:09.32 | whoosh | -27 dBFS | Into the streaming grid |
| 00:13.44 | chime | -31 dBFS | Discount tag reveal |
| 00:14.50 | whoosh_rev | -29 dBFS | Gather into one place |
| 00:17.62 | chime | -34 dBFS | Soft resolve on 'paise bachte' |
