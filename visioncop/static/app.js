// VisionCOP Frontend App

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Get DOM elements
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadFile = document.getElementById('uploadFile');
    const uploadStatus = document.getElementById('uploadStatus');

    const searchBtn = document.getElementById('searchBtn');
    const searchFile = document.getElementById('searchFile');
    const searchStatus = document.getElementById('searchStatus');
    const resultsDiv = document.getElementById('results');

    const statsDiv = document.getElementById('stats');

    // Load initial stats
    loadStats();

    // Upload functionality
    uploadBtn.addEventListener('click', async function() {
        const files = uploadFile.files;
        if (files.length === 0) {
            showStatus(uploadStatus, 'Please select files to upload', 'error');
            return;
        }

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<div class="loading"></div> Uploading...';

        let successCount = 0;
        let errorMessages = [];

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            try {
                const result = await uploadImage(file);
                if (result.success) {
                    successCount++;
                } else {
                    errorMessages.push(`${file.name}: ${result.message}`);
                }
            } catch (error) {
                errorMessages.push(`${file.name}: ${error.message}`);
            }
        }

        uploadBtn.disabled = false;
        uploadBtn.innerHTML = 'Upload & Index';

        if (successCount > 0) {
            showStatus(uploadStatus, `Successfully uploaded ${successCount} image(s)`, 'success');
            loadStats(); // Update stats
        }

        if (errorMessages.length > 0) {
            showStatus(uploadStatus, 'Errors: ' + errorMessages.join('; '), 'error');
        }

        // Clear file input
        uploadFile.value = '';
    });

    // Search functionality
    searchBtn.addEventListener('click', async function() {
        const file = searchFile.files[0];
        if (!file) {
            showStatus(searchStatus, 'Please select an image to search', 'error');
            return;
        }

        searchBtn.disabled = true;
        searchBtn.innerHTML = '<div class="loading"></div> Searching...';
        resultsDiv.innerHTML = '';

        try {
            const result = await searchSimilar(file);
            if (result.success) {
                showStatus(searchStatus, `Found ${result.results.length} similar images`, 'success');
                displayResults(result.results);
            } else {
                showStatus(searchStatus, result.message, 'error');
            }
        } catch (error) {
            showStatus(searchStatus, 'Search failed: ' + error.message, 'error');
        }

        searchBtn.disabled = false;
        searchBtn.innerHTML = 'Search';

        // Clear file input
        searchFile.value = '';
    });
}

async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    return await response.json();
}

async function searchSimilar(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/search', {
        method: 'POST',
        body: formData
    });

    return await response.json();
}

async function loadStats() {
    try {
        const response = await fetch('/status');
        const stats = await response.json();

        if (stats.status === 'running') {
            document.getElementById('stats').innerHTML = `
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-label">Total Images</div>
                        <div class="stat-value">${stats.total_images}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">AI Model</div>
                        <div class="stat-value">${stats.model}</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.log('Could not load stats:', error);
    }
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');

    if (results.length === 0) {
        resultsDiv.innerHTML = '<p>No similar images found. Try uploading some images first.</p>';
        return;
    }

    resultsDiv.innerHTML = '<div class="results-grid"></div>';
    const grid = resultsDiv.querySelector('.results-grid');

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'result-item';

        const similarityPercentage = (result.similarity * 100).toFixed(1);

        item.innerHTML = `
            <img src="/images/${result.filename}" alt="${result.filename}" class="result-image" loading="lazy">
            <div class="result-info">
                <div>${result.filename}</div>
                <div class="similarity">${similarityPercentage}% similar</div>
            </div>
        `;

        grid.appendChild(item);
    });
}

function showStatus(element, message, type) {
    element.innerHTML = `<div class="status ${type}">${message}</div>`;
    element.className = 'status-container';

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            element.innerHTML = '';
        }, 5000);
    }
}
