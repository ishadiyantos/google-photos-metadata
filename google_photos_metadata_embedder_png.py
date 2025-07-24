import os
import json
from datetime import datetime, timezone
import argparse # Import the argparse module

def find_json_file(media_path):
    """
    Attempts to find the Google Photos metadata JSON file associated with a media file.
    Checks for .supplemental-metadata.json, .suppl.json, and .json suffixes.
    This function is adapted from the more comprehensive script for better robustness.
    """
    candidates = [
        media_path + '.supplemental-metadata.json',
        media_path + '.suppl.json',
        media_path + '.json' # Added as a common Google Takeout JSON naming convention
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def get_photo_timestamp(json_path):
    """
    Reads the JSON metadata file to extract the photo's original timestamp.
    Returns the Unix timestamp (integer) or None if not found/error.
    """
    try:
        with open(json_path, 'r') as f:
            metadata = json.load(f)
        if 'photoTakenTime' in metadata and 'timestamp' in metadata['photoTakenTime']:
            ts = int(metadata['photoTakenTime']['timestamp'])
            return ts
        else:
            print(f"❌ No 'photoTakenTime' found in: {json_path}")
            return None
    except Exception as e:
        print(f"⚠️ Failed to read JSON {json_path}: {e}")
        return None

def update_file_timestamp(file_path, new_timestamp):
    """
    Updates the access and modification times of a file.
    Uses os.utime() to set the timestamp.
    """
    try:
        # os.utime expects (access_time, modification_time)
        # We set both to the photo's original timestamp
        os.utime(file_path, (new_timestamp, new_timestamp))
        return True
    except Exception as e:
        print(f"⚠️ Failed to change file timestamp: {file_path} ➤ {e}")
        return False

def process_pngs(base_dir):
    """
    Walks through the specified base directory to find PNG files and their
    associated JSON metadata, then updates the PNG file's timestamp.
    """
    print(f"🔍 Processing PNGs in: {base_dir}")
    success, failed, skipped = [], [], []
    for root, _, files in os.walk(base_dir):
        for file in files:
            # Skip files that are not PNGs
            if not file.lower().endswith('.png'):
                continue

            image_path = os.path.join(root, file)
            
            # Use the more robust find_json_file function to locate the JSON
            json_path = find_json_file(image_path)

            # Skip if no associated JSON metadata file is found
            if not json_path: # `find_json_file` returns None if not found
                skipped.append(image_path)
                print(f"⏭️ No JSON metadata found for: {file}")
                continue

            # Get the timestamp from the JSON file
            ts = get_photo_timestamp(json_path)
            if ts is None:
                failed.append(image_path)
                continue # Skip to the next file if timestamp could not be retrieved

            # Update the PNG file's timestamp
            if update_file_timestamp(image_path, ts):
                success.append(image_path)
                # For logging, convert timestamp back to readable date/time string
                dt = datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                print(f"✅ Timestamp updated: {file} ➤ {dt}")
            else:
                failed.append(image_path) # Add to failed list if update_file_timestamp fails

    print("\n=== SUMMARY ===")
    print(f"🟢 Timestamps successfully updated: {len(success)}")
    print(f"🔴 Failed: {len(failed)}")
    print(f"⚪ Skipped (no JSON found): {len(skipped)}")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Updates the file system timestamp (modification/access time) of PNG files "
                    "based on the 'photoTakenTime' in their associated Google Photos Takeout JSON metadata."
    )
    parser.add_argument(
        'base_folder',
        help='Path to the root directory containing your Google Photos Takeout data (e.g., the "Google Photos" folder) '
             'or a specific subfolder within it.'
    )
    args = parser.parse_args()

    # The base_folder will now be taken from the command-line argument
    process_pngs(args.base_folder)
    # print("SUCCESS!!")