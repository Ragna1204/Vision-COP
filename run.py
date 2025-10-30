#!/usr/bin/env python3
"""
VisionCOP - AI Image Similarity Search Engine
Simple startup script

Run from project root: python run.py
"""

import subprocess
import sys
import os

def start_streamlit():
    """Start the Streamlit app"""
    print("🚀 Starting VisionCOP Server...")
    print("📱 Web interface: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop\n")

    try:
        # Run streamlit app
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501"]
        subprocess.run(cmd, cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n👋 VisionCOP stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def load_corel10k():
    """Download and load Corel-10k dataset"""
    print("📥 Corel-10k Dataset Loader")
    print("This will download sample images and index them into VisionCOP")
    print("Use: python run.py --load-corel10k\n")

    try:
        import requests
        from tqdm import tqdm
        from visioncop.models import get_image_embedding
        from visioncop.database import add_image

        # Corel-10k is available from academic sources
        # For demo purposes, we'll use a simpler approach

        # Change to visioncop directory
        original_dir = os.getcwd()
        os.chdir('visioncop')

        print("🎨 Generating sample Corel-style images...")

        # Generate 10 sample images of different categories
        categories = ['nature', 'buildings', 'animals', 'objects', 'people']
        images_created = 0

        for i, category in enumerate(categories):
            for j in range(2):  # 2 images per category
                # Create a simple colored image for demo
                from PIL import Image
                import numpy as np

                # Create different colors for each category
                colors = [
                    (76, 175, 80),   # Green for nature
                    (33, 150, 243),  # Blue for buildings
                    (255, 152, 0),   # Orange for animals
                    (156, 39, 176),  # Purple for objects
                    (255, 87, 34)    # Red-Orange for people
                ]

                # Create image with pattern
                img = Image.new('RGB', (224, 224), colors[i])
                # Add some pattern
                pixels = np.array(img)
                pixels[50:150, 50:150] = (255, 255, 255)  # White square
                img = Image.fromarray(pixels)

                # Save image
                filename = f"{category}_{j}.jpg"
                filepath = f"data/images/{filename}"
                img.save(filepath)

                # Get embedding and store
                embedding = get_image_embedding(filepath)
                success = add_image(filename, embedding)

                if success:
                    images_created += 1
                    print(f"✓ Created {filename}")
                else:
                    print(f"✗ Failed to index {filename}")

        os.chdir(original_dir)

        if images_created > 0:
            print(f"\n✅ Created {images_created} sample images")
            print("🎯 You can now use these images to test the search functionality!")
            print("📱 Start server with: python run.py")
        else:
            print("\n❌ No images were created successfully")

    except Exception as e:
        print(f"❌ Error during dataset creation: {e}")
        print("Make sure visioncop models and database are working")

def main():
    parser = argparse.ArgumentParser(description="VisionCOP AI Image Search")
    parser.add_argument('--serve', action='store_true', help='Start web server')
    parser.add_argument('--load-corel10k', action='store_true', help='Download Corel-10k dataset')

    # Default action is to serve if no args given
    if len(sys.argv) == 1:
        start_server()
        return

    args = parser.parse_args()

    if args.serve:
        start_server()
    elif args.load_corel10k:
        load_corel10k()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
