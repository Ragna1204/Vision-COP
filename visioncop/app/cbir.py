import clip
import torch
from PIL import Image
import faiss
import numpy as np
import os

INDEX_PATH = "data/index/faiss.index"
DIM = 512  # CLIP embedding dimension

def load_clip_model():
    """Load CLIP model for image embeddings."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    return model, preprocess, device

def extract_embedding(image_path):
    """Extract CLIP embedding for an image."""
    model, preprocess, device = load_clip_model()
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image).float().cpu().numpy()
    return embedding / np.linalg.norm(embedding)  # Normalize

def create_faiss_index():
    """Create a new FAISS index."""
    return faiss.IndexFlatIP(DIM)  # Inner product for cosine similarity

def load_faiss_index():
    """Load existing FAISS index or create new if not exists."""
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    else:
        return create_faiss_index()

def save_faiss_index(index):
    """Save FAISS index to disk."""
    faiss.write_index(index, INDEX_PATH)

def index_image(image_path):
    """Add image embedding to the FAISS index."""
    embedding = extract_embedding(image_path)
    index = load_faiss_index()
    index.add(embedding)
    save_faiss_index(index)

def search_similar(query_path, top_k=5):
    """Search for similar images in the index."""
    query_embedding = extract_embedding(query_path)
    index = load_faiss_index()
    distances, indices = index.search(query_embedding, top_k)
    # Stub: Return dummy filenames for now
    return [f"similar_image_{i}.jpg" for i in range(top_k)]
