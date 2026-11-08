"""Splash story (Saturday, content system #55): the .MD logo as a title screen and a short message below
it, over a clean loop. Run from the repo root.
  python3 templates/splash.py --video assets/videos/pulse_144bpm_9x16_5s_v01.mp4 \
      --text "Water is also a drink." --out out.mp4 [--seconds 10]
Output 720x1280 (9:16) mp4. Logo and text are static and straight (never tilted or animated); the logo
is the master geometry from mdlib. Only the loop moves; it repeats until --seconds. Needs numpy,
Pillow, ffmpeg."""
import argparse, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mdlib

W, H = 720, 1280


def overlay(text):
    """Dark radial scrim + logo + label + message, as one transparent layer."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.47
    r = np.sqrt(((xx - cx) / (W * 0.75)) ** 2 + ((yy - cy) / (H * 0.36)) ** 2)
    a = np.clip(0.62 * (1 - r), 0, 0.62)
    layer = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (a * 255).astype(np.uint8)]), 'RGBA')

    lw = int(W * 0.62)
    mk = mdlib.logo_mask(lw)
    lx, ly = (W - lw) // 2, int(H * 0.33)
    white = Image.new('RGBA', mk.size, mdlib.FILL + (0,)); white.putalpha(mk)
    layer.alpha_composite(white, (lx, ly))

    d = ImageDraw.Draw(layer)
    f = mdlib.mono(int(W * 0.026)); label = "MARKDOWN RECORDS"; sp = 4
    tw = sum(d.textlength(ch, font=f) + sp for ch in label) - sp
    label_y = ly + mk.height + int(H * 0.022)
    mdlib.track(d, (W - tw) / 2, label_y, label, f, mdlib.GREY + (255,), sp)

    # Message: centred lines below the label, with a soft shadow. Stays above the bottom safe zone.
    top = label_y + int(H * 0.07)
    max_h = int(H * 0.87) - top
    n = len(text)
    start = int(W * (0.07 if n <= 32 else 0.06 if n <= 55 else 0.052))
    font, lines, lh = mdlib.wrap_fit(d, text, int(W * 0.8), max_h, start, int(W * 0.042), weight=700)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(shadow)
    for i, l in enumerate(lines):
        x = (W - d.textlength(l, font=font)) / 2; y = top + i * lh
        ds.text((x + 3, y + 3), l, font=font, fill=(0, 0, 0, 200))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(layer)
    for i, l in enumerate(lines):
        d.text(((W - d.textlength(l, font=font)) / 2, top + i * lh), l, font=font, fill=mdlib.FILL + (255,))
    return layer


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--video', required=True); a.add_argument('--text', required=True); a.add_argument('--out', required=True)
    a.add_argument('--seconds', type=float, default=10)
    r = a.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(r.out)), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ov = os.path.join(tmp, 'overlay.png')
        overlay(r.text.replace('\\n', '\n')).save(ov)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', r.video, '-i', ov,
                        '-filter_complex',
                        f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[v];[v][1:v]overlay=0:0',
                        '-t', f'{r.seconds}', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                        '-crf', '18', '-an', '-movflags', '+faststart', r.out], check=True)
    print('ok', r.out)


if __name__ == '__main__':
    main()
