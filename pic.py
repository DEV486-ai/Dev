import random
import cv2
import numpy as np

INPUT_IMAGE = r"krish.png"               
                                                                                
SAVE_IMAGES = False                      
OUTPUT_IMAGE = r"output_clear_photo.png" 
                                         
SAVE_NEON_SKETCH_TOO = True              
OUTPUT_NEON_IMAGE     = r"output_neon_sketch.png"

CANVAS_W, CANVAS_H = 1980, 1100          
FPS               = 60
WINDOW_NAME       = "Neon Sketch Reveal"
FULLSCREEN         = True                
DOT_REVEAL_SECONDS = 3.5                 
REFINE_SECONDS      = 3.0                
HOLD_SECONDS         = 3.0               
CROSSFADE_SECONDS    = 1.5               
FINAL_HOLD_SECONDS   = 3.0               

MOSAIC_BLOCK_SIZE = 10                
DOT_SHAPE          = "circle"          
DARK_PIXEL_SKIP    = 18                  
RANDOM_SEED         = 42               

GLOW_COLOR_MODE   = "original"           
                                          # or set a tuple like (255, 80, 180) for a single neon tint
EDGE_LOW, EDGE_HIGH = 60, 150            
LINE_THICKNESS       = 2                
GLOW_STRENGTH         = 1.6             
REFLECTION_HEIGHT_RATIO = 0.28          


DISPLAY_BRIGHTNESS = 30                 
DISPLAY_CONTRAST     = 1           
AUTO_CONTRAST         = True         


SAVE_MODE = "boosted"


MANUAL_SCREEN_SIZE = None



def get_screen_size():
    """Try to detect the true physical monitor resolution; fall back if it fails."""
    if MANUAL_SCREEN_SIZE is not None:
        return MANUAL_SCREEN_SIZE

   
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    try:
        import ctypes
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass

    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return w, h
    except Exception:
        return 1080, 1920


def load_and_fit(path, w, h):
    """Load image and fit it (letterboxed, centered) into a w x h black canvas."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")

    ih, iw = img.shape[:2]
    scale = min(w / iw, h / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    x_off = (w - new_w) // 2
    y_off = (h - new_h) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized
    return canvas


def make_neon_edge_layer(img):
    """Detect edges and colorize them into a bright, layered-glow neon line-art layer."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    edges = cv2.Canny(gray, EDGE_LOW, EDGE_HIGH)
    if LINE_THICKNESS > 0:
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=LINE_THICKNESS)

    mask = edges.astype(bool)

    color_layer = np.zeros_like(img)
    if GLOW_COLOR_MODE == "original":
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * 1.7, 0, 255)
        hsv[..., 2] = np.clip(hsv[..., 2] * 1.5 + 60, 0, 255)
        boosted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        color_layer[mask] = boosted[mask]
    else:
        b, g, r = GLOW_COLOR_MODE[2], GLOW_COLOR_MODE[1], GLOW_COLOR_MODE[0]
        color_layer[mask] = (b, g, r)

    
    inner_glow = cv2.GaussianBlur(color_layer, (0, 0), sigmaX=4, sigmaY=4)
    outer_glow = cv2.GaussianBlur(color_layer, (0, 0), sigmaX=14, sigmaY=14)

    combined = (
        color_layer.astype(np.float32) * 1.4
        + inner_glow.astype(np.float32) * 1.1
        + outer_glow.astype(np.float32) * 0.7
    ) * GLOW_STRENGTH

    combined = np.clip(combined, 0, 255)

    if AUTO_CONTRAST:
        lit_pixels = combined[combined > 5]
        if lit_pixels.size > 0:
            ref = np.percentile(lit_pixels, 99)
            if ref > 1:
                combined = np.clip(combined * (255.0 / ref), 0, 255)

    return combined.astype(np.uint8)


