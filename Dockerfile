# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY visioncop/ ./visioncop/

# Create data directories
RUN mkdir -p visioncop/data/images visioncop/data/index

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "visioncop.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
