import os, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

W, H = 1080, 1080
F = os.environ.get('WOJAK_FONT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts') + '/')
BOLD, MED, REG = F + 'Poppins-Bold.ttf', F + 'Poppins-Medium.ttf', F + 'Poppins-Regular.ttf'
CREAM = (250, 245, 236)
EDGE = (238, 228, 212)
INK = (30, 27, 24)
MUTED = (120, 110, 98)
YEL = (255, 208, 80)
RED = (214, 72, 60)
GRN = (60, 150, 90)
HERE = os.path.dirname(os.path.abspath(__file__))
LIST = [os.path.join(HERE, l.strip()) for l in open(os.path.join(HERE, 'list.txt')) if l.strip()]
HANDLE = '@dailytipsonself'


def font(p, s):
    return ImageFont.truetype(p, s)


def bg():
    im = Image.new('RGB', (W, H), CREAM)
    # soft vignette toward warmer edges
    mask = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-260, -200, W + 260, H + 200), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    edge = Image.new('RGB', (W, H), EDGE)
    return Image.composite(im, edge, mask)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, text, f, y, maxw, color=INK, gap=1.18, cx=W // 2, hl=None):
    """Centered wrapped text. Words wrapped in *stars* get a yellow marker."""
    lines = wrap(d, text.replace('*', ''), f, maxw)
    marked = set()
    if hl is None:
        import re
        for m in re.findall(r'\*([^*]+)\*', text):
            marked.update(m.split())
    lh = int(f.size * gap)
    for ln in lines:
        lw = d.textlength(ln, font=f)
        x = cx - lw / 2
        for w in ln.split(' '):
            ww = d.textlength(w, font=f)
            if w in marked:
                d.rounded_rectangle((x - 8, y + f.size * 0.22, x + ww + 8, y + f.size * 1.18), 10, fill=YEL)
            d.text((x, y), w, font=f, fill=color)
            x += ww + d.textlength(' ', font=f)
        y += lh
    return y


def is_boxed(im):
    g = im.convert('L')
    w, h = g.size
    return g.getpixel((2, 2)) < 235 and g.getpixel((w - 3, 2)) < 235


def place(canvas, idx, box, boxed=None):
    """Fit image #idx into box (x0,y0,x1,y1). White backgrounds melt into the cream via multiply."""
    x0, y0, x1, y1 = box
    im = Image.open(LIST[idx]).convert('RGB')
    bx = is_boxed(im) if boxed is None else boxed
    if not bx:
        g = ImageChops.invert(im.convert('L')).point(lambda v: 255 if v > 18 else 0)
        bb = g.getbbox()
        if bb:
            m = 6
            im = im.crop((max(0, bb[0]-m), max(0, bb[1]-m), min(im.width, bb[2]+m), min(im.height, bb[3]+m)))
    pad = 0 if not bx else 16
    bw, bh = x1 - x0 - 2 * pad, y1 - y0 - 2 * pad
    s = min(bw / im.width, bh / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    px = x0 + (x1 - x0 - im.width) // 2
    py = y0 + (y1 - y0 - im.height) // 2
    if bx:
        sh = Image.new('L', canvas.size, 0)
        ImageDraw.Draw(sh).rounded_rectangle((px + 10, py + 14, px + im.width + 10, py + im.height + 14), 26, fill=70)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        canvas.paste((0, 0, 0), (0, 0), sh)
        m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 26, fill=255)
        canvas.paste(im, (px, py), m)
        ImageDraw.Draw(canvas).rounded_rectangle((px, py, px + im.width, py + im.height), 26, outline=INK, width=5)
    else:
        region = canvas.crop((px, py, px + im.width, py + im.height))
        canvas.paste(ImageChops.multiply(region, im), (px, py))
    return (px, py, px + im.width, py + im.height)


def footer(c, d, n, total):
    f = font(MED, 30)
    d.text((70, H - 78), HANDLE, font=f, fill=MUTED)
    t = f'{n}/{total}'
    d.text((W - 70 - d.textlength(t, font=f), H - 78), t, font=f, fill=MUTED)


def swipe(d):
    f = font(BOLD, 32)
    t = 'SWIPE  >'
    tw = d.textlength(t, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 30, H - 96, W / 2 + tw / 2 + 30, H - 40), 28, fill=INK)
    d.text((W / 2 - tw / 2, H - 92), t, font=f, fill=CREAM)


