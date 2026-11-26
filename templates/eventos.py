"""Events story (Thursday, content system #54): 2 events over a clean loop. Run from the repo root.
  python3 templates/eventos.py --video loop.mp4 --text "FRI 27/11 · RADION\\nAmsterdam\\nDasha Rush · I-RO · Luke Slater\\n\\n..." \
      --out out.mp4 [--kicker "Events this week"] [--seconds 10]
--text: one block per event, separated by a blank line. Each block has 3 lines:
  1. date · venue  (always on one line: the size shrinks to fit; the same size for every event)
  2. city          (mono, grey)
  3. artists       (up to 3, ' · ' separated; wraps to 2 lines at most)
Output 720x1280 (9:16) mp4. Text and logo are static; only the loop moves. Needs numpy, Pillow, ffmpeg."""
import argparse, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import mdlib

W, H = 720, 1280
M = int(W * 0.08)
MAX_W = W - 2 * M


def blocks(text):
    out = []
    for b in text.replace('\\n', '\n').strip().split('\n\n'):
        lines = [l.strip() for l in b.strip().split('\n')]
        out.append((lines + ['', '', ''])[:3])
    return out


def fit_one_line(d, texts, start, minimum, weight):
    """Largest size where every text fits on a single line."""
    size = start
    while size > minimum and any(d.textlength(t, font=mdlib.sg(size, weight)) > MAX_W for t in texts):
        size -= 1
    return mdlib.sg(size, weight), size


def wrap(d, text, font):
    """Wrap on ' · ' first (keeps artist names whole), then on spaces."""
    parts = text.split(' · '); lines = []; cur = ''
    for p in parts:
        t = p if not cur else cur + ' · ' + p
        if d.textlength(t, font=font) <= MAX_W or not cur: cur = t
        else: lines.append(cur); cur = p
    lines.append(cur)
    return lines


def overlay(text, kicker):
    canvas = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(canvas)
    bs = blocks(text)
    top, bottom = int(H * 0.14), int(H * 0.13)
    lw = int(W * 0.20)
    sig_y = H - bottom - mdlib.signature_block(lw)[4]
    y0 = int(H * 0.27)

    f_head, s_head = fit_one_line(d, [b[0] for b in bs], int(W * 0.062), int(W * 0.036), 600)
    f_city = mdlib.mono(int(W * 0.03))
    # artists: one size for all events, at most 2 lines each
    s_art = int(W * 0.056)
    while s_art > int(W * 0.036) and any(len(wrap(d, b[2], mdlib.sg(s_art, 500))) > 2 for b in bs):
        s_art -= 1
    f_art = mdlib.sg(s_art, 500)

    if kicker:
        mdlib.track(d, M, y0 - int(W * 0.06), kicker.upper(), mdlib.mono(int(W * 0.022)), mdlib.GREY, 3)
    y = y0
    for i, (head, city, artists) in enumerate(bs):
        if i: y += int(H * 0.055)
        d.text((M, y), head, font=f_head, fill=mdlib.FILL); y += int(s_head * 1.18)
        if city:
            mdlib.track(d, M, y + int(s_head * 0.12), city.upper(), f_city, mdlib.GREY, 2); y += int(s_head * 0.12) + int(W * 0.03 * 2.0)
        for l in wrap(d, artists, f_art) if artists else []:
            d.text((M, y), l, font=f_art, fill=mdlib.FILL); y += int(s_art * 1.15)
    if y > sig_y - int(H * 0.03):
        print('warning: text reaches the signature area', file=sys.stderr)
    mdlib.draw_signature(canvas, M, bottom, lw)

    arr = np.asarray(canvas, dtype=np.float32)
    alpha = arr.max(axis=2) / 255.0
    rgb = np.where(alpha[..., None] > 0, np.clip(arr / np.maximum(alpha[..., None], 1e-3), 0, 255), 0)
    return Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), 'RGBA')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--video', required=True); a.add_argument('--text', required=True); a.add_argument('--out', required=True)
    a.add_argument('--kicker'); a.add_argument('--seconds', type=float, default=10)
    r = a.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(r.out)), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ov = os.path.join(tmp, 'overlay.png')
        overlay(r.text, r.kicker).save(ov)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', r.video, '-i', ov,
                        '-filter_complex',
                        f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[v];[v][1:v]overlay=0:0',
                        '-t', f'{r.seconds}', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                        '-crf', '16', '-an', '-movflags', '+faststart', r.out], check=True)
    print('ok', r.out)


if __name__ == '__main__':
    main()
