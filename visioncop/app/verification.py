import hashlib
import imagehash
import exifread
from PIL import Image
import numpy as np

def calculate_sha256(image_path):
    """Calculate SHA256 hash of an image file."""
    with open(image_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash

def perceptual_hash(image_path):
    """Calculate perceptual hash (phash) for similarity detection."""
    image = Image.open(image_path)
    phash = imagehash.phash(image)
    return str(phash)

def extract_exif(image_path):
    """Extract EXIF metadata from an image."""
    with open(image_path, "rb") as f:
        tags = exifread.process_file(f)
    
    exif_data = {}
    for tag in tags.keys():
        if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
            exif_data[tag] = str(tags[tag])
    return exif_data

def error_level_analysis(image_path):
    """Perform Error Level Analysis (ELA) to detect image manipulation."""
    # Stub: Basic implementation for ELA score
    original = Image.open(image_path).convert('RGB')
    # Compress and compare to original to estimate manipulation score (0-100)
    # For now, return a dummy score
    manipulation_score = np.random.randint(0, 100)
    return manipulation_score

def verify_image(image_path):
    """Verify and return comprehensive image metadata."""
    metadata = {
        "sha256": calculate_sha256(image_path),
        "phash": perceptual_hash(image_path),
        "exif": extract_exif(image_path),
        "manipulation_score": error_level_analysis(image_path)
    }
    return metadata

# Optional: Blockchain hash placeholder
def blockchain_hash(image_bytes):
    """Return SHA256 hash for blockchain authenticity (placeholder)."""
    return calculate_sha256(image_bytes)
