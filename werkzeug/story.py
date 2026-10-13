# story.py – Aufruf: python3 story.py FOTO_4x5.jpg AUSGABE.jpg "Zeile 1" "Zeile 2" "Detailzeile" [EMOJI]
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageCms

W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
REG = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
MAXW = 900  # maximale Zeilenbreite, damit seitlich Rand bleibt

def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)  # Noto Color Emoji nur in 109 px
    tmp = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((10, 10), ch, font=f, embedded_color=True)
    tmp = tmp.crop(tmp.getbbox())
    s = size / tmp.height
    return tmp.resize((round(tmp.width * s), size), Image.LANCZOS)

def main(src, dst, l1, l2, detail, emo=""):
    photo = Image.open(src).convert("RGB")
    bg = cover(photo, W, H).filter(ImageFilter.GaussianBlur(45))
    bg = ImageEnhance.Brightness(bg).enhance(0.42)
    canvas = bg.convert("RGBA")
    d = ImageDraw.Draw(canvas)
    lines = [t for t in (l1, l2) if t]
    size = 74
    while True:  # Schrift verkleinern, bis jede Zeile (mit Emoji) passt
        fb = ImageFont.truetype(BOLD, size)
        esz = round(size * 0.95)
        widths = [d.textlength(t, font=fb) + ((esz + 18) if (emo and i == len(lines) - 1) else 0)
                  for i, t in enumerate(lines)]
        if max(widths) <= MAXW or size <= 52:
            break
        size -= 2
    y = 285
    for i, t in enumerate(lines):
        tw = d.textlength(t, font=fb)
        e = emoji_img(emo, esz) if (emo and i == len(lines) - 1) else None
        x = (W - widths[i]) / 2
        d.text((x, y), t, font=fb, fill=(255, 255, 255))
        if e:
            canvas.alpha_composite(e, (round(x + tw + 18), y + round(size * 0.08)))
        y += round(size * 1.24)
    pw, ph = 800, 1000
    py = max(y + 40, 470)
    p = photo.resize((pw, ph), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), radius=28, fill=255)
    shadow = Image.new("RGBA", (pw + 80, ph + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((40, 40, pw + 40, ph + 40), radius=28, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    canvas.alpha_composite(shadow, ((W - pw) // 2 - 40, py - 40 + 12))
    canvas.paste(p, ((W - pw) // 2, py), mask)
    if detail:
        fr = ImageFont.truetype(REG, 42)
        tw = d.textlength(detail, font=fr)
        d.text(((W - tw) / 2, py + ph + 38), detail, font=fr, fill=(235, 235, 235))
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    canvas.convert("RGB").save(dst, "JPEG", quality=90, optimize=True, icc_profile=srgb)
    print(f"Schriftgroesse {size}, breiteste Zeile {round(max(widths))} px")

if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5] if len(a) > 5 else "")
