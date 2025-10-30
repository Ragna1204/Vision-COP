from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from .cbir import index_image, search_similar
from .verification import verify_image
from .database import add_image_metadata
import shutil
import os

app = FastAPI(title="VisionCOP - AI Image Authenticity Engine")

UPLOAD_DIR = "data/images"

@app.on_event("startup")
async def startup_event():
    """Initialize directories and load FAISS index on startup."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Load or create FAISS index here (stub)

@app.post("/index")
async def index_image_endpoint(file: UploadFile = File(...)):
    """Index an uploaded image for search."""
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract features and store in FAISS (stub)
    metadata = verify_image(file_path)
    add_image_metadata(file.filename, metadata)
    index_image(file_path)

    return JSONResponse(content={"message": f"Image {file.filename} indexed successfully"})

@app.post("/search")
async def search_image_endpoint(file: UploadFile = File(...)):
    """Search for similar images to the uploaded one."""
    file_path = f"{UPLOAD_DIR}/temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform search and get results (stub)
    similar_images = search_similar(file_path)

    # Clean up temp file
    os.remove(file_path)

    return JSONResponse(content={"similar_images": similar_images})
