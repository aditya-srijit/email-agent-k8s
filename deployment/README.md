# Deployment Guide

This directory contains all deployment configurations for the Email Agent API.

## Quick Links

- **[Docker Setup](./Dockerfile)** - Build and run with Docker
- **[Docker Compose](./docker-compose.yml)** - Local development with Docker Compose
- **[Kubernetes](./k8s/README.md)** - Deploy to Kubernetes/Minikube
- **[Helm Chart](./helm/middlewareapp/README.md)** - Deploy with Helm

## Deployment Options

### Option 1: Docker

```bash
# Build
docker build -t middlewareapp:latest -f deployment/Dockerfile .

# Run
docker run -p 8000:8000 --env-file .env middlewareapp:latest

# Test
curl http://localhost:8000/health
```

### Option 2: Docker Compose

```bash
cd deployment
docker-compose up -d
docker-compose logs -f
curl http://localhost:8000/health
```

### Option 3: Kubernetes (Raw Manifests)

```bash
# Build image for Minikube
eval $(minikube docker-env)
docker build -t middlewareapp:latest -f deployment/Dockerfile .

# Deploy
kubectl apply -f deployment/k8s/

# Access
kubectl port-forward -n middlewareapp svc/email-agent-service 8000:8000
```

### Option 4: Helm (Recommended for Production)

```bash
# Build image for Minikube
eval $(minikube docker-env)
docker build -t middlewareapp:latest -f deployment/Dockerfile .

# Install
helm install email-agent deployment/helm/middlewareapp/ \
  -n middlewareapp --create-namespace

# Access
minikube service email-agent-middlewareapp-service -n middlewareapp
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
LLM_BASE_URL=http://192.168.1.55:1234/v1/
LLM_API_KEY=sk-dummy
LLM_MODEL_NAME=qwen/qwen3-32
LLM_TEMPERATURE=0.7
PORT=8000
LOG_LEVEL=INFO
```

## Architecture

```
email-agent-k8s/
├── api.py                 # FastAPI application
├── email_agent/          # LangGraph agent code
├── deployment/
│   ├── Dockerfile        # Multi-stage Docker build
│   ├── docker-compose.yml
│   ├── k8s/             # Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── README.md
│   └── helm/            # Helm charts
│       └── middlewareapp/
│           ├── Chart.yaml
│           ├── values.yaml
│           ├── values-dev.yaml
│           ├── values-prod.yaml
│           ├── templates/
│           └── README.md
```

## Scaling

### Kubernetes
```bash
kubectl scale deployment/email-agent -n middlewareapp --replicas=5
```

### Helm
```bash
# Manual scaling
helm upgrade email-agent deployment/helm/middlewareapp/ \
  --set replicaCount=5 -n middlewareapp

# Enable autoscaling
helm upgrade email-agent deployment/helm/middlewareapp/ \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10 \
  -n middlewareapp
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T07:00:00",
  "version": "0.1.0",
  "service": "email-agent"
}
```

### Logs

**Docker:**
```bash
docker logs <container-id> -f
```

**Docker Compose:**
```bash
docker-compose logs -f
```

**Kubernetes:**
```bash
kubectl logs -n middlewareapp -l app=email-agent -f
```

## Important Notes

### LLM Endpoint
The LLM endpoint is configured via `LLM_BASE_URL`. Ensure this is accessible from your deployment environment (Docker container, Kubernetes pod).

### State Persistence
The application uses `InMemorySaver` for state management. This means:
- State is lost on restart
- Multiple replicas don't share state
- Consider using Redis or PostgreSQL for production
  
