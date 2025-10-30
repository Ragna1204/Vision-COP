import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os

# Global model instance
model = None
transforms_img = None

def load_resnet_model():
    """Load ResNet50 model for image embeddings."""
    global model, transforms_img

    if model is None:
        # Load pre-trained ResNet50
        model = models.resnet50(pretrained=True)
        # Remove the final classification layer to get embeddings
        model = nn.Sequential(*list(model.children())[:-1])
        model.eval()

        # Move to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

        # Define image preprocessing
        transforms_img = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    return model, transforms_img

def get_image_embedding(image_path):
    """Extract embedding from image using ResNet."""
    try:
        model, transform = load_resnet_model()

        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image = transform(image).unsqueeze(0)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        image = image.to(device)

        # Get embedding
        with torch.no_grad():
            embedding = model(image)

        # Flatten and normalize
        embedding = embedding.cpu().numpy().flatten()
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None
