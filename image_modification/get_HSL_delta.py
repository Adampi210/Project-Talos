import sys
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
import colorsys
import json

# --- 1. CONFIGURATION ---
ANCHOR_PIXEL = (446, 86)

ERROR_THRESHOLD = 1.0
TRANSPARENCY_TOLERANCE = 10

# HSL search parameters - Let's use the range you found manually in GIMP
# H:-70, S:-65, L:-80
hue_range = np.arange(0, -80, -0.1)
saturation_range = np.arange(-45, -85, -0.1)
lightness_range = np.arange(-60, -95, -0.1)

# --- 2. HELPER FUNCTIONS ---

def is_transparent(pixel_rgba):
    alpha = pixel_rgba[3]
    return alpha < TRANSPARENCY_TOLERANCE

def apply_hsl_transformation(rgb_tuple, dh, ds, dl):
    """
    Applies HSL shifts using a hybrid method that more closely matches image editors.
    - Hue is shifted using the standard colorsys model.
    - Saturation and Brightness/Lightness are adjusted using Pillow's ImageEnhance module.
    """
    # Step 1: Apply Hue shift using the reliable colorsys method
    r, g, b = [x / 255.0 for x in rgb_tuple]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    new_h = (h + dh / 360.0) % 1.0
    hue_shifted_rgb = [int(x * 255) for x in colorsys.hls_to_rgb(new_h, l, s)]

    # Step 2 & 3: Apply Saturation and Lightness using ImageEnhance for better results
    # This requires creating a temporary 1x1 pixel image to apply enhancers to
    temp_img = Image.new("RGB", (1, 1), tuple(hue_shifted_rgb))

    # Apply Saturation. A factor of 1.0 is original, 0.0 is black & white.
    sat_factor = 1.0 + (ds / 100.0)
    enhancer = ImageEnhance.Color(temp_img)
    temp_img = enhancer.enhance(sat_factor)

    # Apply Lightness/Brightness. A factor of 1.0 is original, 0.0 is black.
    light_factor = 1.0 + (dl / 100.0)
    enhancer = ImageEnhance.Brightness(temp_img)
    temp_img = enhancer.enhance(light_factor)
    
    # Return the final RGB tuple from the 1x1 image
    return temp_img.getpixel((0, 0))

# --- 3. MAIN SCRIPT ---

try:
    original_img = Image.open("texture_00.png").convert("RGBA")
    desired_img = Image.open("main_texture.png").convert("RGBA")
    print("✓ Images loaded successfully in RGBA mode.")
except FileNotFoundError as e:
    print(f"Error: Could not find an image file. Make sure '{e.filename}' is in the script's directory.")
    sys.exit()

preview_img = Image.new("RGBA", original_img.size, (0, 0, 0, 0))
preview_img.paste(original_img, (0, 0), original_img)
draw = ImageDraw.Draw(preview_img)

print(f"Using single anchor pixel at location {ANCHOR_PIXEL}...")
pixel_rgba = original_img.getpixel(ANCHOR_PIXEL)
if is_transparent(pixel_rgba):
    print(f"Error: The chosen anchor pixel {ANCHOR_PIXEL} is transparent.")
    sys.exit()

original_anchor_color = pixel_rgba[:3]
desired_anchor_color = desired_img.getpixel(ANCHOR_PIXEL)[:3]

x, y = ANCHOR_PIXEL
draw.rectangle([x-2, y-2, x+2, y+2], fill="red", outline="red")
preview_img.save("anchor_point_preview.png")
print(f"✓ Anchor point set. Original Color: {original_anchor_color}, Desired Color: {desired_anchor_color}")

# --- 4. ITERATIVE SEARCH ---

print("\nStarting HSL search...")
min_rmse_so_far = float('inf')
best_hsl_so_far = {}

total_iterations = len(hue_range) * len(saturation_range) * len(lightness_range)
iteration_count = 0

for h_delta in hue_range:
    for s_delta in saturation_range:
        for l_delta in lightness_range:
            iteration_count += 1
            if iteration_count % 10000 == 0:
                print(f"  > Progress: {iteration_count / total_iterations:.1%}")

            transformed_color = apply_hsl_transformation(original_anchor_color, h_delta, s_delta, l_delta)
            error_squared = sum((transformed_color[j] - desired_anchor_color[j])**2 for j in range(3))
            rmse = np.sqrt(error_squared)
            
            if rmse < min_rmse_so_far:
                min_rmse_so_far = rmse
                best_hsl_so_far = {'h': h_delta, 's': s_delta, 'l': l_delta}
                print(f"  > New best found! HSL({h_delta:.1f}, {s_delta:.1f}, {l_delta:.1f}) -> RGB{transformed_color} | Error: {rmse:.2f}")

# --- 5. FINISH ---

print("\n" + "="*40)
print("Search Complete. Best Possible Match Found:")
print(f"  HSL Deltas: (Hue: {best_hsl_so_far.get('h', 'N/A'):.2f}, Saturation: {best_hsl_so_far.get('s', 'N/A'):.2f}, Lightness: {best_hsl_so_far.get('l', 'N/A'):.2f})")
print(f"  Lowest Error (RMSE): {min_rmse_so_far:.4f}")
print("="*40)