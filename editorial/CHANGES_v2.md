# v2: final refinement (changes from v1)

v1 is preserved in `versions/v1/` (project, style, scripts and both MP4s). The text, timings, captions, scene order, length and **audio are unchanged**. v2 reuses the approved v1 audio streams bit-for-bit.

## Defects fixed (v1 timecodes)
- **3.20–7.68 s (receipt):** was a flat, mottled white sheet that read as a graphic.
- **8.90–12.30 s (tickets):** was on a coloured ochre sheet, a different look from the other inserts.
- **14.87–16.86 s (ledger):** was on flat charcoal, a third look.
- **All inserts:** were static, with no camera or lens character, so none read as footage.
- **Grain** (3.6) was too heavy; **bloom** (0.14) was barely visible.
- **Splits** only translated in and out.

## Changes
1. **One archival style for every insert.** Paper objects are filmed on the same grey table under one soft key light, with matching drop shadows. Each insert has a slow rostrum-camera push and drift (1.02→1.06) and slight lens softness.
2. **B&W grade** (bright, neutral: black 22 / white 246 / gamma 0.86) on the inserts only. The muted-red ink keeps a touch of colour, and the presenter stays clean colour (your choice).
3. **Grain toned down:** 3.6 → 2.2, finer (1.15 → 1.1 px), still fresh on every frame.
4. **Bloom added:** threshold 0.60, strength 0.26, radius 30 px. Soft highlights, with no haze, rings or coloured outlines.
5. **Animated splits:** 0.42 s soft entry and 0.34 s exit. The panel contents trail the panel edge with an 80 px parallax lag, the panel casts a soft shadow onto the presenter, and the rostrum push keeps moving while the split holds.
6. On-panel words (*cost*, *ek jagah*) are now cream to read on the table; their wording and timing are unchanged.

## Checks on the exported v2 files
- **Format:** 570 frames, 30 fps, 1080×1920, exactly 19.000 s.
- **Clean file:** decodes with no errors, black frames or freezes.
- **Audio:** packets identical to v1 (foley version) and to the source (no-foley version).
- **Text data:** captions, emphasis words, scenes and foley identical to v1.
- **Picture sync:** 0-frame lag on every presenter shot and both split panels (r ≥ 0.99).
- **Motion:** stepped through every split entry and exit, the cut into the tickets and the dissolve out frame by frame. Full 5 fps watch-through. v1/v2 grain and bloom compared at full resolution.
- **Not possible here:** real-time playback and listening.
