#!/bin/bash
# Local Development Startup Script

set -e

echo "🚀 Starting Factory Business AI Agent (Local Development)"
echo "=========================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create .env file:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Add your API keys"
    exit 1
fi

# Load environment
echo "📄 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✅ Python $(python3 --version)"

# Navigate to agent-backend
cd ../..

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Recommended: python -m venv venv && source venv/bin/activate"
fi

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Ready!"
echo "📍 Starting agent at http://localhost:8082"
echo "📚 API Docs: http://localhost:8082/docs"
echo "❤️  Health: http://localhost:8082/health"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================================="
echo ""

# Start the agent
python main.py
