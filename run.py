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

def load_mirflickr():
    """Load MIRFLICKR dataset from ZIP file"""
    print("📥 MIRFLICKR Dataset Loader")
    print("This will extract and index the MIRFLICKR dataset with labels")
    print("Make sure the mirflickr.zip file is in the project root directory")
    print("Use: python run.py --load-mirflickr\n")

    import zipfile
    import pandas as pd
    from visioncop.models import get_image_embedding
    from visioncop.database import add_image
    import json

    zip_path = "mirflickr.zip"
    extract_path = "visioncop/data/images"

    if not os.path.exists(zip_path):
        print(f"❌ {zip_path} not found in project root directory!")
        print("Please download MIRFLICKR dataset and place mirflickr.zip in this folder.")
        print("MIRFLICKR can be found at: https://press.liacs.nl/mirflickr/")
        return

    try:
        original_dir = os.getcwd()
        os.chdir('visioncop')

        print("🗜️ Extracting MIRFLICKR dataset...")

        # Extract ZIP file
        with zipfile.ZipFile(f"../{zip_path}", 'r') as zip_ref:
            # List files to see what's in the dataset
            file_list = zip_ref.namelist()
            print(f"📁 Found {len(file_list)} files in ZIP")

            # Look for images and labels
            image_files = [f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            label_files = [f for f in file_list if 'label' in f.lower() or 'tag' in f.lower() or f.endswith('.txt') or f.endswith('.csv')]

            print(f"🖼️ Found {len(image_files)} image files")
            print(f"🏷️ Found {len(label_files)} potential label files")

            # Extract all contents
            zip_ref.extractall("data")

        # Load labels if available
        labels = {}
        images_dir = "data"

        # Try to find label files
        for root, dirs, files in os.walk(images_dir):
            for file in files:
                if file.endswith('.txt') or file.endswith('.csv'):
                    try:
                        print(f"📖 Attempting to read labels from: {file}")

                        if file.endswith('.csv'):
                            df = pd.read_csv(os.path.join(root, file))
                            # Try different column names for labels
                            for col in ['labels', 'tags', 'categories', 'description']:
                                if col in df.columns:
                                    for idx, row in df.iterrows():
                                        image_name = f"{idx+1}.jpg"  # Standard MIRFLICKR naming
                                        labels[image_name] = str(row[col])
                                    break
                        else:  # TXT file
                            with open(os.path.join(root, file), 'r') as f:
                                for line_num, line in enumerate(f):
                                    image_name = f"{line_num+1}.jpg"
                                    labels[image_name] = line.strip()

                    except Exception as e:
                        print(f"⚠️ Could not parse {file}: {e}")
                        continue

        print(f"🏷️ Loaded labels for {len(labels)} images")

        # Find all images in the extracted structure
        all_images = []
        for root, dirs, files in os.walk(images_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    all_images.append(os.path.join(root, file))

        print(f"🔍 Found {len(all_images)} total images to process")

        # Index images (limit for demo)
        max_images = 200  # Process first 200 images to avoid long processing
        images_processed = 0
        images_indexed = 0

        for i, image_path in enumerate(all_images[:max_images]):
            try:
                print(f"Processing {i+1}/{min(max_images, len(all_images))}: {os.path.basename(image_path)}")

                # Save to our images directory with consistent naming
                image_name = f"mirflickr_{i+1}.{image_path.split('.')[-1].lower()}"
                final_path = f"data/images/{image_name}"

                # Copy image to final location
                import shutil
                shutil.copy2(image_path, final_path)

                # Get embedding
                embedding = get_image_embedding(final_path)

                if embedding is not None:
                    # Add metadata including labels
                    metadata = {
                        'source': 'mirflickr',
                        'original_path': image_path,
                        'labels': labels.get(os.path.basename(image_path), 'unknown'),
                        'index_date': datetime.now().isoformat()
                    }

                    # Index with metadata
                    success = add_image(image_name, embedding, metadata)

                    if success:
                        images_indexed += 1

                images_processed += 1

            except Exception as e:
                print(f"❌ Error processing {os.path.basename(image_path)}: {e}")
                continue

        os.chdir(original_dir)

        print(f"\n✅ MIRFLICKR Dataset Loading Complete!")
        print(f"📊 Processed: {images_processed} images")
        print(f"🔍 Indexed: {images_indexed} images with embeddings")
        print(f"🏷️ Labels loaded: {len(labels)} label entries")

        if images_indexed > 0:
            print("\n🎯 Ready for similarity search and authenticity verification!")
            print("📱 Start server with: python run.py")
        else:
            print("\n❌ No images were successfully indexed")

    except Exception as e:
        print(f"❌ Error loading MIRFLICKR dataset: {e}")
        print("Make sure the ZIP file is valid and contains images")

def load_corel10k():
    """Download and load Corel-10k dataset (deprecated)"""
    print("📥 Corel-10k Dataset Loader")
    print("Note: Consider using MIRFLICKR dataset instead with: --load-mirflickr")
    print("Use: python run.py --load-corel10k\n")
    # ... (keep existing function for backward compatibility)

def main():
    parser = argparse.ArgumentParser(description="VisionCOP AI Image Search")
    parser.add_argument('--serve', action='store_true', help='Start web server')
    parser.add_argument('--load-mirflickr', action='store_true', help='Load MIRFLICKR dataset from zip file')
    parser.add_argument('--load-corel10k', action='store_true', help='Download Corel-10k dataset')

    # Default action is to serve if no args given
    if len(sys.argv) == 1:
        start_server()
        return

    args = parser.parse_args()

    if args.serve:
        start_server()
    elif args.load_mirflickr:
        load_mirflickr()
    elif args.load_corel10k:
        load_corel10k()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
