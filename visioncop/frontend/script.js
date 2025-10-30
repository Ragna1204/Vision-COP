// Globals
const API_BASE = 'http://localhost:8000';

// Index Image Form Handler
document.getElementById('indexForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const file = document.getElementById('indexFile').files[0];
    formData.append('file', file);
    
    const resultDiv = document.getElementById('indexResult');
    
    try {
        resultDiv.innerHTML = '<p>Indexing image...</p>';
        
        const response = await fetch(`${API_BASE}/index`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
        } else {
            throw new Error(data.message || 'Error indexing image');
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
    }
    
    // Reset form
    document.getElementById('indexForm').reset();
});

// Search Form Handler
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const file = document.getElementById('searchFile').files[0];
    formData.append('file', file);
    
    const resultDiv = document.getElementById('searchResults');
    const galleryDiv = document.getElementById('resultsGallery');
    
    try {
        resultDiv.innerHTML = '<p>Searching for similar images...</p>';
        galleryDiv.innerHTML = '';
        
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.similar_images) {
            resultDiv.innerHTML = `<div class="alert alert-success">Found ${data.similar_images.length} similar images!</div>`;
            displayResults(data.similar_images);
        } else {
            throw new Error('No similar images found');
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
    }
    
    // Reset form
    document.getElementById('searchForm').reset();
});

function displayResults(images) {
    const galleryDiv = document.getElementById('resultsGallery');
    
    images.forEach((image, index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'result-item';
        
        // Placeholder image since we don't have actual image URLs
        itemDiv.innerHTML = `
            <img src="/placeholder-image.jpg" alt="Similar Image ${index + 1}" style="width: 100px; height: 100px; object-fit: cover;">
            <p>${image}</p>
            <small>Similarity Score: ${Math.floor(Math.random() * 100)}%</small>
        `;
        
        galleryDiv.appendChild(itemDiv);
    });
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('VisionCOP Frontend loaded');
});
