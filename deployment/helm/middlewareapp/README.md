# Email Agent Helm Chart

A Helm chart for deploying the Email Agent API to Kubernetes with support for development and production environments.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Docker image built: `middlewareapp:latest`

## Installation

### Install with default values

```bash
helm install email-agent ./deployment/helm/middlewareapp/ \
  -n middlewareapp --create-namespace
```

### Install for development

```bash
helm install email-agent ./deployment/helm/middlewareapp/ \
  -f ./deployment/helm/middlewareapp/values-dev.yaml \
  -n middlewareapp --create-namespace
```

### Install for production

```bash
helm install email-agent ./deployment/helm/middlewareapp/ \
  -f ./deployment/helm/middlewareapp/values-prod.yaml \
  -n middlewareapp --create-namespace
```

### Install with custom values

```bash
helm install email-agent ./deployment/helm/middlewareapp/ \
  --set replicaCount=3 \
  --set env.LOG_LEVEL=DEBUG \
  --set secrets.LLM_API_KEY=your-api-key \
  -n middlewareapp --create-namespace
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `middlewareapp` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `replicaCount` | Number of replicas | `2` |
| `service.type` | Kubernetes service type | `LoadBalancer` |
| `service.port` | Service port | `8000` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `autoscaling.enabled` | Enable autoscaling | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `5` |
| `env.LLM_BASE_URL` | LLM endpoint URL | `http://192.168.1.55:1234/v1/` |
| `env.LLM_MODEL_NAME` | LLM model name | `qwen/qwen3-32` |
| `env.LOG_LEVEL` | Application log level | `INFO` |
| `secrets.LLM_API_KEY` | LLM API key | `sk-dummy` |

## Upgrading

### Upgrade with new values

```bash
helm upgrade email-agent ./deployment/helm/middlewareapp/ \
  --set replicaCount=5 \
  -n middlewareapp
```

### Upgrade to production configuration

```bash
helm upgrade email-agent ./deployment/helm/middlewareapp/ \
  -f ./deployment/helm/middlewareapp/values-prod.yaml \
  -n middlewareapp
```

## Rollback

```bash
# View release history
helm history email-agent -n middlewareapp

# Rollback to previous revision
helm rollback email-agent -n middlewareapp

# Rollback to specific revision
helm rollback email-agent 2 -n middlewareapp
```

## Uninstallation

```bash
helm uninstall email-agent -n middlewareapp
```

## Testing with Minikube

```bash
# Start Minikube
minikube start

# Build image in Minikube's Docker
eval $(minikube docker-env)
docker build -t middlewareapp:latest -f deployment/Dockerfile .

# Install Helm chart
helm install email-agent ./deployment/helm/middlewareapp/ \
  -n middlewareapp --create-namespace

# Access the service
minikube service email-agent-middlewareapp-service -n middlewareapp

# Or port-forward
kubectl port-forward -n middlewareapp svc/email-agent-middlewareapp-service 8000:8000
```

## Scaling

### Manual scaling

```bash
helm upgrade email-agent ./deployment/helm/middlewareapp/ \
  --set replicaCount=5 \
  -n middlewareapp
```

### Enable autoscaling

```bash
helm upgrade email-agent ./deployment/helm/middlewareapp/ \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10 \
  -n middlewareapp
```

## Monitoring

```bash
# Check deployment status
helm status email-agent -n middlewareapp

# View pods
kubectl get pods -n middlewareapp

# View logs
kubectl logs -n middlewareapp -l app.kubernetes.io/name=middlewareapp -f

# Check resource usage
kubectl top pods -n middlewareapp
```

## Environment-Specific Values

### Development (values-dev.yaml)
- 1 replica
- Lower resource limits
- NodePort service
- DEBUG log level

### Production (values-prod.yaml)
- 3 replicas
- Higher resource limits
- Autoscaling enabled (3-10 replicas)
- LoadBalancer service
- WARNING log level

## Troubleshooting

### View Helm values

```bash
helm get values email-agent -n middlewareapp
```

### View all Kubernetes resources

```bash
helm get manifest email-agent -n middlewareapp
```

### Debug installation

```bash
helm install email-agent ./deployment/helm/middlewareapp/ \
  --dry-run --debug \
  -n middlewareapp
```

### Template rendering

```bash
helm template email-agent ./deployment/helm/middlewareapp/ \
  -n middlewareapp
```
