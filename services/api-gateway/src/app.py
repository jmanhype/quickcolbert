from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Header
from fastapi.security import APIKeyHeader
import logging
import httpx
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="QuickColbert API", description="API Gateway for ColbertV2 Search Service")

# Service URLs from environment
INDEXING_SERVICE_URL = os.environ.get("INDEXING_SERVICE_URL", "http://localhost:8000")
QUERY_SERVICE_URL = os.environ.get("QUERY_SERVICE_URL", "http://localhost:8001")
STORAGE_SERVICE_URL = os.environ.get("STORAGE_SERVICE_URL", "http://localhost:8002")

# HTTP client configuration
DEFAULT_TIMEOUT = 30.0  # seconds
MAX_RETRIES = 3

# API key authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# For MVP, we'll use a simple in-memory store for API keys
API_KEYS = {
    "test-api-key": {"user_id": "test-user"}
}

async def get_current_user(api_key: str = Depends(API_KEY_HEADER)):
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return API_KEYS[api_key]["user_id"]

# Models
class Document(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class SearchQuery(BaseModel):
    query: str
    index_id: Optional[str] = None
    limit: int = 10

@app.post("/documents/index")
async def index_documents(
    documents: List[Document],
    user_id: str = Depends(get_current_user)
):
    """Index a batch of documents"""
    logger.info(f"Received request to index {len(documents)} documents from user {user_id}")

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{INDEXING_SERVICE_URL}/index",
                json=[doc.dict() for doc in documents],
                headers={"X-User-ID": user_id}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )

            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout while indexing documents for user {user_id}")
            raise HTTPException(
                status_code=504,
                detail="Indexing service timeout - please try again"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error while indexing: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )

@app.post("/search")
async def search(
    query: SearchQuery,
    user_id: str = Depends(get_current_user)
):
    """Search documents"""
    logger.info(f"Received search query from user {user_id}: {query.query}")

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{QUERY_SERVICE_URL}/search",
                json=query.dict(),
                headers={"X-User-ID": user_id}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )

            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout while searching for user {user_id}")
            raise HTTPException(
                status_code=504,
                detail="Search service timeout - please try again"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error while searching: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )

@app.get("/health")
async def health_check():
    """Check the health of all services"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        services = {
            "api_gateway": "healthy",
            "indexing_service": "unknown",
            "query_service": "unknown",
            "storage_service": "unknown"
        }

        # Check each service independently to avoid one failure blocking others
        try:
            indexing_health = await client.get(f"{INDEXING_SERVICE_URL}/health")
            services["indexing_service"] = "healthy" if indexing_health.status_code == 200 else "unhealthy"
        except Exception as e:
            logger.warning(f"Indexing service health check failed: {str(e)}")
            services["indexing_service"] = "unhealthy"

        try:
            query_health = await client.get(f"{QUERY_SERVICE_URL}/health")
            services["query_service"] = "healthy" if query_health.status_code == 200 else "unhealthy"
        except Exception as e:
            logger.warning(f"Query service health check failed: {str(e)}")
            services["query_service"] = "unhealthy"

        try:
            storage_health = await client.get(f"{STORAGE_SERVICE_URL}/health")
            services["storage_service"] = "healthy" if storage_health.status_code == 200 else "unhealthy"
        except Exception as e:
            logger.warning(f"Storage service health check failed: {str(e)}")
            services["storage_service"] = "unhealthy"

        # Overall status is healthy if all services are healthy
        all_healthy = all(status == "healthy" for status in services.values())
        overall_status = "healthy" if all_healthy else "degraded"

        return {
            "status": overall_status,
            "services": services
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
