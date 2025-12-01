# Vertex AI Agent Engine Deployment

Deploy the Factory Business AI Agent to Vertex AI Agent Engine (Reasoning Engine).

## Overview

**Vertex AI Agent Engine** provides:

- ✅ Fully managed deployment
- ✅ Built-in tracing and monitoring
- ✅ Automatic scalability
- ✅ Session management
- ✅ Streaming support via SSE
- ✅ REST API endpoint with authentication

**Best for:** Production AI agents with enterprise requirements

## Prerequisites

1. **Google Cloud Project** with Vertex AI enabled
2. **GCS Bucket** for agent artifacts
3. **Python 3.11+** and build tools
4. **gcloud CLI** authenticated

## Quick Deploy

```bash
# 1. Build the agent package
bash scripts/build_package.sh

# 2. Configure (edit config.env)
nano config.env

# 3. Deploy to Agent Engine
source config.env
python deploy.py
```

## Detailed Steps

### Step 1: Create Storage Bucket

```bash
# Create bucket for agent artifacts
export PROJECT_ID="your-project-id"
export BUCKET_NAME="${PROJECT_ID}-agent-storage"

gsutil mb -p ${PROJECT_ID} -l global gs://${BUCKET_NAME}
```

### Step 2: Configure Environment

Edit `config.env`:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_CLOUD_STORAGE_BUCKET="your-bucket-name"
```

### Step 3: Build Agent Package

```bash
bash scripts/build_package.sh
```

This creates a wheel file (`.whl`) containing your agent code.

### Step 4: Deploy

```bash
source config.env
python deploy.py
```

Deployment takes 5-10 minutes and includes:

- Uploading agent package to GCS
- Creating Reasoning Engine resource
- Configuring endpoints
- Running test query

## Using the Deployed Agent

### Via REST API (Streaming)

```bash
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json" \
     https://global-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/global/reasoningEngines/RESOURCE_ID:streamQuery?alt=sse \
     -d '{
       "class_method": "async_stream_query",
       "input": {
         "user_id": "user-123",
         "message": "Research coffee shop trends in Romania"
       }
     }'
```

### Via Python Client

```python
from vertexai import agent_engines
import vertexai

vertexai.init(project="your-project", location="global")

# Get deployed agent
remote_app = agent_engines.get("projects/.../reasoningEngines/...")

# Create session
session = remote_app.create_session(user_id="user-123")

# Stream query
for event in remote_app.stream_query(
    user_id="user-123",
    session_id=session["id"],
    message="Your query here"
):
    print(event)
```

## Monitoring

### View in Console

```
https://console.cloud.google.com/vertex-ai/reasoning-engines
```

### List Deployments

```bash
gcloud ai agent-engines list --location=global --project=PROJECT_ID
```

### View Logs

```bash
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit=50 --format=json
```

## Updating

To update the deployed agent:

```bash
# 1. Make code changes
# 2. Rebuild package
bash scripts/build_package.sh

# 3. Redeploy
python deploy.py
```

This creates a new version while keeping the same endpoint.

## Cost Optimization

Agent Engine pricing:

- **Storage**: GCS bucket costs (~$0.02/GB/month)
- **Compute**: Pay per request
- **Idle cost**: Minimal (no always-on instances)

Typical costs:

- ~1000 requests/day: $10-20/month
- ~10000 requests/day: $100-150/month

## Advantages vs Other Deployments

| Feature | Agent Engine | Cloud Run | GKE |
|---------|--------------|-----------|-----|
| **Setup** | Python script | Docker + scripts | Cluster + K8s |
| **Management** | Fully managed | Managed containers | Self-managed |
| **Scaling** | Automatic | Automatic | Manual/HPA |
| **Tracing** | Built-in | Manual | Manual |
| **Session Mgmt** | Built-in | Manual | Manual |
| **Streaming** | SSE built-in | Custom SSE | Custom SSE |

## Troubleshooting

### Package build fails

```bash
# Install build dependencies
pip install --upgrade build setuptools wheel
```

### Deployment fails

```bash
# Check permissions
gcloud projects get-iam-policy PROJECT_ID

# Verify APIs enabled
gcloud services enable aiplatform.googleapis.com
```

### Can't access endpoint

```bash
# Get authentication token
gcloud auth print-access-token

# Test with curl (add token to Authorization header)
```

## Security

- ✅ IAM-based authentication required
- ✅ Data encrypted in transit and at rest
- ✅ VPC-SC support available
- ✅ Audit logging enabled
- ✅ Private endpoint options

## Next Steps

1. Deploy agent
2. Test via API
3. Integrate with your application
4. Monitor usage and costs
5. Set up CI/CD pipeline

See [Vertex AI Agent Engine docs](https://cloud.google.com/vertex-ai/generative-ai/docs/reasoning-engine/overview) for more information.
