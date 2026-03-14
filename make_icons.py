"""Generate simple PWA icons"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    def make_icon(size, path):
        img = Image.new("RGBA", (size, size), (13, 15, 24, 255))
        draw = ImageDraw.Draw(img)
        # Background circle gradient effect
        for i in range(size//2, 0, -1):
            alpha = int(80 * (1 - i/(size//2)))
            draw.ellipse([size//2-i, size//2-i, size//2+i, size//2+i],
                        fill=(0, 245, 255, alpha))
        # Text B
        try:
            fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                      size//2)
        except:
            fnt = ImageFont.load_default()
        draw.text((size//2, size//2), "B", fill=(0, 245, 255, 255),
                 font=fnt, anchor="mm")
        img.save(path)
        print(f"Icon created: {path}")

    base = os.path.dirname(__file__)
    make_icon(192, os.path.join(base, "static", "icon-192.png"))
    make_icon(512, os.path.join(base, "static", "icon-512.png"))
except ImportError:
    # Create minimal 1x1 PNG if PIL not available
    import base64, os
    # Minimal cyan 192x192 PNG (base64 encoded simple PNG)
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    data = base64.b64decode(png_b64)
    base = os.path.dirname(__file__)
    for name in ["icon-192.png", "icon-512.png"]:
        with open(os.path.join(base, "static", name), "wb") as f:
            f.write(data)
    print("Minimal icons created")
