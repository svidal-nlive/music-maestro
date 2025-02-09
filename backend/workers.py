import os
import requests
import boto3
from celery import Celery

celery_app = Celery("backend.workers", broker="redis://redis:6379/0")

# MinIO connection details (ensure these environment variables are set)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "music-maestro"

# Configure the boto3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)

# URL for the Spleeter API (using the container name as hostname and port)
SPLEETER_API_URL = "http://spleeter:8000/process/"

@celery_app.task()
def process_audio(filename):
    # Step 1: Download the original file from MinIO to a temporary local path.
    local_temp_file = f"/tmp/{filename}"
    s3_client.download_file(BUCKET_NAME, filename, local_temp_file)
    print(f"Downloaded {filename} to {local_temp_file}")

    # Step 2: Call the Spleeter REST API to process the audio.
    with open(local_temp_file, "rb") as f:
        response = requests.post(SPLEETER_API_URL, files={"file": (filename, f)})
    response.raise_for_status()  # Raise an error if the API call failed.
    print(f"File {filename} processed by Spleeter API.")

    # Step 3: Locate the processed stems.
    # The Spleeter API writes output to the shared output directory at:
    #    /spleeter/output/{base_filename}
    base_filename = filename.rsplit(".", 1)[0]
    processed_dir = f"/spleeter/output/{base_filename}"

    # (Optional) You could add polling logic here if processing takes time.

    # List of stems expected (adjust based on your Spleeter configuration)
    stems = ["vocals", "drums", "bass", "other", "piano"]

    # Step 4: Upload each stem to MinIO.
    for stem in stems:
        stem_file = os.path.join(processed_dir, f"{stem}.wav")
        if os.path.exists(stem_file):
            minio_stem_path = f"processed/{base_filename}_{stem}.wav"
            s3_client.upload_file(stem_file, BUCKET_NAME, minio_stem_path)
            print(f"Uploaded {stem_file} to MinIO as {minio_stem_path}")
        else:
            # Log a warning if the expected stem file is missing.
            print(f"Warning: Expected stem file {stem_file} not found.")

    return f"Processing and upload complete for {filename}"
