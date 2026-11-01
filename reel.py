"""Turn rendered carousel slides into a 9:16 slideshow Reel (silent; music is added by Instagram via Eden).

python3 reel.py SLIDE_DIR OUT.mp4 ["Header text"]   (render slides with NO_SWIPE=1 first)
SLIDE_DIR holds slide_01.png, slide_02.png ... from carousel.py.
"""
import glob
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
CREAM = (250, 245, 236)
EDGE = (238, 228, 212)
INK = (30, 27, 24)
TRACK = (222, 210, 192)
COVER_S, SLIDE_S, END_S, FADE_S = 2.6, 3.3, 3.6, 0.28
CARD = 1000          # slide size on the reel canvas
CARD_Y = 460         # top of the slide card (keeps clear of Reels caption UI at the bottom)


def background():
    im = Image.new('RGB', (W, H), CREAM)
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).ellipse((-300, -200, W + 300, H + 200), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(200))
    return Image.composite(im, Image.new('RGB', (W, H), EDGE), mask)


def ease_out(t):
    return 1 - (1 - t) ** 3


def card(slide, scale):
    s = max(1, int(CARD * scale))
    im = slide.resize((s, s), Image.LANCZOS)
    m = Image.new('L', (s, s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), int(36 * scale), fill=255)
    return im, m


def frame(bg, slides, idx, t_in_slide, dur, nxt_alpha, total):
    f = bg.copy()
    if HEADER is not None:
        f.paste(HEADER, (0, 0), HEADER)
    d = ImageDraw.Draw(f)
    # story-style progress bars
    n = total
    gap, x0, x1, y = 10, 60, W - 60, 150
    bw = (x1 - x0 - gap * (n - 1)) / n
    for k in range(n):
        bx = x0 + k * (bw + gap)
        d.rounded_rectangle((bx, y, bx + bw, y + 8), 4, fill=TRACK)
        fill = 1.0 if k < idx else (min(1.0, t_in_slide / dur) if k == idx else 0.0)
        if fill > 0:
            d.rounded_rectangle((bx, y, bx + max(8, bw * fill), y + 8), 4, fill=INK)
    # pop-in then slow push
    pop = ease_out(min(1.0, t_in_slide / 0.32))
    scale = (0.93 + 0.07 * pop) * (1 + 0.025 * (t_in_slide / dur))
    im, m = card(slides[idx], scale)
    # soft shadow
    sh = Image.new('L', (W, H), 0)
    cx = (W - im.width) // 2
    cy = CARD_Y + (CARD - im.height) // 2
    ImageDraw.Draw(sh).rounded_rectangle((cx + 8, cy + 18, cx + im.width + 8, cy + im.height + 18), 40, fill=60)
    f.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    f.paste(im, (cx, cy), m)
    if nxt_alpha > 0 and idx + 1 < len(slides):
        im2, m2 = card(slides[idx + 1], 0.93)
        m2 = m2.point(lambda v: int(v * nxt_alpha))
        f.paste(im2, ((W - im2.width) // 2, CARD_Y + (CARD - im2.height) // 2), m2)
    return f


HEADER = None


def make_header(text):
    font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Poppins-Bold.ttf'), 58)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= 940:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    y = 215 + (210 - len(lines) * 70) // 2
    for ln in lines:
        d.text((W / 2 - d.textlength(ln, font=font) / 2, y), ln, font=font, fill=INK)
        y += 70
    return im


def build(slide_dir, out, title=None):
    global HEADER
    HEADER = make_header(title) if title else None
    paths = sorted(glob.glob(os.path.join(slide_dir, 'slide_*.png')))
    if not paths:
        paths = sorted(glob.glob(os.path.join(slide_dir, 'slide_*.jpg')))
    slides = [Image.open(p).convert('RGB') for p in paths]
    n = len(slides)
    durs = [COVER_S] + [SLIDE_S] * (n - 2) + [END_S] if n > 1 else [END_S]
    bg = background()
    total_s = sum(durs)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
           '-shortest', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i, dur in enumerate(durs):
        frames = int(round(dur * FPS))
        for fr in range(frames):
            t = fr / FPS
            a = 0.0
            if i + 1 < n and t > dur - FADE_S:
                a = (t - (dur - FADE_S)) / FADE_S
            p.stdin.write(frame(bg, slides, i, t, dur, a, n).tobytes())
    p.stdin.close()
    p.wait()
    print(f'{out}: {n} slides, {total_s:.1f}s')


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
