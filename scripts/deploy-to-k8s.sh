#!/bin/bash
set -e

# Usage: ./scripts/deploy-to-k8s.sh [dev|prod]
ENVIRONMENT=${1:-dev}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install it first."
    exit 1
fi

# Check if kustomize is installed
if ! command -v kustomize &> /dev/null; then
    echo "kustomize is not installed. Please install it first."
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace quickcolbert-${ENVIRONMENT} --dry-run=client -o yaml | kubectl apply -f -

# Create secrets
echo "Creating Cloudflare R2 secret..."
kubectl create secret generic cloudflare-r2 \
  --namespace=quickcolbert-${ENVIRONMENT} \
  --from-literal=bucket=${CLOUDFLARE_R2_BUCKET} \
  --from-literal=account-id=${CLOUDFLARE_R2_ACCOUNT_ID} \
  --from-literal=access-key=${CLOUDFLARE_R2_ACCESS_KEY} \
  --from-literal=secret-key=${CLOUDFLARE_R2_SECRET_KEY} \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Creating RunPod API key secret..."
kubectl create secret generic runpod-api-key \
  --namespace=quickcolbert-${ENVIRONMENT} \
  --from-literal=api-key=${RUNPOD_API_KEY} \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Creating Redis password secret..."
kubectl create secret generic redis-password \
  --namespace=quickcolbert-${ENVIRONMENT} \
  --from-literal=password=${REDIS_PASSWORD} \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply Dapr components
echo "Applying Dapr components..."
kubectl apply -f deploy/dapr/components/ -n quickcolbert-${ENVIRONMENT}

# Apply Kubernetes manifests using kustomize
echo "Deploying services..."
kubectl apply -k deploy/kubernetes/overlays/${ENVIRONMENT}

echo "Deployment to ${ENVIRONMENT} environment completed."
