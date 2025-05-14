# QuickColbert

A scalable, high-performance search service using ColbertV2 late-interaction retrieval technology.

## Features

- High-accuracy semantic search using ColbertV2
- Efficient document indexing with FastKMeans clustering
- Scalable service architecture
- Cloud-native deployment

## Getting Started

### Prerequisites
- Docker
- Kubernetes
- Python 3.9+

### Quick Start
```bash
# Run locally
docker-compose up

# Deploy to Kubernetes
kubectl apply -k deploy/kubernetes/overlays/dev
```

## Documentation
- Architecture Overview (docs/architecture/README.md)
- API Documentation (docs/api/README.md)
- Operational Guide (docs/operations/README.md)
