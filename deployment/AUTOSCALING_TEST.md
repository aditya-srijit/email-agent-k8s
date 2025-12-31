# Autoscaling Test Guide

## Prerequisites

Make sure these are running:

1. **Port forwarding** (in one terminal):
   ```bash
   kubectl port-forward -n middlewareapp svc/email-agent-service 8000:8000
   ```

## Step-by-Step Test

### 1. Check Current Status

```bash
# View current pods
kubectl get pods -n middlewareapp

# View HPA status
kubectl get hpa -n middlewareapp

# View current resource usage
kubectl top pods -n middlewareapp
```

### 2. Monitor Autoscaling (Open a new terminal for this)

```bash
# Watch HPA in real-time
kubectl get hpa -n middlewareapp -w

# Or watch pods being created/deleted
kubectl get pods -n middlewareapp -w
```

### 3. Generate Load

**Option A: Using the Python script (Recommended)**
```bash
# Make sure you're in the virtual environment
.venv\Scripts\Activate.ps1

# Install aiohttp if needed
pip install aiohttp

# Run the load test
python deployment/load_test.py
```

**Option B: Using PowerShell loop (Simple)**
```powershell
# Generate load with simple curl loop
$i = 0
while ($i -lt 1000) {
    Start-Job -ScriptBlock { curl http://localhost:8000/health }
    $i++
}
```

**Option C: Using Apache Bench (if installed)**
```bash
ab -n 10000 -c 100 http://localhost:8000/health
```

### 4. What to Expect

1. **Initial state**: 1-2 pods running, CPU usage low
2. **During load**: 
   - CPU usage increases
   - When CPU > 10%, HPA triggers
   - New pods are created (up to max 5)
   - Load is distributed across pods
3. **After load stops**:
   - CPU usage decreases
   - After ~5 minutes of low usage, HPA scales down
   - Eventually returns to minimum (1 pod)

### 5. Check Results

```bash
# View HPA events
kubectl describe hpa email-agent -n middlewareapp

# View pod scaling events
kubectl get events -n middlewareapp --sort-by='.lastTimestamp'

# Current resource usage
kubectl top pods -n middlewareapp
```

## Troubleshooting

### CPU shows `<unknown>`
- Metrics server needs time to collect data (wait 1-2 minutes)
- Check metrics server: `kubectl get pods -n kube-system | grep metrics`
- Docker Desktop's metrics server may need enabling

### Pods not scaling up
- Verify HPA config: `kubectl get hpa -n middlewareapp -o yaml`
- Check CPU threshold is low (10%)
- Ensure load is actually hitting the pods
- Port-forward must be active

### Scaling takes too long
- Default scale-up delay is 3 minutes
- Scale-down delay is 5 minutes
- This is normal Kubernetes behavior

## Quick Test Commands

```bash
# Terminal 1: Port forward
kubectl port-forward -n middlewareapp svc/email-agent-service 8000:8000

# Terminal 2: Watch scaling
kubectl get hpa -n middlewareapp -w

# Terminal 3: Generate load
python deployment/load_test.py

# Terminal 4: Monitor pods
kubectl get pods -n middlewareapp -w
```
