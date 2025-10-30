import sqlite3
import os
import json
import numpy as np
from datetime import datetime

DB_PATH = 'visioncop.db'
DATA_PATH = 'visioncop/data/images'

# Create data directory if it doesn't exist
os.makedirs(DATA_PATH, exist_ok=True)

def init_database():
    """Initialize the database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create initial table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            filename TEXT UNIQUE,
            path TEXT,
            embedding BLOB,
            upload_date TEXT
        )
    ''')

    # Add metadata column if it doesn't exist (migration)
    try:
        cursor.execute("ALTER TABLE images ADD COLUMN metadata TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()

def add_image(filename, embedding, metadata=None):
    """Add an image and its embedding to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Convert embedding to bytes for storage
        embedding_bytes = embedding.tobytes() if embedding is not None else None

        # Convert metadata to JSON string
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT OR REPLACE INTO images (filename, path, embedding, upload_date, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, f'{DATA_PATH}/{filename}', embedding_bytes, datetime.now().isoformat(), metadata_json))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding image: {e}")
        return False

def get_all_images():
    """Get all images from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT filename, path, upload_date FROM images')
        rows = cursor.fetchall()

        conn.close()
        return [{'filename': row[0], 'path': row[1], 'date': row[2]} for row in rows]
    except Exception as e:
        print(f"Error getting images: {e}")
        return []

def find_similar_images(query_embedding, top_k=5):
    """Find similar images using cosine similarity."""
    if query_embedding is None:
        return []

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get all embeddings
        cursor.execute('SELECT filename, embedding FROM images WHERE embedding IS NOT NULL')
        rows = cursor.fetchall()

        similarities = []
        for filename, embedding_bytes in rows:
            if embedding_bytes:
                # Convert bytes back to numpy array
                db_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

                # Calculate cosine similarity
                similarity = np.dot(query_embedding, db_embedding)
                similarities.append((filename, similarity))

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        conn.close()

        return [{'filename': fname, 'similarity': sim} for fname, sim in similarities[:top_k]]

    except Exception as e:
        print(f"Error finding similar images: {e}")
        return []
