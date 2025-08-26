import sys
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
import colorsys
from scipy.optimize import differential_evolution

# --- 1. CONFIGURATION ---
# The rectangle to sample from AND to recolor later
RECOLOR_AND_SAMPLE_RECTANGLE = (1123, 464, 1165, 504)
# The spacing for the anchor points within the rectangle
GRID_SPACING = 3
TRANSPARENCY_TOLERANCE = 10

# --- 2. HELPER FUNCTIONS ---

def is_transparent(pixel_rgba):
    """Checks if a pixel is transparent by looking at its alpha channel."""
    alpha = pixel_rgba[3]
    return alpha < TRANSPARENCY_TOLERANCE

def apply_rgb_and_hsl_transformation(rgb_tuple, dr, dg, db, dh, ds, dl):
    """
    First applies an additive RGB mask, then applies HSL shifts.
    This is the core transformation function for the optimizer.
    """
    r, g, b = rgb_tuple

    # --- Step 1: Apply the additive RGB mask ---
    # We add the delta values and then "clamp" the result between 0 and 255
    masked_r = int(max(0, min(255, r + dr)))
    masked_g = int(max(0, min(255, g + dg)))
    masked_b = int(max(0, min(255, b + db)))

    # --- Step 2: Apply HSL transformation to the masked color ---
    r_norm, g_norm, b_norm = [x / 255.0 for x in (masked_r, masked_g, masked_b)]
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    
    new_h = (h + dh / 360.0) % 1.0
    hue_shifted_rgb = [int(x * 255) for x in colorsys.hls_to_rgb(new_h, l, s)]
    
    # Use Pillow's ImageEnhance for more perceptually accurate saturation/lightness
    temp_img = Image.new("RGB", (1, 1), tuple(hue_shifted_rgb))
    
    sat_factor = 1.0 + (ds / 100.0)
    enhancer = ImageEnhance.Color(temp_img)
    temp_img = enhancer.enhance(sat_factor)
    
    light_factor = 1.0 + (dl / 100.0)
    enhancer = ImageEnhance.Brightness(temp_img)
    temp_img = enhancer.enhance(light_factor)
    
    return temp_img.getpixel((0, 0))

# --- 3. MAIN SCRIPT: SETUP ---

try:
    original_img = Image.open("texture_00_decolored.png").convert("RGBA")
    desired_img = Image.open("main_texture.png").convert("RGBA")
    print("✓ Images loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: Could not find image file '{e.filename}'.")
    sys.exit()

preview_img = original_img.copy()
draw = ImageDraw.Draw(preview_img)

original_anchor_colors = []
desired_anchor_colors = []

print(f"Sampling anchor points from rectangle {RECOLOR_AND_SAMPLE_RECTANGLE} with a {GRID_SPACING}px grid...")
left, top, right, bottom = RECOLOR_AND_SAMPLE_RECTANGLE
for x in range(left, right, GRID_SPACING):
    for y in range(top, bottom, GRID_SPACING):
        pixel_rgba = original_img.getpixel((x, y))
        if not is_transparent(pixel_rgba):
            original_anchor_colors.append(pixel_rgba[:3])
            desired_anchor_colors.append(desired_img.getpixel((x, y))[:3])
            draw.rectangle([x-1, y-1, x+1, y+1], fill="red", outline="red")

if not original_anchor_colors:
    print("Error: No anchor points found in the specified rectangle.")
    sys.exit()

preview_img.save("anchor_points_preview.png")
print(f"✓ Found {len(original_anchor_colors)} anchor points. See 'anchor_points_preview.png' for locations.")

# --- 4. GLOBAL OPTIMIZATION ---

def objective_function(params):
    """
    Calculates the AVERAGE error across all anchor points for a given set of
    6 transformation parameters (R, G, B, H, S, L).
    """
    dr, dg, db, dh, ds, dl = params
    total_error = 0
    
    for i in range(len(original_anchor_colors)):
        original_color = original_anchor_colors[i]
        desired_color = desired_anchor_colors[i]
        
        transformed_color = apply_rgb_and_hsl_transformation(original_color, dr, dg, db, dh, ds, dl)
        
        # Add the squared error for this specific pixel to the total
        total_error += sum((transformed_color[j] - desired_color[j])**2 for j in range(3))
    
    # Return the Root Mean Square Error (RMSE) across all points
    return np.sqrt(total_error / len(original_anchor_colors))

# MODIFIED: Expanded bounds to include RGB mask values
# The order is (R, G, B, Hue, Saturation, Lightness)
bounds = [
    (-255, 255),       # R-delta for the mask
    (-255, 255),       # G-delta for the mask
    (-255, 255),       # B-delta for the mask
    (-180, 180),       # Hue delta
    (-100, 100),       # Saturation delta
    (-100, 100)        # Lightness delta
]

print("\nStarting global optimization for 6 parameters (RGB Mask + HSL)...")
# Note: A 6-dimensional problem is much harder. You might need to increase popsize or maxiter.
result = differential_evolution(objective_function, bounds, disp=True, polish=True, maxiter=10000, popsize=50)

# --- 5. PROCESS AND SAVE RESULTS ---
if result.success:
    best_params = result.x
    final_error = result.fun

    print("\n" + "="*50)
    print("✓✓✓ Global Optimization Successful! ✓✓✓")
    print("The best single RGB Mask + HSL adjustment is:")
    print(f"\n  Mask R Delta:     {best_params[0]:.4f}")
    print(f"  Mask G Delta:     {best_params[1]:.4f}")
    print(f"  Mask B Delta:     {best_params[2]:.4f}")
    print(f"\n  Hue Delta:        {best_params[3]:.4f}")
    print(f"  Saturation Delta: {best_params[4]:.4f}")
    print(f"  Lightness Delta:  {best_params[5]:.4f}")
    print(f"\n  Lowest Average Error (RMSE): {final_error:.4f}")
    print("="*50)

    # RECOLOR THE IMAGE USING THE FOUND TRANSFORMATION
    print("\nApplying the found transformation to the specified rectangle...")
    recolored_image = original_img.copy()
    left, top, right, bottom = RECOLOR_AND_SAMPLE_RECTANGLE

    for x in range(left, right):
        for y in range(top, bottom):
            original_pixel_rgba = original_img.getpixel((x, y))
            if not is_transparent(original_pixel_rgba):
                original_pixel_rgb = original_pixel_rgba[:3]
                # Pass all 6 parameters to the new function
                new_rgb = apply_rgb_and_hsl_transformation(original_pixel_rgb, *best_params)
                new_pixel_rgba = new_rgb + (original_pixel_rgba[3],)
                recolored_image.putpixel((x, y), new_pixel_rgba)
    
    recolored_image.save("recolored_output.png")
    print("✓ Recolor complete. Image saved as 'recolored_output.png'")

else:
    print("\nOptimization failed and could not find a solution.")
    print(result.message)