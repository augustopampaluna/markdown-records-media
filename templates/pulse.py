"""Beat-locked edge pulse over a still (parametrized version of pulse_beat.py). Run from the repo root.
  python3 templates/pulse.py --bg <image> --out <mp4> [--bpm 144] [--seconds 5] [--fps 24]
Output 720x1280 (9:16). No text, no logo (add them with overlay_video.py). Needs numpy, Pillow, ffmpeg."""
import argparse, subprocess, numpy as np
from PIL import Image, ImageFilter
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import mdlib
a_ = argparse.ArgumentParser()
a_.add_argument('--bg', required=True); a_.add_argument('--out', required=True)
a_.add_argument('--bpm', type=float, default=144); a_.add_argument('--seconds', type=float, default=5); a_.add_argument('--fps', type=int, default=24)
r = a_.parse_args()
im = mdlib.cover(Image.open(r.bg).convert('RGB'), (720, 1280))
a = np.asarray(im, dtype=np.float32) / 255
L = a.mean(axis=2)
mask = np.clip((L - 0.45) / 0.35, 0, 1)
bloom = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)), dtype=np.float32) / 255
mask3, bloom3 = mask[..., None], bloom[..., None]
beat = r.fps * 60 / r.bpm; N = int(round(r.seconds * r.fps))
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '720x1280', '-r', str(r.fps),
                      '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', r.out], stdin=subprocess.PIPE)
for n in range(N):
    env = np.exp(-5.0 * ((n % beat) / beat)); dim = 0.55
    out = a * (1 - mask3 * (1 - dim) * (1 - env)) + bloom3 * 0.30 * env
    p.stdin.write((np.clip(out, 0, 1) * 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print('ok', r.out)
