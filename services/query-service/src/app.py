from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
from typing import List, Dict, Any, Optional
import time
import json
from dapr.clients import DaprClient
from .services.colbert_searcher import ColbertSearcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Query Service", description="Search queries with ColbertV2")

# Initialize services
colbert_searcher = ColbertSearcher()
dapr_client = DaprClient()

class SearchQuery(BaseModel):
    query: str
    index_id: Optional[str] = None  # If None, use the latest index
    limit: int = 10

class SearchResult(BaseModel):
    document_id: str
    score: float
    content: str
    metadata: Dict[str, Any] = {}
    cluster: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    processing_time: float
    query: str

@app.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery, x_user_id: Optional[str] = Header(None)):
    """
    Search documents using ColbertV2 late-interaction retrieval
    """
    start_time = time.time()
    user_id = x_user_id or "anonymous"
    logger.info(f"Received search query from user {user_id}: {query.query}")
    
    try:
        # Get the index ID to use
        index_id = query.index_id
        if not index_id:
            # Get the latest index for this user
            # In a real implementation, we would query the state store for the latest index
            # For now, we'll simulate it
            state = await dapr_client.get_state(
                store_name="statestore",
                key=f"latest_index:{user_id}"
            )
            if state.data:
                index_id = state.data.decode("utf-8")
            else:
                raise HTTPException(status_code=404, detail="No index found for this user")
        
        # Get index information
        index_info = await dapr_client.get_state(
            store_name="statestore",
            key=f"index:{index_id}"
        )
        if not index_info.data:
            raise HTTPException(status_code=404, detail="Index not found")
            
        index_info = json.loads(index_info.data.decode("utf-8"))
        index_path = index_info["path"]
        
        # Load the index if not already loaded
        await colbert_searcher.load_index(index_path)
        
        # Perform the search
        raw_results = await colbert_searcher.search(query.query, query.limit)
        
        # Get cluster information
        clusters = await dapr_client.get_state(
            store_name="statestore",
            key=f"clusters:{index_id}"
        )
        cluster_data = {}
        if clusters.data:
            cluster_data = json.loads(clusters.data.decode("utf-8"))
        
        # Format the results
        results = []
        for i, result in enumerate(raw_results):
            document_id = str(result.get("rank", i))
            results.append(SearchResult(
                document_id=document_id,
                score=result.get("score", 0.0),
                content=result.get("content", ""),
                metadata=result.get("metadata", {}),
                cluster=int(cluster_data.get(document_id, -1))
            ))
        
        processing_time = time.time() - start_time
        logger.info(f"Search completed in {processing_time:.2f} seconds")
        
        return SearchResponse(
            results=results,
            processing_time=processing_time,
            query=query.query
        )
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
