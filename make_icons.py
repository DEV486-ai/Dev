"""
icons ফোল্ডারে favicon ও PWA আইকন তৈরি করে।
চালানোর আগে Pillow ইনস্টল থাকতে হবে: pip install Pillow
রান করুন: python3 make_icons.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

GREEN = (47, 65, 49)
GOLD = (200, 145, 22)
CREAM = (243, 236, 221)

SIZES = [16, 32, 48, 180, 192, 512]


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), GREEN)
    draw = ImageDraw.Draw(img)

    # সহজ কাপ-আকৃতির আইকন
    margin = size * 0.2
    cup_top = size * 0.35
    cup_bottom = size * 0.8
    draw.rectangle(
        [margin, cup_top, size - margin, cup_bottom],
        fill=GOLD,
    )
    draw.ellipse(
        [margin, cup_bottom - size * 0.06, size - margin, cup_bottom + size * 0.06],
        fill=CREAM,
    )
    return img


def main():
    for size in SIZES:
        icon = make_icon(size)
        filename = f"favicon-{size}.png" if size <= 48 else f"icon-{size}.png"
        icon.save(os.path.join(ICONS_DIR, filename))
        print(f"তৈরি হয়েছে: icons/{filename}")


if __name__ == "__main__":
    main()
