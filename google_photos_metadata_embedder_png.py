import os
import json
from datetime import datetime, timezone

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
            json_path = image_path + '.supplemental-metadata.json' # Assuming this specific JSON naming convention

            # Skip if no associated JSON metadata file is found
            if not os.path.exists(json_path):
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
    # IMPORTANT: Change this path to your Google Photos Takeout folder or specific subfolder!
    base_folder = "/Volumes/PKP-Salim/Photos2/Takeout/Google Photos/Photos from 2025"
    process_pngs(base_folder)

    # SUCCESS!!