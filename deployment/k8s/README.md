# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Email Agent API.

## Prerequisites

- Kubernetes cluster (Minikube for local testing)
- kubectl CLI installed
- Docker image built: `middlewareapp:latest`

## Quick Start with Minikube

### 1. Start Minikube

```bash
minikube start
```

### 2. Build Docker Image in Minikube

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build image (from project root)
docker build -t middlewareapp:latest -f deployment/Dockerfile .
```

### 3. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f deployment/k8s/

# Verify deployment
kubectl get all -n middlewareapp

# Check pod logs
kubectl logs -n middlewareapp -l app=email-agent --all-containers=true
```

### 4. Access the Service

```bash
# Option 1: Port forwarding
kubectl port-forward -n middlewareapp svc/email-agent-service 8000:8000

# Option 2: Minikube service (opens in browser)
minikube service email-agent-service -n middlewareapp

# Option 3: Get service URL
minikube service email-agent-service -n middlewareapp --url
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Or if using minikube service URL
curl $(minikube service email-agent-service -n middlewareapp --url)/health
```

## Configuration

### Update ConfigMap

Edit `configmap.yaml` to change:
- LLM endpoint URL
- Model name
- Temperature
- Log level

Then apply:
```bash
kubectl apply -f deployment/k8s/configmap.yaml
kubectl rollout restart deployment/email-agent -n middlewareapp
```

### Update Secret

```bash
# Create new secret
kubectl create secret generic email-agent-secret \
  --from-literal=LLM_API_KEY=your-new-api-key \
  -n middlewareapp \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment
kubectl rollout restart deployment/email-agent -n middlewareapp
```

## Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment/email-agent -n middlewareapp --replicas=3

# Enable autoscaling
kubectl autoscale deployment/email-agent -n middlewareapp \
  --cpu-percent=70 --min=2 --max=5
```

## Monitoring

```bash
# Watch pods
kubectl get pods -n middlewareapp -w

# View logs
kubectl logs -n middlewareapp -l app=email-agent -f

# Describe pod for details
kubectl describe pod -n middlewareapp <pod-name>

# Check resource usage
kubectl top pods -n middlewareapp
```

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod -n middlewareapp <pod-name>

# Check logs
kubectl logs -n middlewareapp <pod-name>

# Check if image exists
minikube ssh
docker images | grep middlewareapp
```

### Service not accessible

```bash
# Verify service endpoints
kubectl get endpoints -n middlewareapp

# Check if pods are ready
kubectl get pods -n middlewareapp

# For LoadBalancer with Minikube, run:
minikube tunnel
```

### Health check failing

```bash
# Exec into pod
kubectl exec -it -n middlewareapp <pod-name> -- /bin/bash

# Test health endpoint from inside pod
curl http://localhost:8000/health
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace middlewareapp

# Or delete individual resources
kubectl delete -f deployment/k8s/
```

## Files

- `namespace.yaml` - Creates middlewareapp namespace
- `configmap.yaml` - Non-sensitive configuration
- `secret.yaml` - Sensitive data (API keys)
- `deployment.yaml` - Application deployment (2 replicas)
- `service.yaml` - LoadBalancer service exposing port 8000
