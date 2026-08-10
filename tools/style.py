"""
Tough Country Fitness lower-third renderer.

NOTE: this file was rebuilt from scratch on 2026-08-06. The original
tools/style.py described in the handoff was never actually committed to
github.com/bkbingham95/tcf-media, so there was nothing to preserve.
Parameter names (yb, sa, bb) match the handoff so existing specs still work.

Public API:
    render(photo_path, headline, style_index, out_path, yb=0.5, sa=210, bb=0.42)

Styles cycle: 0 amber, 1 ice blue, 2 clay red, 3 green.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350  # 4:5

FONT_DIR = Path(__file__).parent / "fonts"
HEADLINE_FONT = FONT_DIR / "Anton-Regular.ttf"
TAG_FONT = FONT_DIR / "BarlowCondensed-SemiBold.ttf"

STYLES = [
    {"name": "amber", "accent": (232, 156, 38)},
    {"name": "ice blue", "accent": (126, 190, 226)},
    {"name": "clay red", "accent": (196, 78, 56)},
    {"name": "green", "accent": (116, 168, 96)},
]

MARGIN_X = 78
BASELINE_PAD = 96
TAG_TEXT = "T O U G H   C O U N T R Y   F I T N E S S"


def _crop_45(img, yb):
    """Crop to 4:5 keeping full width where possible. yb biases the vertical
    window: 0.0 hugs the top of the frame, 1.0 hugs the bottom."""
    target = W / H
    w, h = img.size
    if w / h > target:
        new_w = int(round(h * target))
        left = int(round((w - new_w) / 2))
        box = (left, 0, left + new_w, h)
    else:
        new_h = int(round(w / target))
        top = int(round((h - new_h) * yb))
        top = max(0, min(h - new_h, top))
        box = (0, top, w, top + new_h)
    return img.crop(box).resize((W, H), Image.LANCZOS)


def _scrim(sa, bb):
    """Vertical gradient, transparent at the top of the band to alpha `sa`
    at the bottom edge. bb is the band height as a fraction of image height."""
    band = max(1, int(round(H * bb)))
    grad = Image.new("L", (1, band))
    px = grad.load()
    for y in range(band):
        t = y / (band - 1) if band > 1 else 1.0
        px[0, y] = int(round(sa * (t ** 1.55)))
    grad = grad.resize((W, band), Image.BILINEAR)
    mask = Image.new("L", (W, H), 0)
    mask.paste(grad, (0, H - band))
    layer = Image.new("RGB", (W, H), (8, 9, 11))
    return layer, mask


def _fit_headline(draw, text, max_w, max_lines=3):
    """Largest Anton size at which the headline wraps into <= max_lines."""
    words = text.upper().split()
    for size in range(96, 43, -2):
        font = ImageFont.truetype(str(HEADLINE_FONT), size)
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines and all(
            draw.textlength(ln, font=font) <= max_w for ln in lines
        ):
            return font, lines, size
    return font, lines, size


def render(photo_path, headline, style_index, out_path, yb=0.5, sa=210, bb=0.42):
    style = STYLES[style_index % len(STYLES)]
    base = Image.open(photo_path).convert("RGB")
    canvas = _crop_45(base, yb)

    layer, mask = _scrim(sa, bb)
    canvas = Image.composite(layer, canvas, mask)

    draw = ImageDraw.Draw(canvas)
    max_w = W - (MARGIN_X * 2)
    font, lines, size = _fit_headline(draw, headline, max_w)

    leading = int(round(size * 1.06))
    block_h = leading * len(lines)
    tag_h = 34 + 26          # tag glyph band + gap above it
    rule_h = 8 + 26          # accent rule + gap below it
    y = H - BASELINE_PAD - tag_h - rule_h - block_h

    # headline: every line white except the last, which takes the accent
    for i, line in enumerate(lines):
        draw.text(
            (MARGIN_X, y),
            line,
            font=font,
            fill=style["accent"] if i == len(lines) - 1 else (255, 255, 255),
            stroke_width=2,
            stroke_fill=(0, 0, 0),
        )
        y += leading

    # accent rule sits under the headline, above the wordmark
    rule_y = y + 22
    draw.rectangle(
        [MARGIN_X, rule_y, MARGIN_X + 176, rule_y + 8], fill=style["accent"]
    )

    tag = ImageFont.truetype(str(TAG_FONT), 34)
    draw.text(
        (MARGIN_X, rule_y + 34),
        TAG_TEXT,
        font=tag,
        fill=(255, 255, 255),
    )

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "JPEG", quality=92, optimize=True)
    return {
        "out": str(out_path),
        "style": style["name"],
        "font_size": size,
        "lines": lines,
    }
