from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import logging
from typing import List, Dict, Any, Optional
import time
import json
from dapr.clients import DaprClient
from .services.colbert_indexer import ColbertIndexer
from .services.kmeans_clusterer import KMeansClusterer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Indexing Service", description="Document indexing with ColbertV2")

# Initialize services
colbert_indexer = ColbertIndexer()
kmeans_clusterer = KMeansClusterer(n_clusters=100)
dapr_client = DaprClient()

class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = {}

class IndexResponse(BaseModel):
    index_id: str
    document_count: int
    processing_time: float

@app.post("/index", response_model=IndexResponse)
async def index_documents(documents: List[Document], x_user_id: Optional[str] = Header(None)):
    """
    Index a batch of documents using ColbertV2
    """
    start_time = time.time()
    user_id = x_user_id or "anonymous"
    logger.info(f"Received indexing request for {len(documents)} documents from user {user_id}")
    
    # Create a unique index name
    index_name = f"index_{int(time.time())}_{user_id}"
    
    try:
        # Index documents with ColbertV2
        index_path = await colbert_indexer.index_documents(
            [doc.dict() for doc in documents], 
            index_name
        )
        
        # Get document embeddings (in a real implementation)
        # For now, we'll simulate them
        embeddings = [[0.1] * 128 for _ in range(len(documents))]
        
        # Cluster documents using FastKMeans
        cluster_labels = await kmeans_clusterer.fit_predict(embeddings)
        
        # Store index information in the state store
        await dapr_client.save_state(
            store_name="statestore",
            key=f"index:{index_name}",
            value={
                "path": index_path,
                "document_count": len(documents),
                "created_at": time.time(),
                "user_id": user_id
            }
        )
        
        # Store clusters in the state store
        await dapr_client.save_state(
            store_name="statestore",
            key=f"clusters:{index_name}",
            value={str(i): cluster_labels[i] for i in range(len(documents))}
        )
        
        # Publish an event to notify other services
        await dapr_client.publish_event(
            pubsub_name="pubsub",
            topic_name="index-created",
            data={
                "index_name": index_name,
                "document_count": len(documents),
                "user_id": user_id
            }
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Indexed {len(documents)} documents in {processing_time:.2f} seconds")
        
        return IndexResponse(
            index_id=index_name,
            document_count=len(documents),
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error indexing documents: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
