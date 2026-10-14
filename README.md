# Raw.mp4 → Raw_Cinematic_Broll_9x16.mp4

A cinematic 9:16 edit of `source/Raw.mp4` (Hinglish narration about stacking AI and streaming subscriptions) with motion-graphic B-roll, captions, a grade, and a synthesised score.

| Deliverable | Path |
|---|---|
| Final video (1080×1920, 30 fps, H.264/AAC, 19.5 s) | `Raw_Cinematic_Broll_9x16.mp4` |
| Transcript | `deliverables/transcript.md` (raw ASR: `work/transcript/`) |
| Timestamped edit decision list | `deliverables/edit_decision_list.md` |
| Captions | `deliverables/captions.srt` (also burned in) |
| Asset manifest + unavailable services | `deliverables/asset_manifest.md` |
| QC report | `deliverables/qc_report.md` (raw: `work/qc/`) |
| Editing scripts | `scripts/` (`edl.py` is the timeline; `build.sh` rebuilds everything) |

Rebuild: `scripts/build.sh` (add `TRANSCRIBE=1` to redo ASR; needs the sherpa-onnx models in `$MODELS`).
Intermediate WAVs are git-ignored; the build regenerates them.
