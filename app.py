import streamlit as st
import os
import numpy as np
from PIL import Image
import pickle
import glob

from visioncop.models import get_image_embedding

# Paths
DATA_DIR = "visioncop/data/images"
EMBEDDINGS_FILE = "visioncop/data/embeddings.pkl"

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)

def load_embeddings():
    """Load stored image embeddings"""
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_embeddings(embeddings):
    """Save image embeddings"""
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(embeddings, f)

def index_image(file_path, filename):
    """Index a single image"""
    try:
        embedding = get_image_embedding(file_path)
        if embedding is not None:
            embeddings = load_embeddings()
            embeddings[filename] = embedding
            save_embeddings(embeddings)
            return True
    except Exception as e:
        print(f"Error indexing {filename}: {e}")
    return False

def find_similar_images(query_embedding, top_k=6):
    """Find similar images using cosine similarity"""
    embeddings = load_embeddings()
    similarities = []

    for filename, embedding in embeddings.items():
        similarity = np.dot(query_embedding, embedding)  # Cosine similarity
        similarities.append((filename, similarity))

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

# Page config
st.set_page_config(
    page_title="VisionCOP - AI Image Search",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("🎨 VisionCOP - AI Image Similarity Search")
    st.markdown("Upload images to find visually similar ones using ResNet50 embeddings")

    # Load embeddings
    embeddings_data = load_embeddings()

    # Load dataset status
    st.sidebar.header("📊 Dataset Status")
    indexed_count = len(embeddings_data)
    st.sidebar.metric("Indexed Images", indexed_count)

    tab1, tab2 = st.tabs(["🎯 Find Similar", "📤 Index New Images"])

    with tab1:
        st.header("Find Similar Images")

        uploaded_file = st.file_uploader("Choose an image to search for...", type=['jpg', 'jpeg', 'png'])

        if uploaded_file is not None:
            # Display uploaded image
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(uploaded_file, caption="Query Image", width=200)

            with col2:
                if st.button("🔍 Search Similar Images", type="primary"):
                    with st.spinner("Analyzing image and searching..."):
                        # Save temp file
                        temp_path = "temp_query.jpg"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Get embedding
                        embedding = get_image_embedding(temp_path)

                        # Clean up temp file
                        os.remove(temp_path)

                        if embedding is not None:
                            # Find similar images
                            similar_results = find_similar_images(embedding, top_k=6)

                            if similar_results and len(similar_results) > 0:
                                st.success(f"Found {len(similar_results)} similar images!")

                                # Display results in a grid
                                cols = st.columns(3)
                                for i, (filename, similarity) in enumerate(similar_results):
                                    col_idx = i % 3

                                    with cols[col_idx]:
                                        file_path = f"visioncop/data/images/{filename}"
                                        if os.path.exists(file_path):
                                            try:
                                                img = Image.open(file_path)
                                                st.image(img, caption=f"{filename}\nSimilarity: {(similarity*100):.1f}%",
                                                       width=150)
                                            except Exception:
                                                st.write(f"🖼️ {filename}")
                                                st.write(f"Similarity: {(similarity*100):.1f}%")
                                        else:
                                            st.write(f"🖼️ {filename}")
                                            st.write(f"Similarity: {(similarity*100):.1f}%")
                            else:
                                st.warning("No similar images found in the database. Try indexing some images first!")
                        else:
                            st.error("Failed to process the uploaded image. Please try again.")

    with tab2:
        st.header("Index New Images")
        st.markdown("Upload images to add them to the search database")

        uploaded_files = st.file_uploader("Choose images to index...", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

        if uploaded_files:
            if st.button(f"📤 Index {len(uploaded_files)} Images", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                successes = 0
                total = len(uploaded_files)

                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        status_text.text(f"Processing {uploaded_file.name}...")

                        # Save file and index
                        file_path = os.path.join(DATA_DIR, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Index the image
                        if index_image(file_path, uploaded_file.name):
                            successes += 1
                        else:
                            st.error(f"Failed to index {uploaded_file.name}")

                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")

                    progress = (i + 1) / total
                    progress_bar.progress(progress)

                progress_bar.empty()
                status_text.empty()

                # Refresh sidebar count after indexing
                if successes > 0:
                    embeddings_data = load_embeddings()

                if successes > 0:
                    st.success(f"✅ Successfully indexed {successes}/{total} images!")
                    st.balloons()
                else:
                    st.error("❌ No images were successfully indexed.")

    # Footer
    st.markdown("---")
    st.markdown("""
    **VisionCOP** uses ResNet50 neural networks to find visually similar images.
    Upload Corel-10k images or any photos to test the similarity search!
    """)

if __name__ == "__main__":
    main()