def slide_cover(s, n, total):
    c = bg(); d = ImageDraw.Draw(c)
    if s.get('kicker'):
        f = font(BOLD, 34)
        tw = d.textlength(s['kicker'], font=f)
        d.rounded_rectangle((W / 2 - tw / 2 - 26, 60, W / 2 + tw / 2 + 26, 120), 30, fill=INK)
        d.text((W / 2 - tw / 2, 66), s['kicker'], font=f, fill=CREAM)
    y = text_block(d, s['title'], font(BOLD, int(s.get('size', 92) * 0.85)), 140, 960)
    imgs = s['img'] if isinstance(s['img'], list) else [s['img']]
    top, bot = y + 30, H - 150
    if len(imgs) == 1:
        place(c, imgs[0], (90, top, W - 90, bot))
    else:
        place(c, imgs[0], (50, top, W // 2 - 50, bot))
        place(c, imgs[1], (W // 2 + 50, top, W - 50, bot))
        f = font(BOLD, 110)
        my = (top + bot) // 2 - 70
        d.text((W // 2 - d.textlength('>', font=f) / 2, my), '>', font=f, fill=RED)
    if not os.environ.get('NO_SWIPE'):
        swipe(d)
    return c


def slide_single(s, n, total):
    c = bg(); d = ImageDraw.Draw(c)
    y = 60
    if s.get('label'):
        f = font(BOLD, 36)
        d.text((W / 2 - d.textlength(s['label'], font=f) / 2, y), s['label'], font=f, fill=RED)
        y += 54
    if s.get('level'):
        lv, mx = s['level']
        sw, gap = 110, 14
        x0 = W / 2 - (mx * sw + (mx - 1) * gap) / 2
        for k in range(mx):
            d.rounded_rectangle((x0 + k * (sw + gap), y, x0 + k * (sw + gap) + sw, y + 16), 8,
                                fill=GRN if k < lv else (226, 214, 196))
        y += 36
    y = text_block(d, s['head'], font(BOLD, int(s.get('size', 70) * 0.85)), y, 960)
    sub = s.get('sub')
    subf = font(MED, 40)
    sub_h = 0
    if sub:
        sub_h = len(wrap(d, sub.replace('*', ''), subf, 900)) * int(40 * 1.3) + 30 + (58 if s.get('fix') else 0)
    top, bot = y + 20, H - 110 - sub_h
    r = place(c, s['img'], (110, top, W - 110, bot))
    if s.get('stamp'):
        f = font(BOLD, 64)
        t = s['stamp']
        tw = int(d.textlength(t, font=f))
        st = Image.new('RGBA', (tw + 80, 120), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((4, 4, tw + 76, 116), 18, outline=RED + (235,), width=9)
        sd.text((40, 14), t, font=f, fill=RED + (235,))
        st = st.rotate(14, expand=True, resample=Image.BICUBIC)
        c.paste(st, (min(r[2] - int(st.width * 0.3), W - st.width - 24), max(r[1] - 30, 0)), st)
    if sub:
        yy = r[3] + 24
        if s.get('fix'):
            f = font(BOLD, 34)
            t = s.get('badge', 'FIX')
            tw = d.textlength(t, font=f)
            d.rounded_rectangle((W / 2 - tw / 2 - 20, yy - 6, W / 2 + tw / 2 + 20, yy + 46), 22, fill=INK if s.get('badge') else GRN)
            d.text((W / 2 - tw / 2, yy - 2), t, font=f, fill=CREAM)
            yy += 64
        text_block(d, sub, subf, yy, 900, color=INK, gap=1.3)
    footer(c, d, n, total)
    return c


def slide_split(s, n, total):
    c = bg(); d = ImageDraw.Draw(c)
    y = text_block(d, s['head'], font(BOLD, 56), 60, 960)
    top = y + 20
    d.line((W // 2, top + 10, W // 2, H - 150), fill=(205, 192, 172), width=4)
    tagf = font(BOLD, 34)
    for i, (lab, col) in enumerate([(s.get('ltag', 'AVERAGE GUY'), GRN if s.get('flip') else RED), (s.get('rtag', 'GROWING GUY'), RED if s.get('flip') else GRN)]):
        cx = W // 4 if i == 0 else 3 * W // 4
        tw = d.textlength(lab, font=tagf)
        d.rounded_rectangle((cx - tw / 2 - 20, top, cx + tw / 2 + 20, top + 54), 26, fill=col)
        d.text((cx - tw / 2, top + 5), lab, font=tagf, fill=CREAM)
    imgtop, imgbot = top + 80, H - 250
    a = place(c, s['l'][0], (40, imgtop, W // 2 - 40, imgbot))
    b = place(c, s['r'][0], (W // 2 + 40, imgtop, W - 40, imgbot))
    f = font(MED, 38)
    ty = max(a[3], b[3]) + 30
    text_block(d, s['l'][1], f, ty, W // 2 - 80, cx=W // 4, gap=1.28)
    text_block(d, s['r'][1], f, ty, W // 2 - 80, cx=3 * W // 4, gap=1.28)
    footer(c, d, n, total)
    return c


def slide_end(s, n, total):
    c = bg(); d = ImageDraw.Draw(c)
    y = text_block(d, s['head'], font(BOLD, int(s.get('size', 74) * 0.88)), 70, 960)
    if s.get('sub'):
        y = text_block(d, s['sub'], font(MED, 38), y + 10, 920, color=MUTED, gap=1.3)
    top, bot = y + 20, H - 220
    place(c, s['img'], (140, top, W - 140, bot))
    f = font(BOLD, 40)
    t = 'Follow ' + HANDLE
    tw = d.textlength(t, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 200, W / 2 + tw / 2 + 40, H - 124), 38, fill=INK)
    d.text((W / 2 - tw / 2, H - 192), t, font=f, fill=CREAM)
    d.text((W / 2 - d.textlength('for more short and actionable advice', font=font(MED, 32)) / 2, H - 104),
           'for more short and actionable advice', font=font(MED, 32), fill=MUTED)
    return c


KINDS = {'cover': slide_cover, 'single': slide_single, 'split': slide_split, 'end': slide_end}


def slide_duo(s, n, total):
    """Two numbered items per slide: wojak left, number + headline + line right."""
    c = bg(); d = ImageDraw.Draw(c)
    y0 = 60
    if s.get('head'):
        y0 = text_block(d, s['head'], font(BOLD, 50), 56, 960) + 10
    rows = s['items']
    area = (H - 110) - y0
    rh = area // len(rows)
    numf, hf, sf = font(BOLD, 64), font(BOLD, 46), font(MED, 34)
    for i, it in enumerate(rows):
        top = y0 + i * rh
        if i:
            d.line((80, top, W - 80, top), fill=(220, 208, 190), width=3)
        place(c, it['img'], (50, top + 24, 420, top + rh - 24))
        tx = 460
        ty = top + 40
        d.text((tx, ty), it['n'], font=numf, fill=RED)
        ty += 84
        for ln in wrap(d, it['head'], hf, W - tx - 60):
            d.text((tx, ty), ln, font=hf, fill=INK); ty += 56
        ty += 8
        for ln in wrap(d, it['sub'], sf, W - tx - 60):
            d.text((tx, ty), ln, font=sf, fill=MUTED); ty += 44
    footer(c, d, n, total)
    return c


def slide_grid(s, n, total):
    """2x2 grid of wojaks, each with a short label."""
    c = bg(); d = ImageDraw.Draw(c)
    y = text_block(d, s['head'], font(BOLD, 56), 56, 960) + 16
    bot = H - 110
    cw, ch = (W - 120) // 2, (bot - y) // 2
    lf = font(BOLD, 36)
    for i, (img, lab) in enumerate(s['cells']):
        x0 = 50 + (i % 2) * (cw + 20); y0 = y + (i // 2) * ch
        d.rounded_rectangle((x0, y0 + 6, x0 + cw, y0 + ch - 14), 28, fill=(244, 236, 222))
        lines = wrap(d, lab, lf, cw - 40)
        lh = len(lines) * 44
        place(c, img, (x0 + 20, y0 + 22, x0 + cw - 20, y0 + ch - 34 - lh))
        ty = y0 + ch - 26 - lh
        for ln in lines:
            d.text((x0 + cw / 2 - d.textlength(ln, font=lf) / 2, ty), ln, font=lf, fill=INK); ty += 44
    footer(c, d, n, total)
    return c


KINDS.update({'duo': slide_duo, 'grid': slide_grid})


def slide_statement(s, n, total):
    """Dark full-text slide for the twist."""
    c = Image.new('RGB', (W, H), INK); d = ImageDraw.Draw(c)
    pre = s.get('pre')
    f = font(BOLD, s.get('size', 96))
    lines = wrap(d, s['text'].replace('*', ''), f, 920)
    lh = int(f.size * 1.2)
    total_h = len(lines) * lh + (90 if pre else 0)
    y = (H - total_h) // 2
    if pre:
        pf = font(MED, 44)
        d.text((W / 2 - d.textlength(pre, font=pf) / 2, y), pre, font=pf, fill=(200, 190, 175))
        y += 90
    import re
    marked = set()
    for m in re.findall(r'\*([^*]+)\*', s['text']):
        marked.update(m.split())
    for ln in lines:
        x = W / 2 - d.textlength(ln, font=f) / 2
        for w in ln.split(' '):
            ww = d.textlength(w, font=f)
            d.text((x, y), w, font=f, fill=YEL if w in marked else CREAM)
            x += ww + d.textlength(' ', font=f)
        y += lh
    fm = font(MED, 30)
    d.text((70, H - 78), HANDLE, font=fm, fill=(160, 150, 136))
    t = f'{n}/{total}'
    d.text((W - 70 - d.textlength(t, font=fm), H - 78), t, font=fm, fill=(160, 150, 136))
    return c


KINDS.update({'statement': slide_statement})

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    total = len(spec)
    for i, s in enumerate(spec, 1):
        im = KINDS[s['kind']](s, i, total)
        im.save(f'{out}/slide_{i:02d}.png')
    print('done', total)
