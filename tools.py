"""Helpers for the daily wojak run.

python3 tools.py render SPEC.json OUTDIR      -> renders PNG slides, then JPEGs into OUTDIR/jpg
python3 tools.py sheet  OUTDIR PREVIEW.jpg    -> contact sheet of all slides for a visual check
python3 tools.py reel   SPEC.json OUTDIR "Header"  -> slides without SWIPE + OUTDIR/reel.mp4 + OUTDIR/frames.jpg
python3 tools.py slots  YYYY-MM-DD           -> epoch ms for that day's 07:00 / 12:00 / 17:00 / 22:00 Manila slots
"""
import glob
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def render(spec, out):
    subprocess.run([sys.executable, os.path.join(HERE, 'carousel.py'), spec, out], check=True)
    os.makedirs(os.path.join(out, 'jpg'), exist_ok=True)
    for f in sorted(glob.glob(os.path.join(out, '*.png'))):
        o = os.path.join(out, 'jpg', os.path.basename(f).replace('.png', '.jpg'))
        Image.open(f).convert('RGB').save(o, quality=92)
    print('jpgs:', sorted(os.listdir(os.path.join(out, 'jpg'))))


def sheet(out, dest):
    fs = sorted(glob.glob(os.path.join(out, '*.png')))
    t = [Image.open(f).resize((440, 440)) for f in fs]
    rows = (len(t) + 3) // 4
    s = Image.new('RGB', (4 * 448, rows * 448), 'gray')
    for i, im in enumerate(t):
        s.paste(im, ((i % 4) * 448 + 4, (i // 4) * 448 + 4))
    s.save(dest, quality=85)
    print('sheet:', dest)


def reel(spec, out, header):
    env = dict(os.environ, NO_SWIPE='1')
    subprocess.run([sys.executable, os.path.join(HERE, 'carousel.py'), spec, out], check=True, env=env)
    mp4 = os.path.join(out, 'reel.mp4')
    subprocess.run([sys.executable, os.path.join(HERE, 'reel.py'), out, mp4, header], check=True)
    frames = []
    for t in (1, 6, 12):
        fp = os.path.join(out, f'frame_{t}.jpg')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t), '-i', mp4, '-frames:v', '1', fp], check=True)
        frames.append(Image.open(fp).resize((360, 640)))
    s = Image.new('RGB', (3 * 370, 650), 'gray')
    for i, im in enumerate(frames):
        s.paste(im, (i * 370 + 5, 5))
    s.save(os.path.join(out, 'frames.jpg'), quality=85)
    print('reel:', mp4, 'frames:', os.path.join(out, 'frames.jpg'))


def slots(day):
    from datetime import datetime, timedelta, timezone
    tz = timezone(timedelta(hours=8))
    y, m, d = map(int, day.split('-'))
    for hh, kind in ((7, 'REEL'), (12, 'CAROUSEL'), (17, 'REEL'), (22, 'REEL')):
        dt = datetime(y, m, d, hh, 0, tzinfo=tz)
        print(f'{day} {hh:02d}:00 {kind} {int(dt.timestamp() * 1000)}')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render':
        render(sys.argv[2], sys.argv[3])
    elif cmd == 'sheet':
        sheet(sys.argv[2], sys.argv[3])
    elif cmd == 'reel':
        reel(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'slots':
        slots(sys.argv[2])
