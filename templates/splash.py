"""Splash story (Saturday, content system #55): the .MD logo as a title screen and a short message as a
"splash" next to it, tilted and pulsing gently, over a clean loop. Run from the repo root.
  python3 templates/splash.py --video assets/videos/pulse_144bpm_9x16_5s_v01.mp4 \
      --text "Water is also a drink." --out out.mp4 [--seconds 10] [--bpm 144] [--angle 12]
Output 720x1280 (9:16) mp4. The logo is the master geometry from mdlib (static, never animated or
deformed); only the message moves. The loop repeats until --seconds. Needs numpy, Pillow, ffmpeg."""
import argparse, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mdlib

W, H = 720, 1280
FPS = 24


def static_layer():
    """Dark radial scrim + logo + label. Returns (RGBA layer, logo box)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.47
    r = np.sqrt(((xx - cx) / (W * 0.75)) ** 2 + ((yy - cy) / (H * 0.36)) ** 2)
    a = np.clip(0.62 * (1 - r), 0, 0.62)
    layer = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (a * 255).astype(np.uint8)]), 'RGBA')

    lw = int(W * 0.62)
    mk = mdlib.logo_mask(lw)
    lx, ly = (W - lw) // 2, int(H * 0.34)
    white = Image.new('RGBA', mk.size, mdlib.FILL + (0,)); white.putalpha(mk)
    layer.alpha_composite(white, (lx, ly))

    d = ImageDraw.Draw(layer)
    f = mdlib.mono(int(W * 0.026)); label = "MARKDOWN RECORDS"; sp = 4
    mdlib.track(d, lx + int(lw * 0.01), ly + mk.height + int(H * 0.022), label, f, mdlib.GREY + (255,), sp)
    return layer, (lx, ly, lx + lw, ly + mk.height)


def message_layer(text):
    """The message, centred lines, with a soft shadow, on a transparent canvas (2x for clean scaling)."""
    S = 2
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    max_w = int(W * (0.78 if len(text) <= 32 else 0.66)) * S
    n = len(text)
    start = int(W * (0.078 if n <= 28 else 0.064 if n <= 55 else 0.054)) * S
    f, lines, lh = mdlib.wrap_fit(probe, text, max_w, int(H * 0.2) * S, start, int(W * 0.042) * S, weight=700)
    tw = int(max(probe.textlength(l, font=f) for l in lines))
    pad = 24 * S
    cw, ch = tw + 2 * pad, lh * len(lines) + 2 * pad
    shadow = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    txt = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(txt)
    for i, l in enumerate(lines):
        x = pad + (tw - probe.textlength(l, font=f)) / 2; y = pad + i * lh
        ds.text((x + 3 * S, y + 3 * S), l, font=f, fill=(0, 0, 0, 200))
        dt.text((x, y), l, font=f, fill=mdlib.FILL + (255,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3 * S))
    shadow.alpha_composite(txt)
    return shadow.resize((cw // S, ch // S), Image.LANCZOS)


def place(msg, logo_box, angle, scale_max):
    """Centre of the splash: below-right of the logo, clamped so the tilted, scaled block stays inside
    the side margins and out of the bottom safe zone."""
    lx0, ly0, lx1, ly1 = logo_box
    big = msg.resize((int(msg.width * scale_max), int(msg.height * scale_max))).rotate(angle, expand=True)
    m = int(W * 0.06)
    cx = min(lx1 - W * 0.06, W - m - big.width / 2)      # bites the logo's lower-right corner
    cx = max(cx, m + big.width / 2)
    cy = ly1 + H * 0.05 + big.height * 0.3
    cy = min(cy, H * 0.87 - big.height / 2)
    return cx, cy


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--video', required=True); a.add_argument('--text', required=True); a.add_argument('--out', required=True)
    a.add_argument('--seconds', type=float, default=10); a.add_argument('--bpm', type=float, default=144)
    a.add_argument('--angle', type=float, default=12, help='degrees, counter-clockwise (rises to the right)')
    r = a.parse_args()

    base, logo_box = static_layer()
    msg = message_layer(r.text.replace('\\n', '\n'))
    amp = 0.06
    cx, cy = place(msg, logo_box, r.angle, 1 + amp)
    period = 2 * 60 / r.bpm                              # one pulse every 2 beats
    n = int(round(r.seconds * FPS))

    os.makedirs(os.path.dirname(os.path.abspath(r.out)), exist_ok=True)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', r.video,
                          '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-filter_complex',
                          f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}[v];'
                          '[v][1:v]overlay=0:0:shortest=1',
                          '-t', f'{r.seconds}', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                          '-crf', '18', '-an', '-movflags', '+faststart', r.out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        s = 1 + amp * (0.5 + 0.5 * math.cos(2 * math.pi * t / period))      # bounce like a title splash
        m = msg.resize((max(1, int(msg.width * s)), max(1, int(msg.height * s))), Image.BICUBIC)
        m = m.rotate(r.angle, resample=Image.BICUBIC, expand=True)
        frame = base.copy()
        frame.alpha_composite(m, (int(cx - m.width / 2), int(cy - m.height / 2)))
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit('ffmpeg failed')
    print('ok', r.out)


if __name__ == '__main__':
    main()
