import os
import shutil
import re
import argparse
from pathlib import Path

def find_texture_id(character_dir: Path) -> str | None:
    """
    Searches within a character directory for a file named with a 6-digit ID.
    This is more reliable than matching folder names.
    """
    # Pattern to find a file starting with a 6-digit number.
    id_pattern = re.compile(r'^(\d{6})\..+')
    
    # We expect to find the ID in the raw_data/MonoBehaviour or raw_data/TextAsset folders
    search_paths = [character_dir / 'raw_data' / 'MonoBehaviour', character_dir / 'raw_data' / 'TextAsset']

    for path in search_paths:
        if path.is_dir():
            for fname in os.listdir(path):
                match = id_pattern.match(fname)
                if match:
                    return match.group(1) # Return the found 6-digit ID
    return None

def consolidate_textures(source_root: str, output_dir: str):
    """
    Copies and renames texture_00.png from character subdirectories
    into a single output directory.
    """
    source_path = Path(source_root)
    output_path = Path(output_dir)

    if not source_path.is_dir():
        print(f"Error: Source directory not found at '{source_root}'")
        return

    # Create the output directory if it doesn't exist
    output_path.mkdir(exist_ok=True)
    print(f"Output will be saved to: {output_path.resolve()}")

    copied_count = 0
    skipped_count = 0

    for item in source_path.iterdir():
        if item.is_dir():
            print(f"\nProcessing directory: {item.name}")
            
            # 1. Find the unique ID for this character/outfit
            texture_id = find_texture_id(item)
            
            if not texture_id:
                print(f"  -> Warning: Could not determine texture ID for '{item.name}'. Skipping.")
                skipped_count += 1
                continue

            # 2. Find the source texture_00.png
            source_texture = item / 'raw_data' / 'Texture2D' / 'texture_00.png'

            if not source_texture.is_file():
                print(f"  -> Warning: 'texture_00.png' not found in '{item.name}'. Skipping.")
                skipped_count += 1
                continue

            # 3. Define the destination path and copy the file
            dest_filename = f"texture_{texture_id}.png"
            dest_texture = output_path / dest_filename

            try:
                shutil.copyfile(source_texture, dest_texture)
                print(f"  -> Success: Copied '{dest_filename}'")
                copied_count += 1
            except Exception as e:
                print(f"  -> Error copying file for ID {texture_id}: {e}")
                skipped_count += 1
    
    print(f"\n--- Process Complete ---")
    print(f"Successfully copied {copied_count} textures.")
    print(f"Skipped {skipped_count} directories.")


def main():
    """
    Main function to parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Consolidates source textures.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "source_dir",
        type=str,
        help="Path to the root directory"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Path to the directory where the renamed textures will be saved."
    )

    args = parser.parse_args()
    consolidate_textures(args.source_dir, args.output_dir)

if __name__ == '__main__':
    main()