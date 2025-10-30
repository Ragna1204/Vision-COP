import streamlit as st
import os
import numpy as np
from PIL import Image
import pickle
import glob

from visioncop.models import get_image_embedding
from visioncop.verification import verify_image_authenticity, get_verification_status

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

                                # Toggle for detailed verification
                                show_verification = st.checkbox("🔍 Show Authenticity Verification (Comprehensive Analysis)")
                                verify_all = st.checkbox("🔎 Verify Against ALL Images (Not Just Similar Ones)")

                                # Get all images if verification is enabled
                                if show_verification and verify_all:
                                    # Verify against ALL indexed images
                                    all_verifications = []

                                    # Get list of all indexed images
                                    for image_file in os.listdir("visioncop/data/images"):
                                        if image_file.endswith(('.jpg', '.jpeg', '.png')):
                                            image_path = f"visioncop/data/images/{image_file}"
                                            try:
                                                verification = verify_image_authenticity(temp_path, image_path)
                                                if verification['pixel_distance'] >= 0:  # Successful verification
                                                    all_verifications.append((image_file, verification))
                                            except:
                                                continue

                                    # Sort by pixel distance (most similar first)
                                    all_verifications.sort(key=lambda x: x[1]['pixel_distance'])

                                    if all_verifications:
                                        st.markdown("### 🔍 Authenticity Verification Results (All Images)")

                                        # Display top verifications
                                        cols = st.columns(3)
                                        for i, (filename, verification) in enumerate(all_verifications[:9]):  # Show top 9
                                            col_idx = i % 3

                                            with cols[col_idx]:
                                                file_path = f"visioncop/data/images/{filename}"
                                                if os.path.exists(file_path):
                                                    try:
                                                        img = Image.open(file_path)
                                                        confidence, color = get_verification_status(verification)

                                                        caption = f"{filename}\n🔒 {confidence}"
                                                        if verification['pixel_distance'] > 0:
                                                            caption += f" (Dist: {verification['pixel_distance']})"

                                                        # Add color background based on confidence
                                                        if color == "#27ae60":
                                                            st.success(confidence, icon="✅")
                                                        elif color == "#f39c12":
                                                            st.warning(confidence, icon="⚠️")
                                                        elif color == "#e74c3c":
                                                            st.error(confidence, icon="🚩")
                                                        else:
                                                            st.info(confidence, icon="ℹ️")

                                                        st.image(img, caption=caption, width=150)

                                                        # Show metadata issues if any
                                                        if verification['metadata_issues']:
                                                            st.caption("📋 Metadata Differences:")
                                                            for issue in verification['metadata_issues'][:2]:  # Show first 2
                                                                st.caption(f"• {issue}")

                                                        # Show manipulation flags
                                                        if verification['manipulation_flags']:
                                                            st.caption("🚩 Manipulation Indicators:")
                                                            for flag in verification['manipulation_flags'][:2]:
                                                                st.caption(f"• {flag}")

                                                    except Exception as e:
                                                        st.write(f"🖼️ {filename}")
                                                        status, color = get_verification_status(verification)
                                                        st.caption(f"🔒 {status}")

                                # Display semantic similarity results
                                st.markdown("### 🎯 Semantic Similarity Results")
                                cols = st.columns(3)
                                for i, (filename, similarity) in enumerate(similar_results):
                                    col_idx = i % 3

                                    with cols[col_idx]:
                                        file_path = f"visioncop/data/images/{filename}"
                                        if os.path.exists(file_path):
                                            try:
                                                img = Image.open(file_path)
                                                caption = f"{filename}\n🎯 Similarity: {(similarity*100):.1f}%"

                                                st.image(img, caption=caption, width=150)

                                            except Exception as e:
                                                st.write(f"🖼️ {filename}")
                                                st.write(f"Similarity: {(similarity*100):.1f}%")
                                        else:
                                            st.write(f"🖼️ {filename}")
                                            st.write(f"Similarity: {(similarity*100):.1f}%")

                                # Detailed verification for similar images
                                if show_verification and not verify_all:
                                    st.markdown("### 🔍 Detailed Verification (Similar Images Only)")
                                    for filename, similarity in similar_results[:3]:  # Show detailed for top 3
                                        file_path = f"visioncop/data/images/{filename}"

                                        try:
                                            verification = verify_image_authenticity(temp_path, file_path)

                                            col1, col2 = st.columns([1, 3])
                                            with col1:
                                                img = Image.open(file_path)
                                                st.image(img, width=100)

                                            with col2:
                                                confidence, color = get_verification_status(verification)
                                                st.subheader(f"{filename} - {confidence}")

                                                st.metric("Semantic Similarity", f"{(similarity*100):.1f}%")
                                                st.metric("Pixel Distance", verification['pixel_distance'])

                                                if verification['metadata_issues']:
                                                    st.write("📋 **Metadata Differences:**")
                                                    for issue in verification['metadata_issues'][:3]:
                                                        st.write(f"• {issue}")

                                                if verification['manipulation_flags']:
                                                    st.write("🚩 **Manipulation Indicators:**")
                                                    for flag in verification['manipulation_flags'][:3]:
                                                        st.write(f"• {flag}")

                                        except Exception as e:
                                            st.write(f"Error verifying {filename}: {e}")

                                # Comprehensive explanation
                                if show_verification:
                                    with st.expander("🔍 Verification Analysis Explanation"):
                                        st.markdown("""
                                        **Analysis Methods:**

                                        🎯 **Semantic Similarity (ResNet50)**: How visually similar images appear
                                        🔐 **Pixel Authenticity (pHash)**: Exact pixel pattern matching
                                        📋 **Metadata Comparison**: EXIF data validation
                                        🚩 **Manipulation Detection**: Signs of editing/tampering

                                        **Status Levels:**
                                        - 🟢 **Perfectly Authentic**: Exact match with matching metadata
                                        - 🟡 **Likely Authentic/Reused**: Similar pixels, no major issues
                                        - 🔴 **Definitely Manipulated**: High manipulation score detected
                                        - 🔘 **Metadata Mismatch**: Metadata doesn't match original
                                        - ⚪ **Different Image**: Completely different content
                                        """)

                            else:
                                st.warning("No similar images found in the database. Try indexing some images first!")

                                # Still offer verification if requested
                                if show_verification:
                                    st.info("No semantic matches found, but we can still check authenticity against all indexed images.")
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
