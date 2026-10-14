"""English transcription with token timestamps via NeMo Parakeet-TDT (sherpa-onnx, offline)."""
import sys, wave, json
import numpy as np, sherpa_onnx
mdir, wav, out = sys.argv[1], sys.argv[2], sys.argv[3]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{mdir}/encoder.int8.onnx", decoder=f"{mdir}/decoder.int8.onnx", joiner=f"{mdir}/joiner.int8.onnx",
    tokens=f"{mdir}/tokens.txt", model_type="nemo_transducer", num_threads=4)
with wave.open(wav) as w:
    sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
s = rec.create_stream(); s.accept_waveform(sr, x); rec.decode_stream(s)
r = s.result
print("TEXT:", r.text)
json.dump({"text": r.text, "tokens": list(r.tokens), "timestamps": list(r.timestamps),
           "durations": list(getattr(r, "durations", []) or [])}, open(out, "w"), indent=1)
