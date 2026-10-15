"""Per-frame presenter matte for text-behind-subject occlusion.

Model: U^2-Net human segmentation (rembg release asset u2net_human_seg.onnx),
run offline with onnxruntime. Writes one 8-bit PNG per programme frame at half
resolution (540x960) into <out_dir>/m_%04d.png.

Usage: python3 -I scripts/masks.py <source.mp4> <model.onnx> <out_dir> [fps]
"""
import os, subprocess, sys
import numpy as np
import onnxruntime as ort
from PIL import Image

src, model, out = sys.argv[1], sys.argv[2], sys.argv[3]
fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
os.makedirs(out, exist_ok=True)
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
inp = sess.get_inputs()[0].name
W, H = 1080, 1920
mean = np.array([0.485, 0.456, 0.406], np.float32); std = np.array([0.229, 0.224, 0.225], np.float32)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={fps}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     stdout=subprocess.PIPE)
n = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    fr = Image.frombuffer("RGB", (W, H), buf)
    x = (np.asarray(fr.resize((320, 320), Image.BILINEAR), np.float32) / 255 - mean) / std
    y = sess.run(None, {inp: x.transpose(2, 0, 1)[None]})[0][0, 0]
    y = (y - y.min()) / (y.max() - y.min() + 1e-6)
    Image.fromarray((y * 255).astype(np.uint8)).resize((540, 960), Image.BICUBIC).save(f"{out}/m_{n:04d}.png")
    n += 1
    if n % 50 == 0:
        print(n, flush=True)
print("masks", n)
