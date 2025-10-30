import imagehash
from PIL import Image
import os

def verify_image_authenticity(query_image_path, original_candidate_path):
    """
    Compares two images using Perceptual Hashing (pHash) to detect manipulation or re-use.
    Returns the difference (Hamming Distance).

    This provides pixel-level authenticity verification alongside semantic similarity.
    """
    try:
        # Load images
        query_img = Image.open(query_image_path)
        original_img = Image.open(original_candidate_path)

        # Calculate pHashes
        query_hash = imagehash.phash(query_img)
        original_hash = imagehash.phash(original_img)

        # Calculate the Hamming Distance (how many bits are different)
        # Lower distance means higher similarity at a pixel-structure level.
        distance = query_hash - original_hash

        # Define thresholds for verification flagging
        if distance == 0:
            return distance, "Perfect match (Identical file or exact copy)."
        elif distance <= 8:
            return distance, "High similarity (Re-used, resized, or re-compressed)."
        elif distance <= 20:
            return distance, "Potential manipulation (Cropping, filtering, or minor edit detected)."
        else:
            return distance, "Visual difference is high (Likely a different image or major edit)."

    except Exception as e:
        return -1, f"Error during verification: {e}"

def calculate_image_hash(image_path):
    """
    Calculate perceptual hash for an image file.
    Used for authenticity verification.
    """
    try:
        img = Image.open(image_path)
        phash = imagehash.phash(img)
        return phash
    except Exception as e:
        print(f"Error calculating hash for {image_path}: {e}")
        return None

def get_verification_status(distance):
    """
    Get a human-readable status based on Hamming distance.
    """
    if distance == 0:
        return "Authentic", "green"
    elif distance <= 8:
        return "High Similarity", "orange"
    elif distance <= 20:
        return "Potential Manipulation", "red"
    elif distance > 20:
        return "Different Image", "gray"
    else:
        return "Verification Failed", "black"
