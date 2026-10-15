# Ultimate Editors — short-form video edits

This repo holds short-form talking-head edits (source footage, scripts, renders, deliverables).
Edits are built in **Remotion** going forward; `scripts/` holds the earlier Python/FFmpeg pipeline
used for `Raw_Cinematic_Broll_9x16.mp4`.

## Always load before working on an edit

- `.claude/skills/ue-short-form-editing/` — captions, hooks, animations, on-screen overlays.
- `.claude/skills/ue-sound-design/` — Joseph's sound library, placement, levels, three-pass workflow, track rules.

## Non-negotiables

- The speaker's original voice and words are never changed, retimed or replaced. Voice is king.
- Analyze first: give a timecoded breakdown, ask 2–3 questions, and wait before placing sound.
- Sound passes in order: whooshes → textures → risers & hits → music (only after approval).
- Music only under the talking head (-19 dB), never under animations or graphics.
- One sound family per Remotion track (`WHOOSHES`, `TEXTURES`, `RISERS`, `HITS`, `MUSIC`); mute original audio, never delete it.
- Use only the Ultimate Editors SFX library unless told otherwise; never generate a sound the library has.
- Never invent the editing brief's specifics; if it is missing from `docs/brief/`, ask for it.
- Claude cannot hear audio: "audition" by measured properties and say which variation was picked and why.