def block_mosaic(img, block_size):
    """
    Downsample img into block_size x block_size blocks, where each block takes
    the color of its single brightest pixel (keeps thin neon lines visible
    instead of averaging them into a dim blur), then upsamples back with hard
    pixel edges. block_size <= 1 returns the original image unchanged.
    """
    if block_size <= 1:
        return img.copy()

    h, w = img.shape[:2]
    ph = (block_size - h % block_size) % block_size
    pw = (block_size - w % block_size) % block_size
    padded = np.pad(img, ((0, ph), (0, pw), (0, 0)), mode="constant")
    H, W = padded.shape[:2]
    gh, gw = H // block_size, W // block_size

    reshaped = padded.reshape(gh, block_size, gw, block_size, 3)
    reshaped = reshaped.transpose(0, 2, 1, 3, 4).reshape(gh, gw, block_size * block_size, 3)

    intensity = reshaped.sum(axis=-1)                     
    idx = np.argmax(intensity, axis=-1)                   
    block_colors = np.take_along_axis(
        reshaped, idx[..., None, None], axis=2
    ).squeeze(2)                                            

    upsampled = np.repeat(np.repeat(block_colors, block_size, axis=0), block_size, axis=1)
    return upsampled[:h, :w].astype(np.uint8)


def get_block_grid(mosaic_img, block_size):
    """Return a flat list of (x, y, w, h, color) for each block in mosaic_img."""
    h, w = mosaic_img.shape[:2]
    blocks = []
    for by in range(0, h, block_size):
        for bx in range(0, w, block_size):
            color = mosaic_img[by, bx]
            if int(color.max()) <= DARK_PIXEL_SKIP:
                continue  
            bw = min(block_size, w - bx)
            bh = min(block_size, h - by)
            blocks.append((bx, by, bw, bh, tuple(int(c) for c in color)))
    return blocks


