import sys
import colorsys
from PIL import Image, ImageEnhance, ImageDraw

# --- IMAGE TRANSFORMATION ---
def is_transparent(pixel_rgba, tolerance=10):
    """Check if a pixel is transparent by looking at its alpha channel."""
    return pixel_rgba[3] < tolerance

def apply_transformation(rgb_tuple, dr, dg, db, dh, ds, dl, final_dl):
    """
    Apply a full transformation: RGB Mask -> HSL Shift -> Final Lightness.
    """
    r, g, b = rgb_tuple

    # Apply RGB mask
    masked_r = int(max(0, min(255, r + dr)))
    masked_g = int(max(0, min(255, g + dg)))
    masked_b = int(max(0, min(255, b + db)))

    # Apply HSL transformations
    # Hue
    temp_img = Image.new("RGB", (1, 1), (masked_r, masked_g, masked_b))
    r, g, b = temp_img.getpixel((0, 0))
    r_norm, g_norm, b_norm = [x / 255.0 for x in (r, g, b)]
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    new_h = (h + dh / 360.0) % 1.0
    r_norm, g_norm, b_norm = colorsys.hls_to_rgb(new_h, l, s)
    r, g, b = [int(x * 255) for x in (r_norm, g_norm, b_norm)]
    temp_img.putpixel((0, 0), (r, g, b))
    
    # Saturation
    sat_factor = 1.0 + (ds / 100.0)
    enhancer = ImageEnhance.Color(temp_img)
    temp_img = enhancer.enhance(sat_factor)
    
    # Lightness
    light_factor = 1.0 + (dl / 100.0)
    enhancer = ImageEnhance.Brightness(temp_img)
    temp_img = enhancer.enhance(light_factor)

    # Final lightness adjustment
    final_light_factor = 1.0 + (final_dl / 100.0)
    enhancer = ImageEnhance.Brightness(temp_img)
    temp_img = enhancer.enhance(final_light_factor)
    
    return temp_img.getpixel((0, 0))

# --- TRANSFORMATION REGIONS DEFINITION ---
# Defined per texture file

REGIONS_PER_FILE = {
    102001: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 815, 800), # (top left x, top left y, bottom right x, bottom right y)
                (815, 0, 1041, 650), 
                (278, 800, 594, 870)
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1093, 452, 1153, 473),
                (1277, 445, 1340, 461)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1047, 461, 1089, 506),
                (1178, 420, 1217, 460)
            ]
        }
    },
    102002: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 1079, 900), # (top left x, top left y, bottom right x, bottom right y)
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1170, 452, 1228, 477),
                (1351, 444, 1414, 460)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1120, 462, 1165, 506),
                (1253, 420, 1293, 460)
            ]
        }
    },
    102003: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 716, 859),
                (716, 0, 875, 709),
                (875, 0, 959, 601),
                (850, 601, 921, 640),
                (959, 0, 1039, 501),
                (959, 501, 1008, 641),
                (1008, 600, 1036, 655),
                
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1093, 455, 1156, 475),
                (1277, 445, 1340, 460)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1046, 462, 1088, 505),
                (1176, 421, 1220, 461)
            ]
        }
    },
    102004: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 1070, 870), # (top left x, top left y, bottom right x, bottom right y)
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1170, 456, 1228, 472),
                (1352, 445, 1413, 460)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1123, 464, 1165, 504),
                (1251, 420, 1293, 460)
            ]
        }
    },
    102005: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (283, 0, 857, 650),
                (204, 0, 283, 386),
                (120, 0, 204, 357),
                (0, 0, 120, 334),
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (953, 464, 1013, 477),
                (1137, 452, 1199, 469)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (906, 470, 950, 512),
                (1037, 428, 1097, 467)
            ]
        }
    },
    102006: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 1041, 648),
                (0, 648, 848, 728),
                (0, 728, 609, 828),
                (310, 828, 493, 867),
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1099, 456, 1158, 471),
                (1280, 443, 1345, 459)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1050, 461, 1096, 503),
                (1180, 418, 1223, 458)
            ]
        }
    },
    102007: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 1035, 851),
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1121, 547, 1184, 564),
                (1307, 537, 1369, 552)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1075, 554, 1120, 596),
                (1207, 513, 1248, 552)
            ]
        }
    },
    102008: {
        "Hair": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (0, 0, 961, 872),
                (961, 0, 1039, 659)
            ]
        },
        "Eyebrows": {
            "params": (4.4399, -249.6927, -236.8324, -2.9640, -92.7837, 30.4192, -5.0),
            "rects": [
                (1096, 455, 1155, 474),
                (1277, 444, 1340, 461)
            ]
        },
        "Eyes": {
            "params": (-254.8120, 2.4701, -205.3370, 3.1133, -89.4133, -30.9278, 0),
            "rects": [
                (1046, 461, 1089, 504),
                (1174, 420, 1221, 461)
            ]
        }
    },
}


# --- APPLY TRANSFORMATIONS ---
def main():
    # File IDs to iterate over
    texture_ids = REGIONS_PER_FILE.keys()
    
    for texture_id in texture_ids:
        try:
            source_image_path = f"texture_{texture_id}_decolored.png"
            original_img = Image.open(source_image_path).convert("RGBA")
            print(f"\n✓ Image '{source_image_path}' loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Could not find the source image file '{source_image_path}'.")
            continue
        

        # Draw modifications on a copy
        recolored_image = original_img.copy()

        # Preview modification rectangles
        preview = original_img.copy()
        draw = ImageDraw.Draw(preview)

        print("\nApplying transformations to defined regions...")

        # Modify all regions
        for region_name, data in REGIONS_PER_FILE[texture_id].items():
            params = data['params']
            rectangles = data['rects']
            print(f"  -> Processing Region: '{region_name}' ({len(rectangles)} rectangles)")

            # Loop through all rectangles in the region
            for i, rect in enumerate(rectangles):
                left, top, right, bottom = rect
                draw.rectangle(rect, outline="red", width=2)
                draw.text((left+5, top+5), f"{region_name} {i+1}", fill="red")

                # Process all pixels in the rectangle
                for x in range(left, right):
                    for y in range(top, bottom):
                        original_pixel = original_img.getpixel((x, y))
                        if not is_transparent(original_pixel):
                            new_rgb = apply_transformation(original_pixel[:3], *params)
                            new_pixel_rgba = new_rgb + (original_pixel[3],)
                            recolored_image.putpixel((x, y), new_pixel_rgba)
        
        # Save the final output image
        output_path = f"texture_{texture_id}_transformed.png"
        recolored_image.save(output_path)
        print(f"\n✓ All transformations applied. Image saved as '{output_path}'")

        # Save the preview image
        preview_path = f"texture_{texture_id}_regions_preview.png"
        preview.save(preview_path)
        print(f"✓ A map of the defined regions was saved as '{preview_path}'")


if __name__ == "__main__":
    main()