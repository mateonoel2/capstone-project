import os
import uuid
from pathlib import Path

import boto3
from fastapi import UploadFile

UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"


def _get_s3_client():
    endpoint = os.getenv("BUCKET_ENDPOINT")
    if not endpoint:
        return None
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv("BUCKET_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("BUCKET_SECRET_ACCESS_KEY"),
        region_name=os.getenv("BUCKET_REGION", "auto"),
    )


def _generate_key(file: UploadFile) -> str:
    ext = Path(file.filename).suffix if file.filename else ".pdf"
    return f"{uuid.uuid4().hex}{ext}"


def save_upload(file: UploadFile, content: bytes) -> str:
    """Save uploaded file. Uses S3 (Railway Buckets) if configured, otherwise local disk."""
    key = _generate_key(file)
    s3 = _get_s3_client()

    if s3:
        bucket = os.getenv("BUCKET_NAME", "uploads")
        s3.put_object(Bucket=bucket, Key=key, Body=content, ContentType="application/pdf")
    else:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        (UPLOADS_DIR / key).write_bytes(content)

    return key
