# Vision-COP
Image Source and Authenticity Engine

An AI-powered image authenticity and reverse search engine built with FastAPI, CLIP embeddings, and FAISS indexing.

## Features

- **Content-Based Image Retrieval (CBIR)**: Find visually similar images using CLIP embeddings and FAISS
- **Image Authenticity Verification**:
  - SHA256 hashing for tamper detection
  - Perceptual hashing (phash) for duplicate detection
  - EXIF metadata extraction
  - Error Level Analysis (ELA) for manipulation scoring
- **REST API**: Simple endpoints for image indexing and search
- **Web Interface**: Upload and search images via browser
- **SQLite Database**: Metadata storage with SQLAlchemy
- **Scalable Architecture**: Modular design for easy extension

## Project Structure

```
visioncop/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application with endpoints
│   ├── cbir.py          # CLIP embeddings and FAISS indexing
│   ├── verification.py  # Image hashing and forensic analysis
│   ├── database.py      # SQLite database operations
│   ├── models/          # AI/ML models (placeholder)
│   └── utils/
│       ├── image_utils.py  # Processing and analysis utilities
│       └── __init__.py
├── data/
│   ├── images/          # Indexed image files
│   └── index/           # FAISS index files
├── frontend/
│   ├── index.html       # Web UI
│   ├── style.css        # Styling
│   └── script.js        # JavaScript for API calls
├── tests/
│   ├── test_api.py      # API endpoint tests
│   └── test_embeddings.py # CLIP/FAISS tests
├── requirements.txt     # Python dependencies
└── Dockerfile          # Docker configuration
```

## Installation

### Option 1: Virtual Environment (Recommended)

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Docker

1. Build the Docker image:
   ```bash
   docker build -t visioncop .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 visioncop
   ```

## Usage

### Start the Server

1. Run the FastAPI server:
   ```bash
   uvicorn visioncop.app.main:app --reload
   ```

2. Open the web interface by navigating to `http://localhost:8000/frontend/index.html` in your browser

### API Endpoints

- `POST /index`: Index an image for search
  - Upload an image file to index it in the system
  - Returns: Confirmation message

- `POST /search`: Search for similar images
  - Upload a query image
  - Returns: List of similar images with metadata

### Web Interface

1. **Index Images**: Use the "Index Image" section to add images to the search database
2. **Search Images**: Use the "Search Similar Images" section to find visually similar images

### Development

Run tests:
```bash
pytest visioncop/tests/
```

## Dependencies

- **FastAPI**: Modern Python web framework
- **CLIP**: Vision-language model for image embeddings
- **FAISS**: Efficient similarity search and clustering
- **Pillow**: Image processing
- **OpenCV**: Computer vision tasks
- **SQLAlchemy**: Database ORM
- **imagehash**: Perceptual hashing
- **exifread**: EXIF metadata extraction

## Future Enhancements

- **Blockchain Integration**: SHA256 hashes for immutability
- **Advanced Forensic Analysis**: More sophisticated manipulation detection
- **Machine Learning Models**: Auto-tagging and classification
- **WebSocket Support**: Real-time search updates
- **Multi-modal Search**: Text-to-image and image-to-text

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
