#!/usr/bin/env python3
"""Flatten the illustrated cover with title text. 'The Mind of Ayanokoji' is bold."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/book/assets")
ART = ROOT / "cover-ayanokoji.png"
OUT = ROOT / "cover-front.jpg"

# 6×9 in at 300 dpi — usable as an Amazon/KDP front
W, H = 1800, 2700
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def fit_cover(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def tracked(draw, text, font, xy, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def main() -> None:
    base = fit_cover(Image.open(ART), W, H)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pix = overlay.load()
    # Gradient over the lower ~42% (matches the PDF fade)
    y0 = int(H * 0.55)
    for y in range(y0, H):
        t = (y - y0) / (H - y0)
        # ease into dark
        a = int(min(235, (t**1.15) * 240))
        for x in range(W):
            pix[x, y] = (0, 0, 0, a)

    img = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    kicker = ImageFont.truetype(FONT, 46)
    title = ImageFont.truetype(FONT_B, 134)
    sub = ImageFont.truetype(FONT_B, 72)

    mx = 136  # ~1.15cm
    y = H - 640

    tracked(
        d,
        "A STUDY OF SINGULAR THOUGHT",
        kicker,
        (mx, y),
        (201, 184, 150),
        tracking=6,
    )
    y += 78
    d.text((mx, y), "Thinking as", font=title, fill=(244, 239, 230))
    y += 148
    d.text((mx, y), "One Being", font=title, fill=(244, 239, 230))
    y += 168
    d.text((mx, y), "The Mind of Ayanokoji", font=sub, fill=(230, 215, 184))

    img.save(OUT, "JPEG", quality=95, optimize=True, subsampling=0)
    print("wrote", OUT, OUT.stat().st_size, img.size)


if __name__ == "__main__":
    main()
