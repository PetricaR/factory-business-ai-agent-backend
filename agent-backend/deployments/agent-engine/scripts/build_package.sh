#!/bin/bash
# Build Python package for Agent Engine deployment

set -e

echo "========================================="
echo "Building Agent Package"
echo "========================================="

# Navigate to agent-backend directory
cd ../../..

# Configuration
PACKAGE_NAME="agent_factory_ai"
VERSION="0.1.0"
OUTPUT_DIR="deployments/agent-engine"

echo "Package: ${PACKAGE_NAME}"
echo "Version: ${VERSION}"
echo "Output:  ${OUTPUT_DIR}"
echo ""

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "⚠️  Creating pyproject.toml..."
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agent_factory_ai"
version = "0.1.0"
description = "Factory Business AI Agent"
requires-python = ">=3.11"
dependencies = [
    "google-cloud-aiplatform[reasoningengine,langchain]>=1.71.1",
    "fastapi>=0.115.6",
    "uvicorn>=0.34.0",
    "python-dotenv>=1.0.1",
    "pydantic>=2.10.5",
]

[project.optional-dependencies]
dev = ["pytest", "black", "ruff"]
EOF
fi

# Install build tools
echo "📦 Installing build tools..."
# python -m pip install -q --upgrade build wheel setuptools

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Build wheel package
echo "🔨 Building wheel package..."
python -m build --wheel

# Find the built wheel
WHEEL_FILE=$(ls dist/*.whl | head -n 1)

if [ -z "$WHEEL_FILE" ]; then
    echo "❌ Error: No wheel file found"
    exit 1
fi

# Copy to deployment directory
echo "📋 Copying to deployment directory..."
cp "$WHEEL_FILE" "${OUTPUT_DIR}/"

FINAL_WHEEL="${OUTPUT_DIR}/$(basename $WHEEL_FILE)"

echo ""
echo "========================================="
echo "✅ Build Complete!"
echo "========================================="
echo "Wheel file: ${FINAL_WHEEL}"
echo ""
echo "Next step:"
echo "  cd deployments/agent-engine"
echo "  python deploy.py"
echo "========================================="
