# Deployment Options

This directory contains all deployment configurations for the Factory Business AI Agent.

## Quick Start

Choose your deployment method:

| Type | Use Case | Command | Access |
|------|----------|---------|--------|
| **GKE External** | Production with public access | `cd gke-external && bash deploy.sh` | LoadBalancer IP |
| **GKE Internal** | Private VPC-only access | `cd gke-internal && bash deploy.sh` | Internal IP |
| **Cloud Run** | Serverless, auto-scaling | `cd cloud-run && bash deploy.sh` | HTTPS URL |
| **Local** | Development & testing | `cd local && bash start.sh` | localhost:8082 |

## Deployment Types

### 🌐 GKE External ([gke-external/](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/gke-external/))

**Best for:** Production deployments with public internet access

- ✅ Static external IP with LoadBalancer
- ✅ Full control over infrastructure
- ✅ Persistent pods
- ✅ VPC networking

**Quick Deploy:**

```bash
cd gke-external
bash deploy.sh
```

---

### 🔒 GKE Internal ([gke-internal/](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/gke-internal/))

**Best for:** Private deployments accessible only within VPC

- ✅ No external IP exposure
- ✅ VPC-native networking
- ✅ Internal load balancing
- ✅ Enhanced security

**Quick Deploy:**

```bash
cd gke-internal
bash deploy.sh
```

---

### ☁️ Cloud Run ([cloud-run/](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/cloud-run/))

**Best for:** Serverless, auto-scaling deployments

- ✅ Scale to zero (no cost when idle)
- ✅ Auto HTTPS with Google-managed SSL
- ✅ Automatic scaling
- ✅ Pay per use

**Quick Deploy:**

```bash
cd cloud-run
source config.env
bash scripts/deploy.sh
```

---

### 💻 Local Development ([local/](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/local/))

**Best for:** Local development and testing

- ✅ Quick setup
- ✅ Hot reload
- ✅ Easy debugging
- ✅ No GCP costs

**Quick Start:**

```bash
cd local
cp .env.example .env
# Edit .env with your API keys
bash start.sh
```

## Comparison Matrix

| Feature | GKE External | GKE Internal | Cloud Run | Local |
|---------|--------------|--------------|-----------|-------|
| **Cost** | Medium-High | Medium-High | Low (scale-to-zero) | Free |
| **Setup Time** | 5-10 min | 5-10 min | 2-3 min | 1 min |
| **Scalability** | Manual | Manual | Automatic | N/A |
| **Public Access** | ✅ Yes | ❌ No | ✅ Yes | ❌ No |
| **SSL/HTTPS** | Manual | Manual | Automatic | No |
| **Cold Starts** | No | No | Yes | No |
| **Min Cost** | ~$70/month | ~$70/month | $0 when idle | $0 |

## Prerequisites

### All Deployments

- Google Cloud Project
- gcloud CLI installed and configured
- Docker installed

### GKE Deployments

- GKE cluster created ([see cluster-setup](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/cluster-setup/))
- kubectl configured

### Cloud Run

- Cloud Run API enabled
- Artifact Registry or GCR configured

### Local

- Python 3.11+
- Virtual environment

## Environment Variables

All deployments require these environment variables:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_MAPS_API_KEY=your-maps-key
API_KEY_TARGETARE=your-targetare-key

# Optional but recommended
GOOGLE_CUSTOM_SEARCH_API_KEY=your-search-key
GOOGLE_CUSTOM_SEARCH_CX=your-search-engine-id
```

See each deployment folder's README for specific configuration details.

## Support

For deployment-specific help, see the README in each deployment folder:

- [gke-external/README.md](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/gke-external/README.md)
- [gke-internal/README.md](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/gke-internal/README.md)
- [cloud-run/README.md](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/cloud-run/README.md)
- [local/README.md](file:///Users/radanpetrica/PFA/agents/agents-adk-mcp/ai_agents/agent-factory-repo/factory_business_ai_agent_backend/agent-backend/deployments/local/README.md)
