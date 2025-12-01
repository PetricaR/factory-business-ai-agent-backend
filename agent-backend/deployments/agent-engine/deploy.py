# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Deploy Factory Business AI Agent to Vertex AI Agent Engine (Reasoning Engine)
"""

import vertexai
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path to import agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agent_factory_ai.agent import root_agent

load_dotenv()

# Configuration
cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
agent_package = os.getenv("AGENT_PACKAGE", "./agent_factory_ai-0.1.0-py3-none-any.whl")

print("=" * 70)
print("VERTEX AI AGENT ENGINE DEPLOYMENT")
print("=" * 70)
print(f"Project:        {cloud_project}")
print(f"Location:       {cloud_location}")
print(f"Storage Bucket: {storage_bucket}")
print(f"Agent Package:  {agent_package}")
print("=" * 70)

# Validate configuration
if not cloud_project:
    print("❌ Error: GOOGLE_CLOUD_PROJECT not set")
    sys.exit(1)

if not storage_bucket:
    print("❌ Error: GOOGLE_CLOUD_STORAGE_BUCKET not set")
    sys.exit(1)

if not os.path.exists(agent_package):
    print(f"❌ Error: Agent package not found: {agent_package}")
    print("   Run: bash scripts/build_package.sh")
    sys.exit(1)

# Initialize Vertex AI
print("\n📦 Initializing Vertex AI...")
vertexai.init(
    project=cloud_project,
    location=cloud_location,
    staging_bucket=f"gs://{storage_bucket}",
)
print("✅ Vertex AI initialized")

# Create AdkApp wrapper
print("\n🔧 Creating AdkApp wrapper...")
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
print("✅ AdkApp created")

# Deploy to Agent Engine
print("\n🚀 Deploying to Agent Engine...")
print("   This may take several minutes...")

try:
    remote_app = agent_engines.create(
        app,
        requirements=[
            agent_package,
        ],
        extra_packages=[
            agent_package,
        ],
    )
    print("✅ Deployment successful!")
    
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    sys.exit(1)

print("=" * 70)
print("DEPLOYMENT COMPLETE")
print("=" * 70)

# Get resource name
resource_name = remote_app.resource_name
print(f"\n📍 Resource Name: {resource_name}")

# Test deployment
print("\n🧪 Testing deployment...")
try:
    session = remote_app.create_session(user_id="test-user")
    print(f"✅ Session created: {session['id']}")
    
    print("\n💬 Testing query (streaming)...")
    for event in remote_app.stream_query(
        user_id="test-user",
        session_id=session["id"],
        message="Hello! Quick test.",
    ):
        print(f"   Event: {event}")
    
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"⚠️  Test failed: {e}")
    print("   Deployment succeeded but testing failed. Check configuration.")

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("\n1. Test via API:")
print(f"   curl -H 'Authorization: Bearer $(gcloud auth print-access-token)' \\")
print(f"        -H 'Content-Type: application/json' \\")
print(f"        https://{cloud_location}-aiplatform.googleapis.com/v1/{resource_name}:streamQuery?alt=sse \\")
print(f"        -d '{{\"class_method\": \"async_stream_query\", \"input\": {{\"user_id\": \"test\", \"message\": \"Hello\"}}}}'")
print("\n2. View in Console:")
print(f"   https://console.cloud.google.com/vertex-ai/reasoning-engines?project={cloud_project}")
print("\n3. Monitor:")
print(f"   gcloud ai agent-engines list --location={cloud_location} --project={cloud_project}")
print("\n" + "=" * 70)