def draw_block(canvas, block):
    bx, by, bw, bh, color = block
    if DOT_SHAPE == "circle":
        center = (bx + bw // 2, by + bh // 2)
        radius = max(1, min(bw, bh) // 2)
        cv2.circle(canvas, center, radius, color, -1, lineType=cv2.LINE_AA)
    else:
        cv2.rectangle(canvas, (bx, by), (bx + bw - 1, by + bh - 1), color, -1)


def add_reflection(frame, ratio):
    h, w = frame.shape[:2]
    refl_h = int(h * ratio)
    reflection = cv2.flip(frame[h - refl_h:h, :], 0)
    fade = np.linspace(0.35, 0.0, refl_h).reshape(refl_h, 1, 1)
    reflection = (reflection.astype(np.float32) * fade).astype(np.uint8)
    out = frame.copy()
    start_y = h - refl_h
    blended = cv2.addWeighted(out[start_y:h], 0.4, reflection, 0.9, 0)
    out[start_y:h] = np.maximum(out[start_y:h], blended)
    return out


def prepare_for_screen(frame, screen_w, screen_h):
    """Boost brightness/contrast, then letterbox the frame onto a black screen_w x screen_h canvas."""
    display = cv2.convertScaleAbs(frame, alpha=DISPLAY_CONTRAST, beta=DISPLAY_BRIGHTNESS)

    h, w = display.shape[:2]
    scale = min(screen_w / w, screen_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(display, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    canvas = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
    x_off = (screen_w - new_w) // 2
    y_off = (screen_h - new_h) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized
    return canvas


def show_frame(frame, delay_ms, screen_w, screen_h):
    """Display a frame full-screen and return False if the user requested to quit."""
    display_frame = prepare_for_screen(frame, screen_w, screen_h)
    cv2.imshow(WINDOW_NAME, display_frame)
    key = cv2.waitKey(delay_ms) & 0xFF
    if key == ord("q") or key == 27:  # 'q' or Esc
        return False
    return True


def save_neon_sketch(frame):
    """Optionally save the neon sketch (with reflection) to OUTPUT_NEON_IMAGE."""
    if not SAVE_IMAGES or not SAVE_NEON_SKETCH_TOO:
        return
    if SAVE_MODE == "boosted":
        out = cv2.convertScaleAbs(frame, alpha=DISPLAY_CONTRAST, beta=DISPLAY_BRIGHTNESS)
    else:
        out = frame
    ok = cv2.imwrite(OUTPUT_NEON_IMAGE, out)
    if ok:
        print(f"Saved neon sketch to: {OUTPUT_NEON_IMAGE}")
    else:
        print(f"WARNING: failed to save neon sketch to: {OUTPUT_NEON_IMAGE}")


def save_original_photo():
    """
    Copy the ORIGINAL input photo, untouched and at full quality, to OUTPUT_IMAGE.
    This re-reads straight from disk rather than reusing the resized/letterboxed
    in-memory canvas, so the saved file matches exactly what you gave the script.
    """
    if not SAVE_IMAGES:
        return
    import shutil
    try:
        shutil.copyfile(INPUT_IMAGE, OUTPUT_IMAGE)
        print(f"Saved original clear photo to: {OUTPUT_IMAGE}")
    except Exception as e:
        print(f"WARNING: failed to copy original photo to {OUTPUT_IMAGE}: {e}")


def crossfade(frame_a, frame_b, t):
    """Blend two same-size frames: t=0 -> frame_a, t=1 -> frame_b."""
    return cv2.addWeighted(frame_a, 1 - t, frame_b, t, 0)


def main():
    base = load_and_fit(INPUT_IMAGE, CANVAS_W, CANVAS_H)
    neon = make_neon_edge_layer(base)

    delay_ms = max(1, int(1000 / FPS))

    screen_w, screen_h = get_screen_size()
    print(f"Detected screen size: {screen_w} x {screen_h}")
    print(f"If that does NOT match your monitor, set MANUAL_SCREEN_SIZE = ({screen_w}, {screen_h}) "
          f"at the top of the script to the correct values.")

  
    sharp_frame = add_reflection(neon, REFLECTION_HEIGHT_RATIO)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    if FULLSCREEN:
        cv2.resizeWindow(WINDOW_NAME, screen_w, screen_h)
        cv2.moveWindow(WINDOW_NAME, 0, 0)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

   
    full_mosaic = block_mosaic(neon, MOSAIC_BLOCK_SIZE)
    blocks = get_block_grid(full_mosaic, MOSAIC_BLOCK_SIZE)

    rng = random.Random(RANDOM_SEED)
    order = blocks[:]
    rng.shuffle(order)

    dot_frames = max(1, int(DOT_REVEAL_SECONDS * FPS))
    canvas = np.zeros_like(neon)
    revealed = 0

    for i in range(dot_frames):
        target = int(len(order) * (i + 1) / dot_frames)
        for block in order[revealed:target]:
            draw_block(canvas, block)
        revealed = target

        frame = add_reflection(canvas, REFLECTION_HEIGHT_RATIO)
        if not show_frame(frame, delay_ms, screen_w, screen_h):
            save_neon_sketch(sharp_frame)
            save_original_photo()
            cv2.destroyAllWindows()
            return

   
    refine_frames = max(1, int(REFINE_SECONDS * FPS))
    for i in range(refine_frames):
        t = (i + 1) / refine_frames                      # 0 -> 1
        block_size = max(1, int(MOSAIC_BLOCK_SIZE * (1 - t) ** 2))
        frame = block_mosaic(neon, block_size)
        frame = add_reflection(frame, REFLECTION_HEIGHT_RATIO)
        if not show_frame(frame, delay_ms, screen_w, screen_h):
            save_neon_sketch(sharp_frame)
            save_original_photo()
            cv2.destroyAllWindows()
            return

    
    save_neon_sketch(sharp_frame)

    hold_frames = max(1, int(HOLD_SECONDS * FPS))
    for _ in range(hold_frames):
        if not show_frame(sharp_frame, delay_ms, screen_w, screen_h):
            save_original_photo()
            cv2.destroyAllWindows()
            return

   
    crossfade_frames = max(1, int(CROSSFADE_SECONDS * FPS))
    for i in range(crossfade_frames):
        t = (i + 1) / crossfade_frames                   
        frame = crossfade(sharp_frame, base, t)
        if not show_frame(frame, delay_ms, screen_w, screen_h):
            save_original_photo()
            cv2.destroyAllWindows()
            return

   
    save_original_photo()

    final_hold_frames = max(1, int(FINAL_HOLD_SECONDS * FPS))
    for _ in range(final_hold_frames):
        if not show_frame(base, delay_ms, screen_w, screen_h):
            cv2.destroyAllWindows()
            return

    
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
