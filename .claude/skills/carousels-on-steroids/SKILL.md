---
name: carousels-on-steroids
description: Make "carousels on steroids" — Instagram (or LinkedIn / TikTok photo-mode) carousels where every slide is a looping full-motion-graphics video AND the whole post is one continuous scene, so things cross the slide edges as people swipe. Interviews the user first (business, topic, goal, $0 vs AI assets via Higgsfield, real images, style reference), then builds one self-contained HTML file (canvas 2D, everything drawn in code) with a strip preview, swipe preview and record mode, checks every slide, and renders frame-exact MP4s. Use whenever someone wants an animated / motion / video / seamless / "on steroids" carousel for a brand, product, restaurant, launch or offer, wants a carousel like the Ember & Bun burger one, or says "make me a carousel" after installing this skill. Prefer the live-carousel skill only when the user asks for its specific styles (fx techniques, editorial bouncing ball, or animating finished slide images).
---

# Carousels on Steroids

One HTML file holds the whole carousel as a single wide world (N × 1080×1350). Every slide is a
viewport into that world, so smoke, embers, floating ingredients, a conveyor, a fuse… can cross the
edges and the swipe feels like one scene. Every frame is a pure function of time `t`, so loops are
exact, any frame can be rendered on demand, and MP4s come out frame-perfect (no screen recording).

`SKILL` below = the folder this file is in. The bundled example (`examples/ember-and-bun/`, the
"Ember & Bun — The Inferno" smash-burger launch) is the quality bar and the code you start from.

**Cost: $0 by default.** Everything is drawn in code with free tools (Node.js, Python, ffmpeg,
Google Chrome). Paid AI assets (Higgsfield or another connected AI tool) are used ONLY if the user
chooses them in the intake, and you always show the credit cost and wait for a yes before spending.

## 0. First use on a machine
Run `bash SKILL/scripts/setup.sh`. It checks Node 22+, Python 3, ffmpeg and Chrome/Chromium/Edge and
prints "All set". If something is missing, install it the free, official way (ask before anything that
needs a password), then re-run. `bash SKILL/scripts/selftest.sh` proves the whole pipeline.

## 1. Intake — interview the user BEFORE designing anything
**Which kind first.** If the user has not said, and the companion Carousel Kit (static style-sheet
carousels) is installed at `~/carousels-on-steroids/carousel/`, ask once: "A) motion graphics (every
slide moves, MP4s, one continuous scene) or B) style sheet (finished static slides in a ready-made
style sheet, your own photos, your own style-sheet image, optional mascot)?" For B, work inside
`~/carousels-on-steroids/` and follow `~/carousels-on-steroids/.claude/skills/carousel/SKILL.md`
instead of this file. For A, continue here.

Read `references/intake.md`. Ask the 8 questions in ONE message (numbered, each with its default in
brackets, skip any the user already answered): business · topic (theirs, or you find 3) · goal + CTA ·
budget ($0 or AI assets) · real images · style reference · format · words. Wait for the answers.
"Use the defaults" / "just go" is a valid answer. If they choose AI assets and the tool is not
connected, explain exactly how to connect it and wait. If they give a website or IG handle, look at it.
Write the answers into the project's `BRIEF.md` (template: `references/brief-template.md`).

## 2. Concept — one screen, one confirmation
Read `references/direction.md`. Fill the slide-plan table in `BRIEF.md`: for each slide its role, world
colour, hero technique, ONE big moment plus a second beat mid-loop, typography treatment, and the
seam bridge to the next slide. Write the on-slide copy. Show the plan + copy to the user and ask
"Build it?" once (skip if they said "just go"). The variety contract is non-negotiable:
- No two slides share a typography treatment or a hero technique; neighbours never share a background.
- Every slide: at least 3 things moving at all times, real easing (squash/stretch, overshoot, bounce),
  an impact moment (shake / flash / shockwave), and depth (back / mid / front layers at different speeds).
- Find ONE protagonist that belongs to the business (the burger being built, a sneaker, a phone, a
  cocktail, a key, a chart line) and let it travel or evolve across the slides.
- Never just recolour the example. Reuse its machinery, invent new moments.

