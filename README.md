# VisionCOP
AI Image Similarity Search Engine

A simple, powerful image search system using ResNet50 embeddings for finding visually similar images - built with Streamlit.

## Features

- **ResNet50 Image Embeddings**: High-quality image feature extraction for semantic similarity
- **Cosine Similarity Search**: Fast, accurate visual similarity matching
- **Perceptual Hashing (pHash)**: Pixel-level authenticity verification with Hamming distance
- **EXIF Metadata Analysis**: Detects mismatched image tags and metadata inconsistencies
- **Manipulation Detection**: Identifies signs of editing, filtering, and digital tampering
- **Comprehensive Authenticity Verification**: Multi-layered analysis for manipulation detection
- **Streamlit Web Interface**: Interactive drag-and-drop with detailed verification reports
- ** верификация по всем изображениям**: Option to verify query against ALL indexed images
- **Color-coded Results**: Green, orange, red indicators for authenticity confidence levels

## Project Structure

```
visioncop/
├── app.py              # 🚀 Main Streamlit application
├── models.py           # 🤖 ResNet50 model for embeddings
├── database.py         # 💾 Pickle-based storage (legacy)
├── static/             # 📱 Static files (unused in Streamlit)
├── data/               # 🖼️ Data storage
│   └── images/         # Stored image files
├── requirements.txt    # 📦 Python dependencies
└── run.py            # ▶️ Easy startup script
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python run.py
```
Or directly:
```bash
streamlit run app.py
```

### 3. Open Web Interface
Streamlit will automatically open `http://localhost:8501` in your browser

### 4. Load MIRFLICKR Dataset (Recommended)
```bash
python run.py --load-mirflickr
```

**Requirements:**
1. Download MIRFLICKR dataset ZIP file
2. Rename it to `mirflickr.zip`
3. Place it in the project root directory
4. Run the command above

MIRFLICKR provides 25,000 labeled images from Flickr for research on image search and tagging. The loader will automatically:
- Extract images from ZIP file
- Process and index first 200 images (configurable)
- Load labels/metadata for enhanced verification
- Store everything in the database for search

### 5. (Alternative) Load Corel-10K Images
```bash
python run.py --load-corel10k
```
Generates synthetic Corel-style images for testing (deprecated - use MIRFLICKR instead)

## How to Use

1. **Index Images**: Use the "📤 Index New Images" tab to add images to the search database
2. **Search**: Use the "🎯 Find Similar" tab and upload a query image
3. **Enable Verification**: Check "🔍 Show Authenticity Verification" for pixel-level analysis
4. **Dual Results**: See both semantic similarity AND pixel authenticity scores

### Authenticity Verification Features

**Multi-Layer Analysis:**
- **🎯 Semantic Similarity**: Visual appearance matching (ResNet50 CNN)
- **🔐 Pixel Authenticity**: Exact pixel pattern matching (pHash/Hamming Distance)
- **📋 Metadata Validation**: EXIF data consistency checks
- **🚩 Manipulation Detection**: Signs of digital editing/artifacts

**Verification Levels:**
- ✅ **Perfectly Authentic**: Exact match with matching metadata
- 🟢 **Authentic/Authentic Copy**: Near-identical pixels, authentic source
- 🟡 **Likely Authentic/Reused**: High pixel similarity, possibly different context
- 🔴 **Definitely Manipulated**: High manipulation score, clear editing signs
- 🔘 **Metadata Mismatch**: Metadata differs from original (tampered EXIF)
- ⚪ **Different Image**: Completely different content

**Detection Capabilities:**
- **Manipulated optics**: Warmth/saturation modifications (your edited image)
- **Re-used visuals**: Content copied between contexts
- **Mismatched tags**: Inconsistent metadata across similar images
- **Deceptive visuals**: Edited images presented as original content
- **Compression artifacts**: Multiple save/lossy compression detection
- **Brightness anomalies**: Unusual brightness patterns from cloning/retouching

## API Endpoints

- `POST /upload` - Index new images
- `POST /search` - Find similar images
- `GET /status` - System statistics
- `GET /` - Web interface
- `GET /images/{filename}` - Access stored images

## Tech Stack

- **Backend**: FastAPI, Python
- **AI Model**: ResNet50 (PyTorch)
- **Database**: SQLite
- **Frontend**: Vanilla HTML/CSS/JS
- **Similarity**: Cosine similarity

## Next Steps

- Add image metadata extraction
- Implement batch uploads
- Add result pagination
- Create user accounts/sessions
- Add search filters and categories
