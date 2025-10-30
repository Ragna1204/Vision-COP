import pytest
import numpy as np
from app.cbir import load_clip_model, extract_embedding, create_faiss_index, load_faiss_index
from app.verification import calculate_sha256, perceptual_hash
from app.utils.image_utils import preprocess_image
from PIL import Image
import os

# Create a temporary test image
@pytest.fixture
def test_image():
    """Create a temporary test image file."""
    img = Image.new('RGB', (224, 224), color=(73, 109, 137))
    filepath = "test_embed_image.jpg"
    img.save(filepath)
    yield filepath
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)

def test_extract_embedding(test_image):
    """Test CLIP embedding extraction."""
    embedding = extract_embedding(test_image)
    
    # Check embedding shape and normalization
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (512,)
    # Check normalization
    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 1e-5

def test_faiss_index_operations():
    """Test FAISS index creation and operations."""
    # Create index
    index = create_faiss_index()
    
    # Add some dummy embeddings
    embeddings = np.random.rand(10, 512).astype('float32')
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)  # Normalize
    
    index.add(embeddings)
    assert index.ntotal == 10
    
    # Search for similar
    query = np.random.rand(1, 512).astype('float32')
    query /= np.linalg.norm(query)
    distances, indices = index.search(query, k=5)
    
    assert len(distances[0]) == 5
    assert len(indices[0]) == 5

def test_sha256_hash(test_image):
    """Test SHA256 hash calculation."""
    hash1 = calculate_sha256(test_image)
    hash2 = calculate_sha256(test_image)
    
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 hash length
    assert hash1 == hash2  # Should be deterministic

def test_perceptual_hash(test_image):
    """Test perceptual hash calculation."""
    phash = perceptual_hash(test_image)
    
    assert isinstance(phash, str)
    assert len(phash) <= 32  # phash should be short

def test_preprocess_image(test_image):
    """Test image preprocessing."""
    processed = preprocess_image(test_image, target_size=(224, 224))
    
    assert isinstance(processed, np.ndarray)
    assert processed.shape == (224, 224, 3)
    assert processed.dtype == np.uint8  # PIL converts to uint8

# Placeholder for more tests
def testclip_model_loading():
    """Stub: Test CLIP model loading."""
    pass
