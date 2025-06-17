import os
import re
import argparse

def rename_files_with_offset(dir_path, file_pattern, offset):
    """
    Finds all files in a directory matching a pattern, extracts a number,
    adds an offset to it, and renames the file.

    Args:
        dir_path (str): The path to the directory containing the files.
        file_pattern (str): A regex pattern to match files. It must contain
                           one capturing group for the number.
        offset (int): The integer offset to add to the extracted number.
    """
    if not os.path.isdir(dir_path):
        print(f"Error: Directory not found at '{dir_path}'")
        return

    # Compile the regular expression for efficiency
    try:
        # We expect a pattern with one integer capturing group, e.g., r'pattern (\d+)'
        pattern = re.compile(file_pattern)
    except re.error as e:
        print(f"Error: Invalid regular expression pattern: {e}")
        return

    # Create a list of files to rename to avoid issues while iterating
    files_to_process = []
    for fname in os.listdir(dir_path):
        match = pattern.match(fname)
        if match:
            try:
                # The first (and only) captured group should be the number
                num_str = match.group(1)
                num = int(num_str)
                files_to_process.append((fname, num_str, num))
            except (IndexError, ValueError):
                # This happens if the pattern has no capturing group or it's not a number
                print(f"Warning: Pattern matched '{fname}', but couldn't extract a number. Skipping.")
                continue
    
    # Sort files to rename them in a consistent order (optional but good practice)
    # Sorting by the number ensures that 10 comes after 9, not after 1.
    files_to_process.sort(key=lambda x: x[2])

    # Rename the files
    for fname, num_str, num in files_to_process:
        new_num = num + offset
        # Create the new filename by replacing the original number string
        new_fname = fname.replace(num_str, str(new_num), 1)

        old_file_path = os.path.join(dir_path, fname)
        new_file_path = os.path.join(dir_path, new_fname)

        try:
            os.rename(old_file_path, new_file_path)
            print(f"Renamed '{fname}' to '{new_fname}'")
        except OSError as e:
            print(f"Error renaming '{fname}': {e}")


def main():
    """
    Main function to parse command-line arguments and run the renaming script.
    """
    parser = argparse.ArgumentParser(
        description="Rename files by adding an integer offset to a number in their names.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "dir_path",
        type=str,
        help="Path to the directory with files to rename."
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="Regular expression pattern to identify files.\n"
             "This pattern MUST contain one capturing group `(\\d+)` for the number.\n"
    )
    parser.add_argument(
        "offset",
        type=int,
        help="The integer offset to add to the file numbers (can be positive or negative)."
    )

    args = parser.parse_args()
    rename_files_with_offset(args.dir_path, args.file_pattern, args.offset)

if __name__ == '__main__':
    main()