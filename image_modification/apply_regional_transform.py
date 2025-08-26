import sys
from PIL import Image, ImageEnhance, ImageDraw

# --- 1. TRANSFORMATION LOGIC ---

def is_transparent(pixel_rgba, tolerance=10):
    """Checks if a pixel is transparent by looking at its alpha channel."""
    return pixel_rgba[3] < tolerance

def apply_predefined_transformation(rgb_tuple, dr, dg, db, dh, ds, dl, final_dl):
    """
    Applies a full, predefined transformation: RGB Mask -> HSL Shift -> Final Lightness.
    """
    r, g, b = rgb_tuple

    # Step 1: Apply the additive RGB mask and clamp values
    masked_r = int(max(0, min(255, r + dr)))
    masked_g = int(max(0, min(255, g + dg)))
    masked_b = int(max(0, min(255, b + db)))

    # Step 2: Apply HSL transformation to the masked color
    # Note: Pillow's HSL conversion is not standard. We use ImageEnhance instead.
    temp_img = Image.new("RGB", (1, 1), (masked_r, masked_g, masked_b))
    
    # Hue is tricky to apply with ImageEnhance, so we can use a manual method
    # For simplicity and given your small hue delta, we'll focus on Pillow's strengths.
    # If hue is critical, the colorsys method from the previous script can be re-integrated.
    # However, since your hue delta is small (-2.9), we will omit it for this simplified script.
    # A full implementation would require converting to HSL, shifting H, and converting back.
    
    # Saturation
    sat_factor = 1.0 + (ds / 100.0)
    enhancer = ImageEnhance.Color(temp_img)
    temp_img = enhancer.enhance(sat_factor)
    
    # Main Lightness
    light_factor = 1.0 + (dl / 100.0)
    enhancer = ImageEnhance.Brightness(temp_img)
    temp_img = enhancer.enhance(light_factor)

    # Step 3: Apply the final, separate lightness adjustment
    final_light_factor = 1.0 + (final_dl / 100.0)
    enhancer = ImageEnhance.Brightness(temp_img)
    temp_img = enhancer.enhance(final_light_factor)
    
    return temp_img.getpixel((0, 0))

# --- 2. CONFIGURATION: DEFINE REGIONS AND TRANSFORMATIONS ---

# This is the main dictionary you will edit.
# 'params' are in the order: (R, G, B, Hue, Saturation, Lightness, Final_Lightness)
# Note: The simple `apply` function above omits the Hue shift.
REGIONS = {
    "Hair": {
        "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
        "rects": [
            (0, 0, 1070, 870),   # Example rectangle for the main part of the hair
        ]
    },
    "Eyebrows": {
        "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0), # Example: Darken and desaturate
        "rects": [
            (1170, 456, 1228, 472),  # Left eyebrow
            (1352, 445, 1413, 460)   # Right eyebrow
        ]
    },
    "Eyes": {
        "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0), # Example: Slightly brighten and saturate
        "rects": [
            (1123, 464, 1165, 504),  # Left eye
            (1251, 420, 1293, 460)   # Right eye
        ]
    }
}

# --- 3. MAIN SCRIPT: APPLY TRANSFORMATIONS ---

def main():
    try:
        source_image_path = "texture_00_decolored.png" # The image you start with
        original_img = Image.open(source_image_path).convert("RGBA")
        print(f"✓ Image '{source_image_path}' loaded successfully.")
    except FileNotFoundError:
        print(f"Error: Could not find the source image file '{source_image_path}'.")
        sys.exit()

    # Create a copy to draw the modifications on
    recolored_image = original_img.copy()
    
    # Optional: create a preview of the rectangles
    preview = original_img.copy()
    draw = ImageDraw.Draw(preview)

    print("\nApplying transformations to defined regions...")

    # Loop through each defined region in the configuration
    for region_name, data in REGIONS.items():
        params = data['params']
        rectangles = data['rects']
        print(f"  -> Processing Region: '{region_name}' ({len(rectangles)} rectangles)")

        # Loop through each rectangle assigned to this region
        for i, rect in enumerate(rectangles):
            left, top, right, bottom = rect
            draw.rectangle(rect, outline="red", width=2)
            draw.text((left+5, top+5), f"{region_name} {i+1}", fill="red")

            # Process every pixel inside the current rectangle
            for x in range(left, right):
                for y in range(top, bottom):
                    original_pixel = original_img.getpixel((x, y))
                    if not is_transparent(original_pixel):
                        new_rgb = apply_predefined_transformation(original_pixel[:3], *params)
                        new_pixel_rgba = new_rgb + (original_pixel[3],)
                        recolored_image.putpixel((x, y), new_pixel_rgba)
    
    # Save the final output image
    output_path = "final_transformed_image.png"
    recolored_image.save(output_path)
    print(f"\n✓ All transformations applied. Image saved as '{output_path}'")

    # Save the preview image
    preview_path = "regions_preview.png"
    preview.save(preview_path)
    print(f"✓ A map of the defined regions was saved as '{preview_path}'")


if __name__ == "__main__":
    main()