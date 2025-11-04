import boto3
import logging
import os
from typing import Optional, List, Dict, Any
from botocore.client import BaseClient

logger = logging.getLogger(__name__)

class R2Storage:
    """Cloudflare R2 storage client using S3-compatible API"""

    def __init__(self) -> None:
        """Initialize R2 storage client with credentials from environment"""
        self.bucket_name: Optional[str] = os.environ.get("CLOUDFLARE_R2_BUCKET")
        self.account_id: Optional[str] = os.environ.get("CLOUDFLARE_R2_ACCOUNT_ID")
        self.access_key: Optional[str] = os.environ.get("CLOUDFLARE_R2_ACCESS_KEY")
        self.secret_key: Optional[str] = os.environ.get("CLOUDFLARE_R2_SECRET_KEY")

        self.client: BaseClient = self._initialize_client()

    def _initialize_client(self) -> BaseClient:
        """Initialize the S3 client for Cloudflare R2

        Returns:
            Configured boto3 S3 client
        """
        logger.info("Initializing Cloudflare R2 client")

        endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"

        return boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        
    async def store_object(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Store an object in R2

        Args:
            key: Object key/path
            data: Binary data to store
            metadata: Optional metadata dictionary

        Returns:
            True if successful

        Raises:
            Exception: If storage operation fails
        """
        logger.info(f"Storing object with key: {key}")

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                Metadata=metadata or {}
            )
            logger.info(f"Successfully stored object with key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error storing object with key {key}: {str(e)}")
            raise

    async def get_object(self, key: str) -> bytes:
        """Retrieve an object from R2

        Args:
            key: Object key/path

        Returns:
            Binary data of the object

        Raises:
            Exception: If retrieval operation fails
        """
        logger.info(f"Retrieving object with key: {key}")

        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            data = response['Body'].read()
            logger.info(f"Successfully retrieved object with key: {key}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving object with key {key}: {str(e)}")
            raise

    async def list_objects(self, prefix: str = "") -> List[str]:
        """List objects in R2 with a given prefix

        Args:
            prefix: Object key prefix to filter by

        Returns:
            List of object keys

        Raises:
            Exception: If list operation fails
        """
        logger.info(f"Listing objects with prefix: {prefix}")

        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            objects = []
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]

            logger.info(f"Found {len(objects)} objects with prefix: {prefix}")
            return objects
        except Exception as e:
            logger.error(f"Error listing objects with prefix {prefix}: {str(e)}")
            raise
