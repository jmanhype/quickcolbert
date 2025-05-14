from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import logging
from typing import List, Dict, Any, Optional
import json
from .services.r2_storage import R2Storage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Storage Service", description="Document and index storage with Cloudflare R2")

# Initialize R2 storage service
r2_storage = R2Storage()

class ObjectMetadata(BaseModel):
    key: str
    size: int
    last_modified: str
    metadata: Dict[str, str] = {}

@app.post("/objects/{key}")
async def store_object(
    key: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """Store an object in Cloudflare R2"""
    logger.info(f"Received request to store object with key: {key}")
    
    content = await file.read()
    meta = {}
    
    if metadata:
        try:
            meta = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata format")
    
    await r2_storage.store_object(key, content, meta)
    
    return {"key": key, "size": len(content), "metadata": meta}

@app.get("/objects/{key}")
async def get_object(key: str):
    """Retrieve an object from Cloudflare R2"""
    logger.info(f"Received request to retrieve object with key: {key}")
    
    try:
        data = await r2_storage.get_object(key)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Object not found: {str(e)}")

@app.get("/objects")
async def list_objects(prefix: str = ""):
    """List objects in Cloudflare R2 with a given prefix"""
    logger.info(f"Received request to list objects with prefix: {prefix}")
    
    try:
        objects = await r2_storage.list_objects(prefix)
        return {"objects": objects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing objects: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