## 3. Build
1. `python3 SKILL/scripts/new_carousel.py ~/carousels-on-steroids/motion/<short-name>` — copies the engine and
   the example into a new project and builds it (it renders immediately; you then replace the burger).
2. Read `references/engine-api.md` (file map, every helper, the rules), then the example files you are
   about to replace. Edit only the project files:
   - `src/00-project.js` brand, title, slide names, counters, loop length.
   - `src/02-hero.js` the protagonist, drawn in code (the example's burger shows layered, turntable-ready
     drawing) and/or real images from `assets/` via `drawImg()` (see `references/assets.md`).
   - `src/03-slides.js` one object per slide `{ build, back, mid, front, shakes, zooms, flashes }`, plus `SL`.
   - `src/04-world.js` world colours (`BGK`), seam bridges (`FLOAT`, `buildFG`), floor, far/near particles.
   Engine files (`01-core.js`, `05-render.js`, `06-app.js`, `template.html`, `style.css`) stay as they are.
3. `python3 build.py` → `carousel.html`. Open it; Strip / Single / Record / Export are built in.
4. Before delivering, `grep -niE "burger|patty|cheddar|ember|inferno|E&B" src/0[0234]*.js` must
   return nothing that belongs to the example (unless the user's brief really is a burger).

## 4. Check — look at it like a creative director
Read `references/qa.md`. Loop until it passes:
- `node tools/capture.mjs sheet renders/qa` → `contact-sheet.jpg`: rows = slides, columns = 0 / 25% /
  50% / 75% / last frame. Look at it. Last frame must flow into the first (seamless loop).
- `node tools/capture.mjs seams renders/qa` → every slide edge in close-up: things must cross.
- `node tools/capture.mjs frames renders/qa "3:2.25,5:1.6"` → each big moment, full size.
- Ask of every slide: "Would this stop someone scrolling?" If it is flat, has one thing moving, or the
  text just fades in, push it further and re-check. Check copy is spelled right and readable at phone size.

## 5. Render and deliver
`node tools/capture.mjs video renders all` → `renders/slide-01.mp4 …` (1080×1350, 30 fps, H.264
yuv420p, one exact loop each). Then tell the user, in plain words: the MP4 paths in posting order,
`carousel.html` (open it for them), a caption with the CTA, and that slide 1's first frame is the cover
(pick a strong cover frame in Instagram if slide 1 starts dark). Offer one round of tweaks.

## Rules that keep it correct (and why)
- **Pure function of t.** No `Math.random`, `Date`, timers or animation state. Use `hash(i, k)` for
  randomness and `pnoise(t, P, seed)` for noise. The renderer seeks frames out of order.
- **Loop exactly.** Free-running sinusoids use `OM(k)` (k whole cycles per loop); particle lives divide
  `LOOP`; bursts use wrapped age so tails continue across the loop; every slide returns to its frame-0
  state by `LOOP`. Keep big hits ≥ 0.8 s before the loop end.
- **Seams are persistent.** Objects that cross an edge must be there at every moment (floating items,
  smoke bands, continuous floor/fire), because people swipe at random times.
- **Instagram overlays.** Keep 72 px clear at the top-right (slide counter) and bottom-right (sound icon).
- **Text.** Big words ≥ 100 px, labels ≥ 20 px, strong contrast; typography always animates in
  (drop, burn, stack, fill, slam, roll, type) — never a plain fade.
- **Images.** Only use images the user owns or gave you. Keep `assets/` small (≤ 1600 px wide);
  `build.py` embeds them so the HTML stays one file (warns above 15 MB).
- **Spend.** $0 unless the user chose AI assets; preflight every paid call's cost and ask before spending.

## References
| File | Read it for |
| --- | --- |
| `references/intake.md` | the interview: questions, defaults, how each answer changes the build, topic finding |
| `references/direction.md` | slide roles, motion vocabulary, typography treatments, seam bridges, industry starters, copy |
| `references/engine-api.md` | file map, every helper with signatures, slide anatomy, layers, camera, world, rules |
| `references/assets.md` | $0 drawn-in-code, the user's own images, AI assets (Higgsfield recipe, costs, consent) |
| `references/qa.md` | capture commands, the checklist, common bugs and fixes, posting tips |
