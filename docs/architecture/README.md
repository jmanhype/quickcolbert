# Architecture Overview

## System Architecture

QuickColbert is a distributed search service built with a microservices architecture, utilizing ColbertV2 for high-accuracy semantic search.

## Core Components

### API Gateway
- **Port**: 8080
- **Responsibility**: Authentication, request routing, and API orchestration
- **Tech Stack**: FastAPI, httpx
- **Key Features**:
  - API key authentication
  - Request timeout handling
  - Service health monitoring
  - Error handling and retry logic

### Indexing Service
- **Port**: 8000
- **Responsibility**: Document indexing with ColbertV2
- **Tech Stack**: FastAPI, RAGatouille (ColbertV2), Dapr
- **Key Features**:
  - ColbertV2 late-interaction indexing
  - FastKMeans clustering for document organization
  - State management via Dapr
  - Event publishing for index creation

### Query Service
- **Port**: 8001
- **Responsibility**: Search query processing
- **Tech Stack**: FastAPI, RAGatouille (ColbertV2), Dapr
- **Key Features**:
  - ColbertV2 semantic search
  - Index loading and caching
  - Cluster-aware result ranking
  - State retrieval via Dapr

### Storage Service
- **Port**: 8002
- **Responsibility**: Object storage with Cloudflare R2
- **Tech Stack**: FastAPI, boto3
- **Key Features**:
  - S3-compatible API for R2
  - Index and document persistence
  - Metadata management

## Data Flow

### Indexing Flow
```
User → API Gateway → Indexing Service → Storage Service
                          ↓
                    Dapr State Store
                          ↓
                      Pub/Sub Event
```

### Query Flow
```
User → API Gateway → Query Service → Dapr State Store
                          ↓
                    Search Results
```

## Technology Stack

- **Application Framework**: FastAPI
- **ML/Search**: ColbertV2 (via RAGatouille)
- **Clustering**: FastKMeans
- **State Management**: Dapr
- **Storage**: Cloudflare R2 (S3-compatible)
- **Deployment**: Kubernetes, Docker
- **Language**: Python 3.9+

## Scalability Considerations

- Services are independently scalable via Kubernetes
- Dapr provides service mesh capabilities
- R2 storage offers unlimited scalability
- ColbertV2 indexes can be cached and distributed

## Security

- API key authentication at gateway level
- Service-to-service communication via Dapr
- Environment-based configuration
- No hardcoded secrets
