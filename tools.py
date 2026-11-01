"""Helpers for the daily wojak run.

python3 tools.py render SPEC.json OUTDIR      -> renders PNG slides, then JPEGs into OUTDIR/jpg
python3 tools.py sheet  OUTDIR PREVIEW.jpg    -> contact sheet of all slides for a visual check
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


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render':
        render(sys.argv[2], sys.argv[3])
    elif cmd == 'sheet':
        sheet(sys.argv[2], sys.argv[3])
