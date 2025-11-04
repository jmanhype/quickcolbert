# Operations Guide

## Deployment

### Local Development

```bash
# Start all services with Docker Compose
docker-compose up

# Services will be available at:
# - API Gateway: http://localhost:8080
# - Indexing Service: http://localhost:8000
# - Query Service: http://localhost:8001
# - Storage Service: http://localhost:8002
```

### Kubernetes Deployment

```bash
# Deploy to development environment
kubectl apply -k deploy/kubernetes/overlays/dev

# Check deployment status
kubectl get pods -n quickcolbert

# View logs
kubectl logs -f deployment/api-gateway -n quickcolbert
```

## Configuration

### Environment Variables

#### API Gateway
- `INDEXING_SERVICE_URL`: URL of the indexing service (default: http://localhost:8000)
- `QUERY_SERVICE_URL`: URL of the query service (default: http://localhost:8001)
- `STORAGE_SERVICE_URL`: URL of the storage service (default: http://localhost:8002)

#### Storage Service
- `CLOUDFLARE_R2_BUCKET`: R2 bucket name
- `CLOUDFLARE_R2_ACCOUNT_ID`: Cloudflare account ID
- `CLOUDFLARE_R2_ACCESS_KEY`: R2 access key
- `CLOUDFLARE_R2_SECRET_KEY`: R2 secret key

## Monitoring

### Health Checks

All services expose a `/health` endpoint:

```bash
# Check individual service health
curl http://localhost:8000/health  # Indexing
curl http://localhost:8001/health  # Query
curl http://localhost:8002/health  # Storage

# Check overall system health
curl http://localhost:8080/health
```

### Logs

Services use structured logging at INFO level by default.

```bash
# View logs in Kubernetes
kubectl logs -f deployment/api-gateway
kubectl logs -f deployment/indexing-service
kubectl logs -f deployment/query-service
kubectl logs -f deployment/storage-service
```

## Troubleshooting

### Service Timeout Errors

If you receive 504 timeout errors:
1. Check service health endpoints
2. Review service logs for performance issues
3. Verify network connectivity between services
4. Consider increasing `DEFAULT_TIMEOUT` in API Gateway

### Index Not Found

If searches fail with "Index not found":
1. Verify the index_id is correct
2. Check Dapr state store connectivity
3. Ensure indexing completed successfully
4. Review indexing service logs

### Storage Service Errors

If storage operations fail:
1. Verify R2 credentials are configured correctly
2. Check bucket permissions
3. Ensure network connectivity to Cloudflare R2
4. Review storage service logs for boto3 errors

## Scaling

### Horizontal Scaling

```bash
# Scale individual services
kubectl scale deployment api-gateway --replicas=3
kubectl scale deployment query-service --replicas=5

# Or use Horizontal Pod Autoscaler
kubectl autoscale deployment query-service --min=2 --max=10 --cpu-percent=70
```

### Performance Tuning

- **API Gateway**: Increase timeout for large indexing jobs
- **Indexing Service**: Batch documents for better throughput
- **Query Service**: Pre-load frequently used indexes
- **Storage Service**: Use R2 caching for hot data

## Backup and Recovery

### State Store Backup

Dapr state is critical for index metadata:
```bash
# Backup state store (implementation depends on chosen state store)
# Redis example:
redis-cli --rdb /backup/dump.rdb
```

### R2 Storage

Cloudflare R2 provides automatic redundancy and durability. Consider:
- Regular snapshots of critical indexes
- Version control for important document sets
- Cross-region replication for disaster recovery

## Security Best Practices

1. **API Keys**: Rotate API keys regularly
2. **Environment Variables**: Use Kubernetes secrets for sensitive config
3. **Network Policies**: Restrict service-to-service communication
4. **TLS**: Enable TLS for all external endpoints
5. **Audit Logs**: Enable audit logging in production

## Maintenance

### Updating Services

```bash
# Update container images
kubectl set image deployment/api-gateway api-gateway=quickcolbert/api-gateway:v1.1

# Rolling update with zero downtime
kubectl rollout status deployment/api-gateway

# Rollback if needed
kubectl rollout undo deployment/api-gateway
```

### Database Migrations

State schema changes should be handled carefully:
1. Deploy backward-compatible changes first
2. Migrate data in the background
3. Deploy code that uses new schema
4. Clean up old schema after verification
