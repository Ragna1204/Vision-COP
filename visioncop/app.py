from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_image_embedding
from database import init_database, add_image, find_similar_images, get_all_images

app = FastAPI(title="VisionCOP", description="AI Image Similarity Search Engine")

# Mount static files (frontend)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "images")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_database()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface."""
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    return FileResponse(index_path, media_type="text/html")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload and index an image."""
    try:
        # Save the uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(DATA_PATH, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get embedding
        embedding = get_image_embedding(file_path)

        # Store in database
        success = add_image(unique_filename, embedding)

        if success:
            return {
                "success": True,
                "message": f"Image {file.filename} uploaded and indexed successfully",
                "filename": unique_filename
            }
        else:
            # Clean up file if database failed
            os.remove(file_path)
            return {
                "success": False,
                "message": "Failed to index image"
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading image: {str(e)}"
        }

@app.post("/search")
async def search_similar(file: UploadFile = File(...)):
    """Search for similar images."""
    try:
        # Save temp file for processing
        temp_filename = f"temp_{uuid.uuid4()}.jpg"
        temp_path = os.path.join(DATA_PATH, temp_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get embedding for search query
        query_embedding = get_image_embedding(temp_path)

        # Clean up temp file
        os.remove(temp_path)

        # Find similar images
        similar = find_similar_images(query_embedding, top_k=5)

        return {
            "success": True,
            "query_image": file.filename,
            "results": similar
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching images: {str(e)}"
        }

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serve uploaded images."""
    file_path = os.path.join(DATA_PATH, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "Image not found"}

@app.get("/status")
async def get_status():
    """Get system status and statistics."""
    try:
        total_images = len(get_all_images())
        return {
            "status": "running",
            "total_images": total_images,
            "model": "ResNet50"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
