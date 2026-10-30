"""Burn static text + logo signature over a clean video (clip from pulse.py or a Krea video). Run from the repo root.
  python3 templates/overlay_video.py --video in.mp4 --text "RAW SIGNALS." --out out.mp4 [--kicker "RAW SIGNALS"] [--no-signature]
The logo is static (never animated or deformed). Output keeps the input size (scaled to 720x1280 if different). Needs Pillow, ffmpeg."""
import argparse, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import mdlib
a = argparse.ArgumentParser()
a.add_argument('--video', required=True); a.add_argument('--text', required=True); a.add_argument('--out', required=True)
a.add_argument('--kicker'); a.add_argument('--no-signature', action='store_true')
r = a.parse_args()
W, H = 720, 1280
# build overlay by drawing on a transparent-ready RGBA: draw on black then derive alpha via difference-free approach:
# draw on a copy with text/logo, and on a plain black copy, alpha = max channel diff -> simpler: render on white-on-transparent.
import numpy as np
black = Image.new('RGB', (W, H), (0, 0, 0))
mdlib.draw_piece_overlay = None
canvas = black.copy()
# no scrim for video (keeps the clip untouched except text/logo)
orig = mdlib.scrim; mdlib.scrim = lambda *x, **k: None
mdlib.draw_piece(canvas, 'story', r.text.replace('\\n', '\n'), r.kicker, None, signature=not r.no_signature)
mdlib.scrim = orig
arr = np.asarray(canvas, dtype=np.float32)
alpha = arr.max(axis=2) / 255.0
rgba = np.dstack([np.where(alpha[..., None] > 0, np.clip(arr / np.maximum(alpha[..., None], 1e-3), 0, 255), 0), alpha * 255]).astype(np.uint8)
ov = '/tmp/_md_overlay.png'; Image.fromarray(rgba, 'RGBA').save(ov)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', r.video, '-i', ov, '-filter_complex',
                '[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[v];[v][1:v]overlay=0:0',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-an', r.out], check=True)
print('ok', r.out)
