from PIL import Image, ImageFilter
import numpy as np
import cv2
from io import BytesIO

def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess image for analysis."""
    image = Image.open(image_path).convert('RGB')
    image = image.resize(target_size, Image.Resampling.LANCZOS)
    return np.array(image)

def error_level_analysis_detailed(image_path, quality=90):
    """Detailed Error Level Analysis for manipulation detection."""
    original = Image.open(image_path).convert('RGB')
    
    # Save image at reduced quality
    buffer = BytesIO()
    original.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    compressed = Image.open(buffer)
    
    # Calculate absolute difference
    diff = np.abs(np.array(original) - np.array(compressed)).astype(np.uint8)
    
    # Return average difference as manipulation score (0-255)
    manipulation_score = np.mean(diff)
    
    return manipulation_score

def detect_edges(image_path):
    """Detect edges for forensic analysis."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return edges

def image_histogram(image_path):
    """Generate color histogram for image analysis."""
    image = Image.open(image_path).convert('RGB')
    histogram = image.histogram()
    return histogram

def resize_and_save(image: Image.Image, output_path, size=(224, 224)):
    """Resize image and save to disk."""
    resized = image.resize(size, Image.Resampling.LANCZOS)
    resized.save(output_path)

# Additional stubs for future forensic analysis
def check_compression_artifacts(image_path):
    """Stub: Check for JPEG compression artifacts."""
    # TODO: Implement artifact detection
    return True

def estimate_creation_tool(image_path):
    """Stub: Estimate image creation tool from metadata."""
    # TODO: Machine learning based tool detection
    return "Unknown"
