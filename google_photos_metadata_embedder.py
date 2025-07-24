import os
import json
from datetime import datetime, timezone
import piexif
from PIL import Image, PngImagePlugin

def is_image(filename):
    """Checks if the file is an image based on its extension and not a macOS '._' file."""
    return filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) and not os.path.basename(filename).startswith("._")

def is_jpeg(filename):
    """Checks if the file is a JPEG."""
    return filename.lower().endswith(('.jpg', '.jpeg'))

def is_png(filename):
    """Checks if the file is a PNG."""
    return filename.lower().endswith('.png')

def find_json_file(media_path):
    """
    Attempts to find the Google Photos metadata JSON file associated with a media file.
    Checks for .supplemental-metadata.json and .suppl.json suffixes.
    """
    candidates = [
        media_path + '.supplemental-metadata.json',
        media_path + '.suppl.json'
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def read_json_metadata(json_path):
    """
    Reads the JSON metadata file and extracts the photo taken time.
    Converts timestamp to a formatted datetime string.
    """
    try:
        with open(json_path, 'r') as f:
            metadata = json.load(f)
        if 'photoTakenTime' in metadata and 'timestamp' in metadata['photoTakenTime']:
            ts = int(metadata['photoTakenTime']['timestamp'])
            dt = datetime.fromtimestamp(ts, timezone.utc)
            dt_str = dt.strftime('%Y:%m:%d %H:%M:%S')
            return metadata, dt_str
        return metadata, None
    except Exception as e:
        print(f"⚠️ Failed to read JSON {json_path}: {e}")
        return None, None

def add_gps_info(exif_dict, lat, lng, alt):
    """
    Adds GPS information (latitude, longitude, altitude) to the EXIF dictionary.
    Converts decimal coordinates to degrees, minutes, seconds format for EXIF.
    """
    def to_deg(value):
        abs_val = abs(value)
        deg = int(abs_val)
        min_float = (abs_val - deg) * 60
        min = int(min_float)
        sec = round((min_float - min) * 60 * 10000)
        return ((deg, 1), (min, 1), (sec, 10000))

    gps_ifd = {}
    if lat is not None and lng is not None:
        gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
        gps_ifd[piexif.GPSIFD.GPSLatitude] = to_deg(lat)
        gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = b'E' if lng >= 0 else b'W'
        gps_ifd[piexif.GPSIFD.GPSLongitude] = to_deg(lng)
    if alt is not None:
        gps_ifd[piexif.GPSIFD.GPSAltitude] = (int(alt * 100), 100)
        gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if alt >= 0 else 1
    exif_dict['GPS'] = gps_ifd

def embed_full_exif_jpeg(image_path, json_data, datetime_str):
    """
    Embeds full EXIF metadata (time, GPS, UserComment) into a JPEG image.
    Modifies the image file in place.
    """
    try:
        exif_dict = piexif.load(image_path)

        # Set time
        if datetime_str:
            encoded = datetime_str.encode('utf-8')
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = encoded
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = encoded
            exif_dict['0th'][piexif.ImageIFD.DateTime] = encoded

        # Set GPS if available
        geo = json_data.get("geoDataExif") or json_data.get("geoData")
        if geo:
            lat = geo.get("latitude")
            lng = geo.get("longitude")
            alt = geo.get("altitude")
            if lat is not None and lng is not None:
                add_gps_info(exif_dict, lat, lng, alt)

        # Set UserComment as a JSON string of selected metadata
        try:
            short_json = {
                "device": json_data.get("googlePhotosOrigin", {}).get("mobileUpload", {}).get("deviceType"),
                "url": json_data.get("url"),
                "imageViews": json_data.get("imageViews")
            }
            user_comment = json.dumps(short_json)
            exif_dict['Exif'][piexif.ExifIFD.UserComment] = user_comment.encode('utf-8')
        except Exception as ue:
            print(f"⚠️ Failed to set UserComment: {ue}")

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)
        return True
    except Exception as e:
        print(f"⚠️ Failed to embed full EXIF into {image_path}: {e}")
        return False

def embed_metadata_png(image_path, json_data, datetime_str):
    """
    Embeds selected metadata into a PNG image using tEXt chunks.
    PNGs do not support EXIF directly like JPEGs.
    """
    try:
        im = Image.open(image_path)
        meta = PngImagePlugin.PngInfo()

        # Example metadata inserted into 'UserComment' tEXt chunk
        short_json = {
            "dateTimeOriginal": datetime_str,
            "device": json_data.get("googlePhotosOrigin", {}).get("mobileUpload", {}).get("deviceType"),
            "url": json_data.get("url"),
            "imageViews": json_data.get("imageViews")
        }
        user_comment = json.dumps(short_json)
        meta.add_text("UserComment", user_comment)

        # Save again with inserted metadata
        im.save(image_path, "PNG", pnginfo=meta)
        return True
    except Exception as e:
        print(f"⚠️ Failed to embed PNG metadata into {image_path}: {e}")
        return False

def process_directory(directory):
    """
    Walks through the specified directory, finds image files and their
    associated JSON metadata, and embeds the metadata into the images.
    Logs the success/failure of each operation.
    """
    successful_images, failed_images = [], []
    with open("embed_log.txt", "w") as log_file:
        for root, _, files in os.walk(directory):
            for file in files:
                if is_image(file):
                    media_path = os.path.join(root, file)
                    print(f"🖼️ Checking and embedding metadata: {media_path}")
                    json_path = find_json_file(media_path)
                    if json_path:
                        metadata, dt_str = read_json_metadata(json_path)
                        if metadata:
                            if is_jpeg(media_path):
                                success = embed_full_exif_jpeg(media_path, metadata, dt_str)
                            elif is_png(media_path):
                                success = embed_metadata_png(media_path, metadata, dt_str)
                            else:
                                print(f"⚠️ Format {media_path} is not supported for EXIF metadata embedding.")
                                success = False # Mark as failed if format is not supported
                            if success:
                                successful_images.append(media_path)
                                log_file.write(f"IMAGE EMBEDDED SUCCESSFULLY: {media_path} with date/time {dt_str}\n")
                            else:
                                failed_images.append(media_path)
                                log_file.write(f"IMAGE EMBEDDING FAILED: {media_path}\n")
                        else:
                            failed_images.append(media_path)
                            log_file.write(f"FAILED TO READ JSON METADATA: {json_path}\n")
                    else:
                        failed_images.append(media_path)
                        log_file.write(f"NO JSON METADATA FILE FOUND: {media_path}\n")
    print(f"✅ Done. Successful: {len(successful_images)}, Failed: {len(failed_images)}")

if __name__ == "__main__":
    # IMPORTANT: Change this path to your Google Photos Takeout folder!
    base_folder = "/Volumes/PKP-Salim/Photos2/Takeout/Google Photos" 
    process_directory(base_folder)
    # SUCCESS!!