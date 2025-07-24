# 📸 Google Photos Metadata Embedder

This tool embeds metadata from **Google Photos Takeout** `.json` files into your original image files (`.jpg`, `.jpeg`, `.png`). It restores lost metadata like **photo taken date**, **GPS location**, and **upload source** into the image files, making them usable in photo organization apps again.

---

## 🎯 Background

When exporting your media library from **Google Photos via Takeout**, the image files lose their embedded metadata such as the date taken and GPS location. Instead, this metadata is placed into adjacent `.json` files.

This becomes a problem when you want to import the files into other photo management software such as:

- 📁 **Synology Photos**
- 📱 **Apple Photos**
- 🖼️ **Windows Photos App**

These applications typically rely on EXIF metadata to organize your photos chronologically or geographically. Without this metadata, all your images may appear incorrectly sorted by file system modification date.

**This script solves the problem by embedding the original metadata back into each photo**, ensuring compatibility with Synology Photos and other gallery apps.

---

## ✨ Features

- 🔍 Automatically matches images with their Google Photos JSON metadata
- 🕒 Embeds photo taken time into EXIF (`DateTimeOriginal`, etc.)
- 📍 Embeds GPS coordinates (latitude, longitude, altitude)
- 📱 Embeds upload source device and image view count as `UserComment`
- 📂 Recursively processes folders (ideal for Google Takeout exports)
- 📝 Creates a log file (`embed_log.txt`) summarizing all results

---

## 🧪 Supported Formats

| File Type           | Metadata Embedding                   | Notes                                         |
| ------------------- | ------------------------------------ | --------------------------------------------- |
| `.jpg`, `.jpeg` | ✅ Full EXIF support via `piexif`  | Time, GPS, and user comment                   |
| `.png`            | ✅ tEXt chunk support via `Pillow` | PNG doesn't use EXIF; metadata stored in tEXt |
| `.gif`            | ❌ Not supported for embedding       | Skipped                                       |
| Other               | ❌ Skipped                           | Must be `.jpg`, `.jpeg`, or `.png`      |

---

## 📦 Installation

Clone the repository and install required packages:

```bash
git clone https://github.com/yourusername/google-photos-metadata-embedder.git
cd google-photos-metadata-embedder
pip install -r requirements.txt
```

### `requirements.txt`

```txt
piexif
pillow
```

---

## 🚀 Usage

```bash
python google_photos_metadata_embedder.py /path/to/Google_Photos_directory
```

### Positional Arguments

- `/path/to/Google_Photos_directory`: The root folder from your Google Takeout download (e.g., `"Google Photos"`). The script will recursively walk through all subfolders.

### Example

```bash
python google_photos_metadata_embedder.py "/Users/yourname/Downloads/Takeout/Google Photos"
```

---

## 🗂 Folder Structure Example

```
Google Photos/
├── IMG_001.jpg
├── IMG_001.jpg.json
├── Vacation/
│   ├── IMG_002.png
│   ├── IMG_002.png.supplemental-metadata.json
└── Event/
    ├── IMG_003.jpeg
    ├── IMG_003.jpeg.suppl.json
```

The script will automatically search for matching `.json`, `.supplemental-metadata.json`, or `.suppl.json` files for each image.

---

## 🧠 What Metadata is Embedded?

### JPEG (`.jpg`, `.jpeg`)

| Tag                                                       | Description                                        |
| --------------------------------------------------------- | -------------------------------------------------- |
| `DateTimeOriginal`, `DateTimeDigitized`, `DateTime` | The original photo taken time                      |
| `GPSLatitude`, `GPSLongitude`, `GPSAltitude`        | Location info (if available)                       |
| `UserComment`                                           | JSON-encoded custom data (device type, views, URL) |

### PNG (`.png`)

- Metadata is added via PNG `tEXt` chunk named `UserComment` containing:
  ```json
  {
    "dateTimeOriginal": "2023:01:15 14:30:22",
    "device": "ANDROID_PHONE",
    "url": "https://photos.google.com/photo/...",
    "imageViews": 84
  }
  ```

---

## 📑 Output

- A log file named `embed_log.txt` is created in the working directory, listing:
  - ✅ Successfully embedded images
  - ❌ Failed or unsupported files
  - ⚠️ JSON metadata not found

---

## 🔒 Limitations

- This tool **does not modify** `.gif`, `.webp`, or unsupported formats.
- Some image viewers may not fully read custom fields like `UserComment`.
- Very large `UserComment` values may be truncated.

---

## 👨‍💻 Developer Notes

- Uses `piexif` to insert EXIF data for JPEGs
- Uses `PIL.Image` and `PngInfo` for PNG metadata
- Recursively processes all subdirectories
- Removes `.DS_Store` or macOS `._` hidden files

---

## 📜 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork the repository and submit a pull request.

---

## 🙏 Acknowledgements

- Google Takeout team for providing media metadata
- [`piexif`](https://github.com/hMatoba/Piexif) for EXIF manipulation
- [`Pillow`](https://python-pillow.org/) for image processing

---

## 📂 Additional Script: PNG Timestamp Restorer

# 🕒 PNG Timestamp Restorer from Google Photos Takeout

This Python script restores the **original timestamp** (creation/modification time) of `.png` image files using the metadata exported by **Google Photos Takeout**.

Google Photos stores the actual timestamp in adjacent `.json` files, while the exported image file itself loses the proper metadata. This script updates the file system timestamp so that image viewers (like Synology Photos, Windows Photos, or Apple Photos) display the **correct photo date**.

---

## ✅ What It Does

- Scans a directory recursively for `.png` files
- Searches for associated JSON metadata (`.supplemental-metadata.json`)
- Extracts the photo's original timestamp from the JSON file
- Updates the PNG file's access & modification time accordingly

---

## 📦 Requirements

This script requires **Python 3.6+** and uses only standard libraries. No installation is needed for external packages.

### Python Standard Libraries Used:

- `os`
- `json`
- `datetime`

---

1.

## 🚀 Usage

```bash
python google_photos_metadata_embedder_png.py /path/to/Google_Photos_directory
```

### Positional Arguments

- `/path/to/Google_Photos_directory`: The root folder from your Google Takeout download (e.g., `"Google Photos"`). The script will recursively walk through all subfolders.

### Example

```bash
python google_photos_metadata_embedder_png.py "/Users/yourname/Downloads/Takeout/Google Photos"
```


---

## 🗂 Example Folder Structure

```
Photos from 2025/
├── IMG_001.png
├── IMG_001.png.supplemental-metadata.json
├── Vacation/
│   ├── IMG_002.png
│   ├── IMG_002.png.supplemental-metadata.json
```

Each `.png` should have an accompanying `.supplemental-metadata.json` file. If not, the image will be skipped.

---

## 🧪 Output Summary

After running, you will get a summary of:

- 🟢 Number of PNGs successfully timestamped
- 🔴 Number of failures
- ⚪ Files skipped due to missing metadata

---

## 🧠 Why This Matters

Applications like **Synology Photos**, **macOS Finder**, or **Windows Explorer** often rely on the file system timestamp when there's no EXIF data (as in PNGs). If you're importing old photos exported from Google Photos, restoring timestamps is critical for **chronological sorting and display**.

---

## 📝 License

This project is licensed under the MIT License.
