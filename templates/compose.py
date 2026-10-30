"""Compose text + logo signature over a clean background (no text/logo in the background).
Run from the repo root.

Single piece:
  python3 templates/compose.py --format feed --bg assets/backgrounds/bg_glass_floor_4x5_v01.png \
      --text "Dark pressure.\nPrecise sound." --out /tmp/out.png [--kicker "Statement"] [--cta "markdownrecords.com"] [--no-signature]
Several pieces (carousel, 3-story set): a JSON list of the same fields:
  python3 templates/compose.py --spec spec.json
  [{"format":"story","bg":"...","text":"...","out":"..."}, ...]
Formats: feed (1080x1350, 4:5), story (1080x1920, 9:16). Text auto-fits; use \n for forced breaks.
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import mdlib

def render(p):
    size = mdlib.SIZES[p['format']]
    bg = mdlib.cover(Image.open(p['bg']).convert('RGB'), size)
    mdlib.draw_piece(bg, p['format'], p['text'].replace('\\n', '\n'), p.get('kicker'), p.get('cta'),
                     signature=not p.get('no_signature', False))
    os.makedirs(os.path.dirname(os.path.abspath(p['out'])), exist_ok=True)
    bg.save(p['out']); print('ok', p['out'], bg.size)

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--spec'); a.add_argument('--format', choices=list(mdlib.SIZES)); a.add_argument('--bg')
    a.add_argument('--text'); a.add_argument('--out'); a.add_argument('--kicker'); a.add_argument('--cta')
    a.add_argument('--no-signature', action='store_true')
    r = a.parse_args()
    if r.spec: items = json.load(open(r.spec))
    else:
        if not (r.format and r.bg and r.text and r.out): a.error('need --format --bg --text --out (or --spec)')
        items = [dict(format=r.format, bg=r.bg, text=r.text, out=r.out, kicker=r.kicker, cta=r.cta, no_signature=r.no_signature)]
    for it in items: render(it)
