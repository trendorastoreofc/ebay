from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

B = '/tmp/claude-0/-home-user-ebay/863e68f2-aa7a-5e89-aef7-f39e415d1dd4/'
OUT = __import__('os').path.dirname(__import__('os').path.abspath(__file__)) + '/'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ITAL = '/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf'
BLACK = (20, 20, 20)
RED = (215, 25, 32)


def load(i):
    return Image.open(f'{B}images/{i}.webp').convert('RGB')


def alpha_from_mask(i, lo=0.15, hi=0.85):
    m = np.array(Image.open(f'{B}work/bmask{i}.png').convert('L')).astype(float) / 255
    return np.clip((m - lo) / (hi - lo), 0, 1)


def on_white(img, a):
    arr = np.array(img).astype(float)
    a = a[..., None]
    out = arr * a + 255 * (1 - a)
    return Image.fromarray(out.astype(np.uint8))


def colour_key(img, target, tol):
    arr = np.array(img).astype(float)
    d = np.sqrt(((arr - np.array(target)) ** 2).sum(-1))
    return np.clip(1 - (d - tol * 0.6) / (tol * 0.4), 0, 1)


def paint(canvas, a, colour):
    arr = np.array(canvas).astype(float)
    a = a[..., None]
    arr = arr * (1 - a) + np.array(colour) * a
    return Image.fromarray(arr.astype(np.uint8))


# EXP logo taken from image 1 (it already sits on white there)
src1 = load(1)
logo = src1.crop((410, 38, 612, 104))


def add_logo(canvas, x=30, y=28, w=150):
    lg = logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS)
    la = np.array(lg).astype(float)
    # treat near-white as transparent so it sits cleanly on the white canvas
    a = np.clip((255 - la.min(-1)) / 60, 0, 1)
    arr = np.array(canvas).astype(float)
    region = arr[y:y + lg.height, x:x + lg.width]
    region[:] = region * (1 - a[..., None]) + la * a[..., None]
    return Image.fromarray(arr.astype(np.uint8))


def text(d, xy, s, size, font=BOLD, fill=BLACK, anchor='la'):
    d.text(xy, s, font=ImageFont.truetype(font, size), fill=fill, anchor=anchor)


def fit(d, s, font, max_w, start):
    size = start
    while ImageFont.truetype(font, size).getlength(s) > max_w:
        size -= 1
    return size


def captions(img, title, sub, top, right_edge=None, left=None):
    d = ImageDraw.Draw(img)
    W = img.width
    ts = fit(d, title, BOLD, W - 80, 64)
    ss = fit(d, sub, ITAL, W - 80, 36)
    if left is not None:
        text(d, (left, top), title, ts)
        text(d, (left, top + ts + 12), sub, ss, ITAL, RED)
    else:
        text(d, (right_edge, top), title, ts, anchor='ra')
        text(d, (right_edge, top + ts + 12), sub, ss, ITAL, RED, anchor='ra')


def circle_callout(canvas, src, cx, cy, r, tail):
    """Paste a circular zoom crop with a yellow ring and pointer tail."""
    d = ImageDraw.Draw(canvas)
    d.polygon([(cx + (tail[0] - cx) * 0.2 - 18, cy + (tail[1] - cy) * 0.2),
               (cx + (tail[0] - cx) * 0.2 + 18, cy + (tail[1] - cy) * 0.2), tail], fill=(250, 215, 0))
    crop = src.crop((cx - r, cy - r, cx + r, cy + r))
    m = Image.new('L', (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    canvas.paste(crop, (cx - r, cy - r), m)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(250, 215, 0), width=8)
    return canvas


# ---------- Image 1: whiten patterned background ----------
arr = np.array(src1).astype(int)
lowsat = (arr.max(-1) - arr.min(-1)) < 22
bright = arr.min(-1) > 200
arr[lowsat & bright] = 255
Image.fromarray(arr.astype(np.uint8)).save(OUT + '1-hunter-jump-frog.jpg', quality=95)

# ---------- Image 2: hook tube ----------
src = load(2)
img = on_white(src, alpha_from_mask(2))
img = add_logo(img)
captions(img, 'HOOK TUBE', 'Weedless: prevents snagging in weeds', 80, right_edge=src.width - 40)
img.save(OUT + '2-hook-tube.jpg', quality=95)

# ---------- Image 3: removable tube ----------
src = load(3)
a = alpha_from_mask(3)
fade = np.clip((640 - np.arange(src.height)) / 60, 0, 1)[:, None]
a = a * fade
img = on_white(src, a)
arrows = colour_key(src, (216, 152, 82), 70)
arrows[:, :450] = 0
arrows[360:, :] = 0
img = paint(img, arrows, (240, 150, 40))
img = add_logo(img)
d = ImageDraw.Draw(img)
text(d, (465, 350), 'Higher', 40, ITAL, RED)
text(d, (465, 398), 'hook-up rate!', 40, ITAL, RED)
captions(img, 'REMOVABLE TUBE', 'Take it off for open-water fishing', 655, right_edge=src.width - 30)
img.save(OUT + '3-removable-tube.jpg', quality=95)

# ---------- Image 4: wooden body ----------
src = load(4)
img = on_white(src, alpha_from_mask(4))
img = circle_callout(img, src, 118, 185, 88, (205, 283))
img = circle_callout(img, src, 563, 180, 88, (472, 325))
img = add_logo(img, x=src.width - 190, y=28)
d = ImageDraw.Draw(img)
text(d, (232, 200), 'Clean paint', 34, ITAL, BLACK)
text(d, (232, 240), 'finish', 34, ITAL, BLACK)
text(d, (660, 250), 'Quality', 34, ITAL, BLACK)
text(d, (660, 290), 'wood', 34, ITAL, BLACK)
captions(img, 'WOODEN BODY', 'Made from selected wood only', 640, left=35)
img.save(OUT + '4-wooden-body.jpg', quality=95)

# ---------- Image 5: flat mouth ----------
src = load(5)
a = alpha_from_mask(5)
img = on_white(src, a)
cyan = colour_key(src, (4, 254, 255), 120)
cyan[600:, :] = 0
cyan[:, :450] = 0
cyan[515:580, 480:760] = 0
yellow = colour_key(src, (250, 235, 20), 110)
yellow[:150, :] = 0
yellow[610:, :] = 0
yellow[:, :280] = 0
yellow[150:240, 430:560] = 0  # drop the old "Rata*" label
yellow = yellow * (1 - a)
img = paint(img, cyan, (0, 160, 210))
img = paint(img, yellow, (235, 170, 0))
img = add_logo(img)
d = ImageDraw.Draw(img)
text(d, (420, 175), 'Flat*', 38, ITAL, BLACK)
text(d, (480, 520), 'Water splash*', 38, ITAL, (0, 140, 190))
captions(img, 'FLAT-MOUTH DESIGN', 'Wider, stronger surface splash', 645, left=35)
img.save(OUT + '5-flat-mouth.jpg', quality=95)
