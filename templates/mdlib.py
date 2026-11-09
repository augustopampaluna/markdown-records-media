"""Shared helpers for MARKDOWN templates. Pure Pillow. Run scripts from the repo root."""
from PIL import Image, ImageDraw, ImageFont

FILL = (244, 245, 246)
GREY = (150, 152, 156)
SIZES = {"feed": (1080, 1350), "story": (1080, 1920)}  # reel overlay uses story size
# logo geometry (.MD master, 852x354 box starting at 192,450) - do not alter
def _bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],
                    (1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]))
    return out
POLYS = [[(192,678),(312,678),(312,804),(192,804)],
         [(328,450),(514,630),(514,804),(487,804),(328,641)],
         [(699,450),(699,804),(691,804),(518,629)],
         [(725,450),(875,450)]+_bez((875,450),(968.3,450),(1044,529.2),(1044,627))
         +_bez((1044,627),(1044,724.8),(968.3,804),(875,804))+[(725,804)]]

def sg(size, weight=600):
    f = ImageFont.truetype('brand/fonts/SpaceGrotesk[wght].ttf', size)
    f.set_variation_by_axes([weight]); return f

def mono(size, medium=True):
    return ImageFont.truetype('brand/fonts/IBMPlexMono-%s.ttf' % ('Medium' if medium else 'Regular'), size)

def cover(img, size):
    """Resize + center-crop to exactly size (no distortion)."""
    W, H = size; w, h = img.size
    s = max(W / w, H / h)
    img = img.resize((round(w*s), round(h*s)), Image.LANCZOS)
    l, t = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((l, t, l + W, t + H))

def logo_mask(width):
    SS = 4; lh = int(width * 354 / 852)
    mk = Image.new('L', (width*SS, lh*SS), 0); md = ImageDraw.Draw(mk); k = width*SS/852
    for p in POLYS: md.polygon([((x-192)*k, (y-450)*k) for x, y in p], fill=255)
    return mk.resize((width, lh), Image.LANCZOS)

def track(d, x, y, text, font, fill, sp):
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + sp

def wrap_fit(d, text, max_w, max_h, start, min_size, weight=600, line_gap=1.12):
    """Largest font size (start..min_size) where the wrapped text fits max_w x max_h.
    Explicit '\n' in text are respected. Returns (font, lines, line_h)."""
    size = start
    while True:
        f = sg(size, weight); lines = []
        for para in text.split('\n'):
            cur = ''
            for w in para.split():
                t = (cur + ' ' + w).strip()
                if d.textlength(t, font=f) <= max_w or not cur: cur = t
                else: lines.append(cur); cur = w
            lines.append(cur)
        lh = int(size * line_gap)
        ok = all(d.textlength(l, font=f) <= max_w for l in lines) and lh * len(lines) <= max_h
        if ok or size <= min_size: return f, lines, lh
        size -= 4

def scrim(canvas, y_top, y_bot, sig_y):
    """Soft dark gradients so text/logo stay readable over bright light lines (background stays visible)."""
    import numpy as np
    W, H = canvas.size
    a = np.zeros((H, W), dtype=np.float32)
    # left-to-right fade behind the text block
    yy = np.arange(H)[:, None]; xx = np.arange(W)[None, :]
    band = np.clip(1 - np.abs(yy - (y_top + y_bot) / 2) / ((y_bot - y_top) / 2 + 120), 0, 1)
    a = np.maximum(a, 0.50 * band * np.clip(1 - xx / (W * 0.95), 0.25, 1))
    # bottom fade behind the signature
    a = np.maximum(a, 0.65 * np.clip((yy - (sig_y - 160)) / 220, 0, 1) * np.ones((1, W)))
    base = np.asarray(canvas, dtype=np.float32) * (1 - a[..., None])
    canvas.paste(Image.fromarray(base.astype('uint8')))

SIG_LABEL = "MARKDOWN RECORDS"

def signature_block(lw):
    """Layout of the brand signature for a logo lw px wide: .MD logo with SIG_LABEL below it, the label
    spanning the logo width (tracking adjusted). Returns (mask, font, spacing, gap, block_height)."""
    mk = logo_mask(lw); n = len(SIG_LABEL)
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    nat = lambda f: sum(probe.textlength(ch, font=f) for ch in SIG_LABEL)
    size = int(lw * 0.15)
    while size > 8 and nat(mono(size)) + (n - 1) * size * 0.12 > lw: size -= 1
    f = mono(size); sp = (lw - nat(f)) / (n - 1)
    gap = int(mk.height * 0.20)
    asc, desc = f.getmetrics()
    return mk, f, sp, gap, mk.height + gap + asc

def draw_signature(canvas, right, bottom, lw, fill=FILL):
    """Brand signature at the bottom-right corner: logo, and SIG_LABEL below it at the logo's width.
    right/bottom are the margins to the canvas edge. Returns the top y of the block."""
    W, H = canvas.size
    mk, f, sp, gap, bh = signature_block(lw)
    x, y = W - right - lw, H - bottom - bh
    logo = Image.new('RGBA', mk.size, fill + (0,)); logo.putalpha(mk)
    canvas.paste(logo, (x, y), logo)
    track(ImageDraw.Draw(canvas), x, y + mk.height + gap, SIG_LABEL, f, fill, sp)
    return y

def draw_piece(canvas, fmt, text, kicker=None, cta=None, signature=True, size_hint=None):
    """Draw text block, optional kicker (series, mono) and CTA (mono) and the brand signature
    (bottom-right, see draw_signature).
    Safe zones: story keeps top 14% and bottom 13% free of text/logo (Instagram UI)."""
    W, H = canvas.size; d = ImageDraw.Draw(canvas)
    m = int(W * 0.08)
    if fmt == 'story':
        top, bottom = int(H * 0.14), int(H * 0.13); y0 = int(H * 0.30)
    else:
        top, bottom = int(H * 0.07), int(H * 0.07); y0 = int(H * 0.20)
    lw = int(W * 0.20)
    sig_y = H - bottom - signature_block(lw)[4]
    max_h = sig_y - y0 - int(H * 0.06) - (int(H*0.07) if cta else 0)
    start = size_hint or int(W * (0.105 if len(text) <= 40 else 0.078))
    f, lines, line_h = wrap_fit(d, text, W - 2*m - int(W*0.03), max_h, start, int(W * 0.05))
    scrim(canvas, y0 - int(W*0.08), y0 + line_h * len(lines) + (int(H*0.08) if cta else 0), sig_y)
    d = ImageDraw.Draw(canvas)
    y = y0
    if kicker:
        track(d, m, y - int(W*0.06), kicker.upper(), mono(int(W*0.022)), GREY, 3)
    for l in lines:
        d.text((m, y), l, font=f, fill=FILL); y += line_h
    if cta:
        track(d, m, y + int(H*0.035), cta, mono(int(W*0.026)), FILL, 3)
    if signature:
        draw_signature(canvas, m, bottom, lw)
    return canvas
