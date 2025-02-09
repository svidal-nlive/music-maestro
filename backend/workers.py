import os
import requests
import boto3
import redis
from celery import Celery

celery_app = Celery(
    "backend.workers",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"  # <-- Add this line
)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

# MinIO connection details
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "music-maestro"
SPLEETER_API_URL = "http://spleeter:8000/process/"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)

@celery_app.task()
def process_audio(filename):
    task_id = process_audio.request.id
    redis_client.set(f"task:{task_id}", "Downloading")

    local_temp_file = f"/tmp/{filename}"
    s3_client.download_file(BUCKET_NAME, filename, local_temp_file)
    redis_client.set(f"task:{task_id}", "Processing")
    
    with open(local_temp_file, "rb") as f:
        response = requests.post(SPLEETER_API_URL, files={"file": (filename, f)})
    response.raise_for_status()
    redis_client.set(f"task:{task_id}", "Uploading")

    base_filename = filename.rsplit(".", 1)[0]
    processed_dir = f"/spleeter/output/{base_filename}"
    stems = ["vocals", "drums", "bass", "other", "piano"]
    
    for stem in stems:
        stem_file = os.path.join(processed_dir, f"{stem}.wav")
        if os.path.exists(stem_file):
            minio_stem_path = f"processed/{base_filename}_{stem}.wav"
            s3_client.upload_file(stem_file, BUCKET_NAME, minio_stem_path)
    
    redis_client.set(f"task:{task_id}", "Complete")
    return f"Processing and upload complete for {filename}"
