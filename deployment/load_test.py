"""
Load testing script to trigger Kubernetes autoscaling.

This script generates HTTP requests to the FastAPI service to increase CPU usage
and trigger the HorizontalPodAutoscaler.
"""

import asyncio
import aiohttp
import time
from datetime import datetime

# Configuration
SERVICE_URL = "http://localhost:8000/health"
CONCURRENT_REQUESTS = 50  # Number of concurrent requests
DURATION_SECONDS = 300  # Run for 5 minutes
REQUEST_DELAY = 0.01  # Small delay between requests (in seconds)


async def make_request(session, request_num):
    """Make a single HTTP request."""
    try:
        async with session.get(SERVICE_URL) as response:
            status = response.status
            return f"Request {request_num}: Status {status}"
    except Exception as e:
        return f"Request {request_num}: Error - {e}"


async def load_generator():
    """Generate load by making concurrent requests."""
    print(f"🚀 Starting load test at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Target: {SERVICE_URL}")
    print(f"Concurrent requests: {CONCURRENT_REQUESTS}")
    print(f"Duration: {DURATION_SECONDS} seconds")
    print("-" * 60)
    
    start_time = time.time()
    request_count = 0
    
    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < DURATION_SECONDS:
            # Create batch of concurrent requests
            tasks = [
                make_request(session, request_count + i)
                for i in range(CONCURRENT_REQUESTS)
            ]
            
            # Execute requests concurrently
            results = await asyncio.gather(*tasks)
            request_count += CONCURRENT_REQUESTS
            
            # Print progress every 100 requests
            if request_count % 100 == 0:
                elapsed = time.time() - start_time
                rate = request_count / elapsed
                print(f"✓ Completed {request_count} requests | "
                      f"Rate: {rate:.1f} req/s | "
                      f"Elapsed: {elapsed:.1f}s")
            
            # Small delay to control request rate
            await asyncio.sleep(REQUEST_DELAY)
    
    total_time = time.time() - start_time
    print("-" * 60)
    print(f"✅ Load test completed!")
    print(f"Total requests: {request_count}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average rate: {request_count/total_time:.1f} requests/second")
    print(f"\n💡 Check autoscaling with: kubectl get hpa -n middlewareapp -w")


if __name__ == "__main__":
    print("=" * 60)
    print("KUBERNETES AUTOSCALING LOAD TEST")
    print("=" * 60)
    print("\n⚠️  Make sure kubectl port-forward is running:")
    print("   kubectl port-forward -n middlewareapp svc/email-agent-service 8000:8000")
    print("\n📊 Monitor scaling in another terminal:")
    print("   kubectl get hpa -n middlewareapp -w")
    print("   kubectl get pods -n middlewareapp -w")
    print("\n")
    
    try:
        asyncio.run(load_generator())
    except KeyboardInterrupt:
        print("\n\n⚠️  Load test interrupted by user")
