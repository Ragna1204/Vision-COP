# VisionCOP
AI Image Similarity Search Engine

A simple, powerful image search system using ResNet50 embeddings for finding visually similar images - built with Streamlit.

## Features

- **ResNet50 Image Embeddings**: High-quality image feature extraction
- **Cosine Similarity Search**: Fast, accurate semantic similarity matching
- **Perceptual Hashing (pHash)**: Pixel-level authenticity verification for manipulation detection
- **Dual Analysis**: Semantic similarity + pixel authenticity for comprehensive analysis
- **Streamlit Web Interface**: Drag-and-drop upload with instant results
- **Pickle-based Storage**: Simple, reliable embeddings storage
- **Corel-10K Integration**: Ready for large dataset testing

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

### 4. (Optional) Load Corel-10K Images
The Corel-10K images you added to `visioncop/data/images/` will be automatically available for search once you upload and index any query image.

## How to Use

1. **Index Images**: Use the "📤 Index New Images" tab to add images to the search database
2. **Search**: Use the "🎯 Find Similar" tab and upload a query image
3. **Enable Verification**: Check "🔍 Show Authenticity Verification" for pixel-level analysis
4. **Dual Results**: See both semantic similarity AND pixel authenticity scores

### Authenticity Verification Levels
- ✅ **Authentic**: Identical file or exact copy (Distance = 0)
- ⚠️ **High Similarity**: Re-used, resized, or re-compressed (Distance ≤ 8)
- 🚩 **Potential Manipulation**: Cropped, filtered, or minor edits (Distance ≤ 20)
- ℹ️ **Different Image**: Major changes or different content (Distance > 20)

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
