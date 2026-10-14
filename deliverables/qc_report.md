# Quality-control report — Raw_Cinematic_Broll_9x16.mp4

All checks ran on the exported file. Raw outputs are in `work/qc/`.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | File exists, decodes cleanly | ✅ Pass | Full `ffmpeg -v error -f null` decode: 0 errors |
| 2 | Resolution / frame rate / format | ✅ Pass | H.264 High, 1080×1920, 30/1 CFR, 585 frames, yuv420p (BT.709, TV range); AAC-LC 48 kHz stereo, 256 kb/s; moov before mdat (faststart); 19.50 s (`work/qc/ffprobe.txt`) |
| 3 | Narration complete and in sync | ✅ Pass | Output audio vs source cross-correlation: +1.9 to +2.0 ms lag in every third of the clip (AAC priming, well under one frame), r = 0.92–0.94 with music mixed in. Picture: motion-signature cross-correlation gives a **0-frame** lag on all four speaker segments (`work/qc/sync.txt`). The voice is never stretched, cut or replaced. |
| 4 | No words cut by transitions | ✅ Pass | Every cut sits on a measured pause or inter-word dip (3.20, 7.68, 9.50, 12.30, 14.74, 16.86 s). Transitions are picture-only; the voice track is continuous. |
| 5 | Captions match the narration | ✅ Pass, with 2 flagged gaps | 15 phrase captions, words taken from cross-checked Whisper (Hindi) + Parakeet (English names) decodes. Two short spans that no ASR pass could resolve are deliberately **not captioned** (08.90–09.48, and 18.25–18.93 where the source cuts off mid-phrase). |
| 6 | B-roll in / out points | ✅ Pass | Every graphic beat lands on its spoken word (card and tile entries ±0.06 s of the ASR token); speaker returns for the hook, "kaafi zyada", the "discounted rates" claim and the payoff line. |
| 7 | No black frames, gaps, missing assets or corruption | ✅ Pass | `blackdetect`: only 19.33–19.47 s (the intended fade to black). `freezedetect`: none. All sprites are generated in-process; no external files referenced. Build is deterministic (two runs, identical MD5). |
| 8 | Consistent audio levels | ✅ Pass | Integrated −15.9 LUFS, true peak −1.5 dBTP, LRA 4.4 LU (source voice LRA 4.2: dynamics preserved; static gain only, limiter on the sum as a safety ceiling) |
| 9 | Music / SFX never obscure speech | ✅ Pass | Ducked music ≈ −31.6 LUFS, about 15.6 LU under the voice. SFX peaks −26 to −37 dBFS. No SFX lands on a stressed syllable except the deliberate soft thump under "expensive". |
| 10 | Intentional ending | ✅ Pass | Narration's hard cut at 19.00 s gets a 60 ms fade (no click). The last frame holds and fades to black over 0.5 s while the music resolves on C major. |
| — | Full watch-through | ✅ Done | Whole video reviewed at 4 fps (78 frames): `work/qc/watch_00-06s.jpg`, `watch_06-13s.jpg`, `watch_13-19s.jpg`. Fixed before the final render: messy card pile text, caption plate grazing the mic mount on punch-ins, clumped chips. |

## Known limitations
- **Duration is 19.50 s, not 19.00 s.** A 0.5 s held-frame fade was added because the source audio stops mid-word at 19.0 s. Nothing in the original was shortened or retimed.
- **No real stock or AI-generated footage.** See `asset_manifest.md` for why.
- **Hindi word timings are phrase-level.** English words (brand names, "expensive", "discounted rates") are anchored to ASR token timestamps; Hindi word boundaries come from the energy envelope. So captions are phrase-synchronised, and karaoke-style highlighting is used only on token-timed words.
