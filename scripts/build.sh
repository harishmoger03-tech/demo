#!/usr/bin/env bash
# Reproducible end-to-end build of Raw_Cinematic_Broll_9x16.mp4.
# Requires: ffmpeg 6, python3 with numpy + pillow (+ sherpa-onnx and the two
# models in $MODELS only for the optional transcription step).
set -euo pipefail
cd "$(dirname "$0")/.."

SRC=source/Raw.mp4
OUT=Raw_Cinematic_Broll_9x16.mp4
MODELS=${MODELS:-/root/models}

mkdir -p work/audio work/transcript work/qc deliverables

if [[ "${TRANSCRIBE:-0}" == 1 ]]; then
  ffmpeg -v error -y -i "$SRC" -vn -ac 1 -ar 16000 work/audio/raw_16k_mono.wav
  python3 scripts/transcribe_whisper.py "$MODELS/sherpa-onnx-whisper-turbo" work/audio/raw_16k_mono.wav \
    work/transcript/whisper_hi.json hi "0-8.80,8.80-16.85,16.85-19.0,0-3.1,3.1-6.4,6.4-8.8,8.8-12.3,12.3-14.7,14.7-16.85"
  python3 scripts/transcribe_parakeet.py "$MODELS/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8" \
    work/audio/raw_16k_mono.wav work/transcript/parakeet.json
fi

python3 -I scripts/audio.py "$SRC" work/audio                       # music, sfx, mix
python3 -I scripts/render.py "$SRC" work/audio/mix.wav "$OUT"       # picture + mux
python3 -I scripts/export_docs.py deliverables                      # EDL + SRT
python3 -I scripts/qc_sync.py "$SRC" "$OUT" | tee work/qc/sync.txt  # sync QC
ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,sample_rate,channels \
  -of default=nw=1 "$OUT" | tee work/qc/ffprobe.txt
