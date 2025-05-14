import boto3
import logging
import os
from typing import Optional, List, Dict, Any
import json

logger = logging.getLogger(__name__)

class R2Storage:
    def __init__(self):
        self.bucket_name = os.environ.get("CLOUDFLARE_R2_BUCKET")
        self.account_id = os.environ.get("CLOUDFLARE_R2_ACCOUNT_ID")
        self.access_key = os.environ.get("CLOUDFLARE_R2_ACCESS_KEY")
        self.secret_key = os.environ.get("CLOUDFLARE_R2_SECRET_KEY")
        
        self.client = self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the S3 client for Cloudflare R2"""
        logger.info("Initializing Cloudflare R2 client")
        
        endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        
        return boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        
    async def store_object(self, key: str, data: bytes, metadata: Optional[Dict[str, str]] = None):
        """Store an object in R2"""
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
            
    async def get_object(self, key: str):
        """Retrieve an object from R2"""
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
            
    async def list_objects(self, prefix: str = ""):
        """List objects in R2 with a given prefix"""
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
