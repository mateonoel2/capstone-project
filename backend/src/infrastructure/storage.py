import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from src.core.logger import get_logger

UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"

PRESIGNED_URL_EXPIRY = 300  # 5 minutes

logger = get_logger("storage")


def generate_key(filename: str) -> str:
    ext = Path(filename).suffix if filename else ".pdf"
    return f"{uuid.uuid4().hex}{ext}"


class StorageBackend(ABC):
    @abstractmethod
    def generate_upload_url(self, key: str, content_type: str) -> str | None:
        """Return a presigned PUT URL for direct browser upload, or None."""
        ...

    @abstractmethod
    def save(self, key: str, content: bytes) -> None: ...

    @abstractmethod
    def download(self, key: str) -> bytes: ...

    def configure_cors(self, allowed_origins: list[str]) -> None:
        """Configure CORS on the storage bucket. No-op by default."""


class LocalStorage(StorageBackend):
    def generate_upload_url(self, key: str, content_type: str) -> str | None:
        return None

    def save(self, key: str, content: bytes) -> None:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        (UPLOADS_DIR / key).write_bytes(content)

    def download(self, key: str) -> bytes:
        path = UPLOADS_DIR / key
        if not path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return path.read_bytes()


class S3Storage(StorageBackend):
    def __init__(self) -> None:
        endpoint = os.getenv("AWS_ENDPOINT_URL")
        public_endpoint = os.getenv("AWS_PUBLIC_ENDPOINT_URL", endpoint)
        kwargs = {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region_name": os.getenv("AWS_DEFAULT_REGION", "auto"),
        }
        self._client = boto3.client("s3", endpoint_url=endpoint, **kwargs)
        # Presigned URLs must use a browser-reachable endpoint
        if public_endpoint != endpoint:
            self._public_client = boto3.client("s3", endpoint_url=public_endpoint, **kwargs)
        else:
            self._public_client = self._client
        self._bucket = os.getenv("AWS_S3_BUCKET_NAME", "uploads")

    def generate_upload_url(self, key: str, content_type: str) -> str | None:
        return self._public_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self._bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=PRESIGNED_URL_EXPIRY,
        )

    def save(self, key: str, content: bytes) -> None:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=content)

    def download(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def configure_cors(self, allowed_origins: list[str]) -> None:
        cors_config = {
            "CORSRules": [
                {
                    "AllowedOrigins": allowed_origins,
                    "AllowedMethods": ["GET", "PUT"],
                    "AllowedHeaders": ["*"],
                    "ExposeHeaders": ["ETag"],
                }
            ]
        }
        try:
            self._client.put_bucket_cors(Bucket=self._bucket, CORSConfiguration=cors_config)
            logger.info("S3 CORS configured for bucket '%s'", self._bucket)
        except ClientError as e:
            logger.warning("Failed to configure S3 CORS: %s", e)


def get_storage() -> StorageBackend:
    if os.getenv("AWS_ENDPOINT_URL"):
        return S3Storage()
    return LocalStorage()
