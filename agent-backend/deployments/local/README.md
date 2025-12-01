# Local Development Setup

Run the Factory Business AI Agent locally for development and testing.

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your API keys
nano .env

# 3. Start the agent
bash start.sh
```

The agent will be available at: <http://localhost:8082>

## Prerequisites

- Python 3.11+
- pip or uv
- API keys configured

## Environment Variables

Create `.env` file with:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_MAPS_API_KEY=your-maps-key
API_KEY_TARGETARE=your-targetare-key

# Optional
GOOGLE_CUSTOM_SEARCH_API_KEY=your-search-key
GOOGLE_CUSTOM_SEARCH_CX=your-cx-id

# Model Configuration
MODEL=gemini-2.0-flash-exp
GOOGLE_CLOUD_LOCATION=global

# MCP Server (if running separately)
MCP_SERVER_URL=http://localhost:8000/mcp
```

## Running with Docker

```bash
# Build
docker build -t agent-factory-ai:local ../..

# Run
docker run -p 8082:8080 \\
  --env-file .env \\
  agent-factory-ai:local
```

## Running with Python

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r ../../requirements.txt

# Run
cd ../..
python main.py
```

## Testing

```bash
# Health check
curl http://localhost:8082/health

# Test query
curl -X POST http://localhost:8082/stream-query \\
  -H "Content-Type: application/json" \\
  -d '{"user_id": "test", "message": "Hello"}'

# API docs
open http://localhost:8082/docs
```

## Development Workflow

1. **Make code changes** in `agent_factory_ai/`
2. **Restart** with `bash start.sh`
3. **Test** locally
4. **Deploy** when ready

## Hot Reload

For development with auto-reload:

```bash
cd ../..
uvicorn main:app --reload --port 8082
```

## Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with VS Code debugger
# Add to launch.json:
{
  "name": "Python: FastAPI",
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["main:app", "--reload"],
  "cwd": "${workspaceFolder}/agent-backend"
}
```

## Common Issues

### Port already in use

```bash
# Kill process on port 8082
lsof -ti:8082 | xargs kill -9
```

### Missing dependencies

```bash
pip install --upgrade -r requirements.txt
```

### MCP connection issues

```bash
# Start MCP server first (if needed)
cd ../../map-mcp
python -m fastmcp run server.py
```
