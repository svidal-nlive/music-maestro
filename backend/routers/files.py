from fastapi import APIRouter, UploadFile, Depends
from routers.auth import get_current_user
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "music-maestro"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)

# Ensure the MinIO bucket exists
def ensure_bucket_exists():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except Exception:
        s3_client.create_bucket(Bucket=BUCKET_NAME)

ensure_bucket_exists()

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
def upload_file(file: UploadFile, user: str = Depends(get_current_user)):
    s3_client.upload_fileobj(file.file, BUCKET_NAME, file.filename)
    file_url = f"{MINIO_ENDPOINT}/{BUCKET_NAME}/{file.filename}"
    return {"filename": file.filename, "uploaded_by": user, "url": file_url}
