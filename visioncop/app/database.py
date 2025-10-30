from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import json
from datetime import datetime

Base = declarative_base()

class ImageMetadata(Base):
    __tablename__ = 'image_metadata'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), unique=True)
    sha256 = Column(String(64))
    phash = Column(String(16))
    exif_data = Column(Text)  # JSON string
    manipulation_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

DATABASE_URL = "sqlite:///visioncop.db"
engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_image_metadata(filename, metadata):
    """Add image metadata to the database."""
    session = SessionLocal()
    try:
        # Check if image already exists
        existing = session.query(ImageMetadata).filter_by(filename=filename).first()
        if existing:
            # Update existing record
            existing.sha256 = metadata['sha256']
            existing.phash = metadata['phash']
            existing.exif_data = json.dumps(metadata['exif'])
            existing.manipulation_score = metadata['manipulation_score']
        else:
            # Add new record
            image_meta = ImageMetadata(
                filename=filename,
                sha256=metadata['sha256'],
                phash=metadata['phash'],
                exif_data=json.dumps(metadata['exif']),
                manipulation_score=metadata['manipulation_score']
            )
            session.add(image_meta)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error adding metadata: {e}")
    finally:
        session.close()

def get_image_metadata(filename):
    """Retrieve metadata for a specific image."""
    session = SessionLocal()
    try:
        image_meta = session.query(ImageMetadata).filter_by(filename=filename).first()
        if image_meta:
            return {
                "filename": image_meta.filename,
                "sha256": image_meta.sha256,
                "phash": image_meta.phash,
                "exif": json.loads(image_meta.exif_data or '{}'),
                "manipulation_score": image_meta.manipulation_score,
                "created_at": image_meta.created_at.isoformat()
            }
        return None
    finally:
        session.close()

def get_all_images():
    """Get all indexed images metadata (stub)."""
    session = SessionLocal()
    try:
        images = session.query(ImageMetadata).all()
        return [{
            "filename": img.filename,
            "phash": img.phash,
            "manipulation_score": img.manipulation_score
        } for img in images]
    finally:
        session.close()
