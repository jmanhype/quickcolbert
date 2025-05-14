#!/bin/bash
set -e

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env file from .env.example. Please update with your actual values."
  exit 1
fi

# Start the local development environment
docker-compose up -d

echo "Local development environment is running."
echo "API Gateway: http://localhost:8080"
echo "Indexing Service: http://localhost:8000"
echo "Query Service: http://localhost:8001"
echo "Storage Service: http://localhost:8002"
