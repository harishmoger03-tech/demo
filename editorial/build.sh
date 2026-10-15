#!/usr/bin/env bash
# Rebuild the editorial cut of Raw.mp4. See README.md.
set -euo pipefail
cd "$(dirname "$0")"
MODEL=${MODEL:-/root/models/rembg/u2net_human_seg.onnx}

if [[ "${MASKS:-0}" == 1 ]]; then
  [[ -f "$MODEL" ]] || { mkdir -p "$(dirname "$MODEL")"; curl -sSL -o "$MODEL" \
    https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx; }
  python3 -I scripts/masks.py ../source/Raw.mp4 "$MODEL" work/masks 30
fi

# python3 -I scripts/foley.py . assets/sfx   # v1 mix (approved; not regenerated in v2)
python3 -I scripts/render.py . out/Raw_Editorial_master.mp4       # CRF 17 master, original audio copied

V=(-c:v libx264 -preset slow -crf 21 -profile:v high -pix_fmt yuv420p
   -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart)
# v2: picture-only revision -> keep the approved v1 audio streams bit-for-bit
ffmpeg -v error -y -i out/Raw_Editorial_master.mp4 -i versions/v1/out/Raw_Editorial_Film_v1.mp4 -map 0:v -map 1:a "${V[@]}" \
  -c:a copy -t 19.0 out/Raw_Editorial_Film_v2.mp4
ffmpeg -v error -y -i out/Raw_Editorial_master.mp4 -i ../source/Raw.mp4 -map 0:v -map 1:a "${V[@]}" \
  -c:a copy out/Raw_Editorial_Film_v2_no_foley.mp4
python3 -I scripts/qc_sync.py . out/Raw_Editorial_Film_v2.mp4 | tee work/qc/sync_final.txt
