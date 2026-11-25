#!/usr/bin/env python3
"""Prepare the pre-wedding photos for the site.

Usage:
    python3 scripts/build_photos.py "/path/to/folder of photos" [--order a.jpg,b.jpg,...]

What it does, for every .jpg/.jpeg/.png in the folder (sorted by name unless --order is given):
  * turns the photo upright using its EXIF orientation tag,
  * writes three WebP sizes into website/photos/ (720, 1280 and 2048 pixels wide, never larger than
    the original), keeping the Display P3 colour profile and dropping all other metadata (camera
    details, location),
  * makes a tiny, pre-blurred and darkened copy, embedded as text in the list; the site shows it
    instantly in the photo's place while the full photo loads,
  * writes website/photos/photos.js, the list the page reads (a script, so it also works when the
    page is opened straight from the folder).

The first photo in the order is the cover. Captions typed into photos.js are kept on the next run,
matched by the original file name.

Needs only tools already on this Mac: sips (built in), cwebp (brew install webp) and ffmpeg.
"""
import argparse, base64, json, math, os, shutil, struct, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'website', 'photos')
WIDTHS = [720, 1280, 2048]
QUALITY = {720: 80, 1280: 82, 2048: 80}
ROTATE = {3: 180, 6: 90, 8: 270}          # EXIF orientation -> degrees clockwise for sips


def exif_orientation(path):
    with open(path, 'rb') as f:
        d = f.read(256 * 1024)
    if d[:2] != b'\xff\xd8':
        return 1
    i = 2
    while i < len(d) - 4 and d[i] == 0xFF:
        marker, length = d[i + 1], struct.unpack('>H', d[i + 2:i + 4])[0]
        if marker == 0xE1 and d[i + 4:i + 10] == b'Exif\x00\x00':
            t = d[i + 10:i + 2 + length]
            e = '<' if t[:2] == b'II' else '>'
            off = struct.unpack(e + 'I', t[4:8])[0]
            for k in range(struct.unpack(e + 'H', t[off:off + 2])[0]):
                entry = t[off + 2 + 12 * k:off + 14 + 12 * k]
                if struct.unpack(e + 'H', entry[:2])[0] == 0x112:
                    return struct.unpack(e + 'H', entry[8:10])[0]
            return 1
        i += 2 + length
    return 1


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'failed: {" ".join(args)}\n{r.stderr}')
    return r.stdout


def size_of(path):
    out = run('sips', '-g', 'pixelWidth', '-g', 'pixelHeight', path)
    w = int(out.split('pixelWidth:')[1].split()[0])
    h = int(out.split('pixelHeight:')[1].split()[0])
    return w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder')
    ap.add_argument('--order', help='comma-separated file names; the first is the cover')
    a = ap.parse_args()
    for tool in ('sips', 'cwebp', 'ffmpeg'):
        if not shutil.which(tool):
            sys.exit(f'{tool} is needed (cwebp: brew install webp)')
    names = sorted(n for n in os.listdir(a.folder) if n.lower().endswith(('.jpg', '.jpeg', '.png')) and not n.startswith('.'))
    if a.order:
        wanted = [n.strip() for n in a.order.split(',') if n.strip()]
        missing = [n for n in wanted if n not in names]
        if missing:
            sys.exit(f'not in the folder: {missing}')
        names = wanted + [n for n in names if n not in wanted]
    old = {}
    for prev_file in ('photos.js', 'photos.json'):            # keep captions and cover crops from the last run
        try:
            with open(os.path.join(OUT, prev_file)) as f:
                text = f.read().strip()
            if text.startswith('window.__PHOTOS'):
                text = text.split('=', 1)[1].strip().rstrip(';')
            old = {p.get('source'): p for p in json.loads(text)['photos']}
            break
        except (OSError, ValueError, KeyError):
            pass
    os.makedirs(OUT, exist_ok=True)
    for n in os.listdir(OUT):
        if n.endswith('.webp'):
            os.remove(os.path.join(OUT, n))
    photos = []
    with tempfile.TemporaryDirectory() as tmp:
        for idx, name in enumerate(names, 1):
            src = os.path.join(a.folder, name)
            rot = ROTATE.get(exif_orientation(src), 0)
            rw, rh = size_of(src)
            w0, h0 = (rh, rw) if rot in (90, 270) else (rw, rh)
            stem = f'{idx:02d}'
            widths = [w for w in WIDTHS if w < w0] or [w0]
            for w in widths:
                h = math.ceil(w * h0 / w0)            # ceil, so a portrait comes out the full width
                png = os.path.join(tmp, f'{stem}-{w}.png')
                cmd = ['sips', '-s', 'format', 'png', '-Z', str(max(w, h))]
                if rot:
                    cmd += ['-r', str(rot)]
                run(*cmd, src, '--out', png)
                run('cwebp', '-quiet', '-q', str(QUALITY.get(w, 80)), '-m', '6', '-sharp_yuv', '-metadata', 'icc', png, '-o', os.path.join(OUT, f'{stem}-{w}.webp'))
            # tiny blurred, darkened copy for the backdrop and the loading placeholder
            tiny = os.path.join(tmp, f'{stem}-tiny.png')
            cmd = ['sips', '-s', 'format', 'png', '-Z', '96']
            if rot:
                cmd += ['-r', str(rot)]
            run(*cmd, src, '--out', tiny)
            blur = os.path.join(tmp, f'{stem}-blur.png')
            run('ffmpeg', '-loglevel', 'error', '-y', '-i', tiny, '-vf', 'scale=40:-2,gblur=sigma=1.5,colorchannelmixer=rr=.58:gg=.58:bb=.58,eq=saturation=1.15', blur)
            lq = os.path.join(tmp, f'{stem}-lq.webp')
            run('cwebp', '-quiet', '-q', '90', blur, '-o', lq)
            with open(lq, 'rb') as f:
                lqip = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()
            prev = old.get(name, {})
            photos.append({'source': name, 'file': stem, 'w': w0, 'h': h0, 'widths': widths,
                           'lqip': lqip, 'caption': prev.get('caption', ''), 'focus': prev.get('focus', '50% 45%')})
            sizes = ', '.join(f"{w}: {os.path.getsize(os.path.join(OUT, f'{stem}-{w}.webp')) // 1024} KB" for w in widths)
            print(f'{stem}  {name}  {w0}x{h0}{"  rotated " + str(rot) if rot else ""}  ->  {sizes}')
    # a small script rather than JSON, so the page can read it even when opened straight from the folder
    with open(os.path.join(OUT, 'photos.js'), 'w') as f:
        f.write('window.__PHOTOS = ' + json.dumps({'cover': 0, 'photos': photos}, indent=1) + ';\n')
    if os.path.exists(os.path.join(OUT, 'photos.json')):
        os.remove(os.path.join(OUT, 'photos.json'))
    total = sum(os.path.getsize(os.path.join(OUT, n)) for n in os.listdir(OUT))
    print(f'{len(photos)} photos, {total // 1024} KB in website/photos')


if __name__ == '__main__':
    main()
