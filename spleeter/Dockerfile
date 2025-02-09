# Use an official Python slim image
FROM python:3.9-slim

# Install system dependencies; for example, ffmpeg is required by Spleeter.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the Python dependencies file and install them.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Spleeter API server script into the image.
COPY spleeter_api.py /app/

# Copy the models directory (if required by Spleeter)
COPY models /model

# Define shared volume mount points for input and output directories.
VOLUME ["/input", "/output"]

# Expose the API port (for internal container communication)
EXPOSE 8000

# Start the API server using Uvicorn.
CMD ["uvicorn", "spleeter_api:app", "--host", "0.0.0.0", "--port", "8000"]
