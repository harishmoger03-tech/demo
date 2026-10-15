#!/usr/bin/env bash
# Builds the bundled example carousel, renders a contact sheet and slide 1 as an MP4, and checks the results.
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$HOME/carousels-on-steroids/motion/_selftest}"
bash "$SK/scripts/setup.sh"
python3 "$SK/scripts/new_carousel.py" "$OUT" --force
node "$OUT/tools/capture.mjs" sheet "$OUT/renders/qa"
node "$OUT/tools/capture.mjs" video "$OUT/renders" "1"
test -s "$OUT/renders/qa/contact-sheet.jpg" && test -s "$OUT/renders/slide-01.mp4"
frames=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of default=nw=1:nk=1 "$OUT/renders/slide-01.mp4")
echo "slide-01.mp4: $frames frames"
[ "$frames" -gt 100 ] && echo "SELFTEST PASSED: $OUT/carousel.html"
