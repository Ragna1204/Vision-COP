import imagehash
import exifread
from PIL import Image
import os
import cv2
import numpy as np
import io

def verify_image_authenticity(query_image_path, original_candidate_path):
    """
    Comprehensive authenticity verification using multiple methods.
    Returns authenticity score and detailed analysis.

    This provides pixel-level and metadata-based authenticity verification.
    """
    results = {
        'pixel_distance': -1,
        'pixel_status': 'Verification Failed',
        'metadata_match': False,
        'metadata_issues': [],
        'manipulation_score': 0,
        'manipulation_flags': [],
        'overall_confidence': 'Unknown'
    }

    try:
        # Load images
        query_img = Image.open(query_image_path).convert('RGB')
        original_img = Image.open(original_candidate_path).convert('RGB')

        # 1. PERCEPTUAL HASHING (pHash)
        query_hash = imagehash.phash(query_img)
        original_hash = imagehash.phash(original_img)
        pixel_distance = query_hash - original_hash
        results['pixel_distance'] = pixel_distance

        # Determine status based on pixel distance
        if pixel_distance == 0:
            results['pixel_status'] = "Identical"
            results['overall_confidence'] = "Authentic"
        elif pixel_distance <= 5:
            results['pixel_status'] = "Near Identical"
            results['overall_confidence'] = "Authentic Copy"
        elif pixel_distance <= 15:
            results['pixel_status'] = "High Similarity"
            results['overall_confidence'] = "Possibly Modified"
        elif pixel_distance <= 30:
            results['pixel_status'] = "Moderate Similarity"
            results['overall_confidence'] = "Significantly Modified"
        else:
            results['pixel_status'] = "Different Content"
            results['overall_confidence'] = "Different Image"

        # 2. METADATA COMPARISON (EXIF)
        metadata_results = compare_image_metadata(query_image_path, original_candidate_path)
        results['metadata_match'] = metadata_results['match']
        results['metadata_issues'] = metadata_results['issues']

        # 3. MANIPULATION DETECTION
        manip_results = detect_image_manipulation(query_image_path)
        results['manipulation_score'] = manip_results['score']
        results['manipulation_flags'] = manip_results['flags']

        # Final determination
        if pixel_distance == 0 and metadata_results['match']:
            results['overall_confidence'] = "Perfectly Authentic"
        elif pixel_distance <= 15 and not metadata_results['issues']:
            results['overall_confidence'] = "Likely Authentic/Reused"
        elif manip_results['score'] > 0.7:
            results['overall_confidence'] = "Definitely Manipulated"
        elif pixel_distance > 30:
            results['overall_confidence'] = "Different Image"
        elif metadata_results['issues']:
            results['overall_confidence'] = "Metadata Mismatch"
        else:
            results['overall_confidence'] = "Possibly Modified"

        return results

    except Exception as e:
        results['pixel_status'] = f"Error: {e}"
        results['overall_confidence'] = "Verification Failed"
        return results

def compare_image_metadata(query_path, original_path):
    """Compare EXIF metadata between two images."""
    results = {'match': True, 'issues': []}

    try:
        with open(query_path, 'rb') as f1, open(original_path, 'rb') as f2:
            query_tags = exifread.process_file(f1, details=False)
            original_tags = exifread.process_file(f2, details=False)

        # Check key metadata fields
        key_fields = [
            ('Image DateTime', 'EXIF DateTimeOriginal'),
            ('Image Width', 'EXIF ExifImageWidth'),
            ('Image Height', 'EXIF ExifImageLength'),
            ('Camera Make', 'Image Make'),
            ('Camera Model', 'Image Model'),
            ('Software', 'Image Software')
        ]

        for field in key_fields:
            for field_name in field:
                if field_name in original_tags:
                    original_value = str(original_tags[field_name])
                    query_value = str(query_tags.get(field_name, 'Missing'))

                    if original_value != query_value:
                        results['issues'].append(f"{field[0]}: {original_value} → {query_value}")
                        results['match'] = False
                    break

        if results['issues']:
            results['match'] = False

    except Exception as e:
        results['issues'].append(f"Metadata read error: {e}")

    return results

def detect_image_manipulation(image_path):
    """Detect signs of image manipulation."""
    results = {'score': 0.0, 'flags': []}

    try:
        img = cv2.imread(image_path)
        if img is None:
            return results

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Check for unusual brightness patterns (sign of cloning/retouching)
        brightness_std = np.std(gray)
        if brightness_std < 30:  # Too uniform
            results['score'] += 0.3
            results['flags'].append("Unusually uniform brightness")
        elif brightness_std > 80:  # Too variable
            results['score'] += 0.2
            results['flags'].append("Highly variable brightness")

        # 2. Check for JPEG artifacts (re-compression signs)
        height, width = gray.shape
        if height > 100 and width > 100:
            # Check for blocking artifacts
            block_size = 8
            if (height % block_size == 0) and (width % block_size == 0):
                results['score'] += 0.2
                results['flags'].append("JPEG blocking artifacts detected")

        # 3. Check color histogram consistency
        channels = cv2.split(img)
        for i, channel in enumerate(channels):
            hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
            # Check for unnatural histogram peaks/spikes
            max_val = np.max(hist)
            if max_val > 0.1 * np.sum(hist):  # More than 10% in one bin
                results['score'] += 0.1
                results['flags'].append(f"Unnatural color distribution in channel {i}")

        # 4. Error Level Analysis (simple version)
        try:
            pil_img = Image.open(image_path).convert('RGB')
            buffer = io.BytesIO()
            pil_img.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            compressed = Image.open(buffer)

            diff = np.abs(np.array(pil_img) - np.array(compressed))
            ela_score = np.mean(diff) / 255.0
            if ela_score > 0.05:
                results['score'] += ela_score
                results['flags'].append(f"ELA indicates manipulation (score: {ela_score:.3f})")
        except:
            pass

        # Cap score at 1.0
        results['score'] = min(results['score'], 1.0)

        return results

    except Exception as e:
        results['flags'].append(f"Manipulation detection error: {e}")
        return results

def get_verification_status(results_dict):
    """Get color coding and simplified status based on comprehensive results."""
    confidence = results_dict.get('overall_confidence', 'Unknown')

    if confidence in ['Perfectly Authentic', 'Authentic', 'Authentic Copy']:
        return confidence, "#27ae60"  # Green
    elif confidence == 'Likely Authentic/Reused':
        return confidence, "#f39c12"  # Orange
    elif confidence in ['Definitely Manipulated', 'Metadata Mismatch', 'Possibly Modified']:
        return confidence, "#e74c3c"  # Red
    else:
        return confidence, "#95a5a6"  # Gray

def calculate_image_hash(image_path):
    """Calculate perceptual hash for an image file."""
    try:
        img = Image.open(image_path)
        phash = imagehash.phash(img)
        return phash
    except Exception as e:
        print(f"Error calculating hash for {image_path}: {e}")
        return None
