"""Transcribe source narration with Whisper large-v3-turbo (sherpa-onnx, offline).

sherpa-onnx drops Whisper byte-level tokens that are not valid UTF-8 on their own
(every Devanagari character spans several byte tokens), so we load a vocabulary in
which each token is spelled as "{hex bytes}" and reassemble the UTF-8 here.
Usage: python3 transcribe_whisper.py <model_dir> <wav16k> <out.json> [language]"""
import sys, wave, json, re
import numpy as np, sherpa_onnx

mdir, wav, out = sys.argv[1], sys.argv[2], sys.argv[3]
lang = sys.argv[4] if len(sys.argv) > 4 else ""
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{mdir}/turbo-encoder.int8.onnx", decoder=f"{mdir}/turbo-decoder.int8.onnx",
    tokens=f"{mdir}/turbo-tokens-hex.txt", language=lang, task="transcribe", num_threads=4)
with wave.open(wav) as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

# sherpa-onnx caps output at ~6 tokens per second of input; trailing silence raises
# the cap so Devanagari (≈3 byte tokens per character) is not cut short.
TAIL = 18.0

def run(chunk):
    s = rec.create_stream(); s.accept_waveform(sr, chunk); rec.decode_stream(s)
    raw = "".join(s.result.tokens)
    return bytes.fromhex("".join(re.findall(r"\{([0-9a-f]*)\}", raw))).decode("utf-8", "replace").strip()

# Whisper can stop early on dense speech, so also decode each phrase between the
# natural pauses found with silencedetect (passed as "a-b,c-d" in argv[5]).
res = {"language": lang, "full": run(x), "chunks": []}
print("FULL:", res["full"])
for span in (sys.argv[5].split(",") if len(sys.argv) > 5 else []):
    a, b = map(float, span.split("-"))
    seg = np.concatenate([np.zeros(int(0.3 * sr), np.float32), x[int(a * sr):int(b * sr)], np.zeros(int(TAIL * sr), np.float32)])
    t = run(seg); res["chunks"].append({"start": a, "end": b, "text": t}); print(f"[{a:5.2f}-{b:5.2f}] {t}")
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
