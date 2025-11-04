# API Documentation

## Authentication

All API requests require an API key provided via the `X-API-Key` header.

```bash
curl -H "X-API-Key: your-api-key" https://api.quickcolbert.com/health
```

## Endpoints

### Health Check

**GET** `/health`

Check the health status of all services.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "api_gateway": "healthy",
    "indexing_service": "healthy",
    "query_service": "healthy",
    "storage_service": "healthy"
  }
}
```

### Index Documents

**POST** `/documents/index`

Index a batch of documents for semantic search.

**Request Body:**
```json
[
  {
    "content": "Document content here",
    "metadata": {
      "source": "example.pdf",
      "page": 1
    }
  }
]
```

**Response:**
```json
{
  "index_id": "index_1234567890_user123",
  "document_count": 1,
  "processing_time": 2.45
}
```

**Error Codes:**
- `401`: Invalid API key
- `503`: Indexing service unavailable
- `504`: Indexing timeout

### Search Documents

**POST** `/search`

Search indexed documents using semantic search.

**Request Body:**
```json
{
  "query": "What is the capital of France?",
  "index_id": "index_1234567890_user123",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "0",
      "score": 0.95,
      "content": "Paris is the capital of France",
      "metadata": {},
      "cluster": 5
    }
  ],
  "processing_time": 0.23,
  "query": "What is the capital of France?"
}
```

**Error Codes:**
- `401`: Invalid API key
- `404`: Index not found
- `503`: Query service unavailable
- `504`: Search timeout

## Rate Limits

Currently no rate limits are enforced in the MVP version.

## SDK Examples

### Python

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "https://api.quickcolbert.com"

headers = {"X-API-Key": API_KEY}

# Index documents
documents = [
    {"content": "Document 1", "metadata": {}},
    {"content": "Document 2", "metadata": {}}
]
response = requests.post(
    f"{BASE_URL}/documents/index",
    json=documents,
    headers=headers
)
index_id = response.json()["index_id"]

# Search
query = {"query": "search query", "index_id": index_id, "limit": 5}
response = requests.post(
    f"{BASE_URL}/search",
    json=query,
    headers=headers
)
results = response.json()["results"]
```

### cURL

```bash
# Index documents
curl -X POST https://api.quickcolbert.com/documents/index \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '[{"content": "Example document", "metadata": {}}]'

# Search
curl -X POST https://api.quickcolbert.com/search \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "search query", "limit": 10}'
```
