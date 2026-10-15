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

python3 -I scripts/foley.py . assets/sfx                          # work/foley.wav, work/mix.wav
python3 -I scripts/render.py . out/Raw_Editorial_master.mp4       # CRF 17 master, original audio copied

V=(-c:v libx264 -preset slow -crf 21 -profile:v high -pix_fmt yuv420p
   -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart)
ffmpeg -v error -y -i out/Raw_Editorial_master.mp4 -i work/mix.wav -map 0:v -map 1:a "${V[@]}" \
  -c:a aac -b:a 256k -ar 48000 -t 19.0 out/Raw_Editorial_Film.mp4
ffmpeg -v error -y -i out/Raw_Editorial_master.mp4 -i ../source/Raw.mp4 -map 0:v -map 1:a "${V[@]}" \
  -c:a copy out/Raw_Editorial_Film_no_foley.mp4
python3 -I scripts/qc_sync.py . out/Raw_Editorial_Film.mp4 | tee work/qc/sync_final.txt
