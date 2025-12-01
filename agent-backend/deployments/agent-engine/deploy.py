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

import sys
import os
import logging
try:
    import tomllib
except ImportError:
    # For Python < 3.11
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: 'tomli' is required for Python < 3.11. Please run: pip install tomli")
        sys.exit(1)

from dotenv import set_key, load_dotenv
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to sys.path to import the agent
# We are in agent-backend/deployments/agent-engine, so we need to go up 3 levels to reach agent-backend
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the agent after adding project root to path
try:
    from agent_factory_ai.agent import root_agent
except ImportError as e:
    logger.error(f"Failed to import agent: {e}")
    logger.error(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Load environment variables
# Try loading from config.env in current dir first, then .env in project root
current_dir = os.path.dirname(os.path.abspath(__file__))
config_env_path = os.path.join(current_dir, "config.env")
project_env_path = os.path.join(project_root, ".env")

load_dotenv(config_env_path)
load_dotenv(project_env_path)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

# Validate configuration
if not GOOGLE_CLOUD_PROJECT:
    logger.error("GOOGLE_CLOUD_PROJECT not set")
    sys.exit(1)

if not STAGING_BUCKET:
    logger.error("GOOGLE_CLOUD_STORAGE_BUCKET not set")
    sys.exit(1)

# Initialize Vertex AI
logger.info(f"Initializing Vertex AI with Project: {GOOGLE_CLOUD_PROJECT}, Location: {GOOGLE_CLOUD_LOCATION}, Bucket: {STAGING_BUCKET}")
vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=f"gs://{STAGING_BUCKET}",
)

def update_env_file(agent_engine_id, env_file_path):
    """Updates the .env file with the agent engine ID."""
    try:
        # Create file if it doesn't exist
        if not os.path.exists(env_file_path):
            with open(env_file_path, 'w') as f:
                f.write("")
        
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        logger.info(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
    except Exception as e:
        logger.error(f"Error updating .env file: {e}")

def load_requirements():
    """Loads requirements from pyproject.toml."""
    # pyproject.toml is in agent-backend/
    pyproject_path = os.path.join(project_root, "pyproject.toml")
    
    if not os.path.exists(pyproject_path):
        logger.warning(f"pyproject.toml not found at {pyproject_path}. Using default dependencies.")
        return [
            "google-cloud-aiplatform[reasoningengine,langchain]>=1.71.1",
            "fastapi>=0.115.6",
            "uvicorn>=0.34.0",
            "python-dotenv>=1.0.1",
            "pydantic>=2.10.5",
        ]

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        dependencies = pyproject_data.get("project", {}).get("dependencies", [])
        logger.info(f"Loaded {len(dependencies)} dependencies from pyproject.toml")
        return dependencies
    except Exception as e:
        logger.error(f"Error loading requirements from pyproject.toml: {e}")
        sys.exit(1)

# Check/Create GCS Bucket
def check_create_bucket():
    logger.info("Checking GCS bucket...")
    import subprocess

    try:
        # Check if bucket exists
        result = subprocess.run(
            ["gsutil", "ls", f"gs://{STAGING_BUCKET}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            # Bucket doesn't exist, create it
            logger.info(f"Creating bucket: gs://{STAGING_BUCKET}")
            create_result = subprocess.run(
                ["gsutil", "mb", "-l", GOOGLE_CLOUD_LOCATION, f"gs://{STAGING_BUCKET}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if create_result.returncode == 0:
                logger.info(f"✅ Bucket created: gs://{STAGING_BUCKET}")
            else:
                logger.error(f"❌ Error creating bucket: {create_result.stderr}")
                sys.exit(1)
        else:
            logger.info(f"✅ Bucket exists: gs://{STAGING_BUCKET}")
            
    except FileNotFoundError:
        logger.error("❌ Error: gsutil not found. Please install Google Cloud SDK")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error checking bucket: {e}")
        sys.exit(1)

def main():
    check_create_bucket()

    logger.info("Deploying app...")

    app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    logger.info("Deploying agent to Agent Engine...")
    
    # Path to the agent package directory (relative to where we run this script, or absolute)
    # We want to include the 'agent_factory_ai' directory which is in 'agent-backend'
    agent_package_path = os.path.join(project_root, "agent_factory_ai")

    if not os.path.exists(agent_package_path):
        logger.error(f"Agent package directory not found at: {agent_package_path}")
        sys.exit(1)

    try:
        remote_app = agent_engines.create(
            app,
            display_name="agent_factory_ai",
            requirements=load_requirements(),
            extra_packages=[
                agent_package_path, 
            ],
        )

        logger.info(f"✅ Deployed agent to Vertex AI Agent Engine successfully!")
        logger.info(f"📍 Resource Name: {remote_app.resource_name}")

        # Update the .env file with the new Agent Engine ID
        # We'll update the config.env in the current directory
        update_env_file(remote_app.resource_name, config_env_path)
        
        print("\n" + "=" * 70)
        print("DEPLOYMENT COMPLETE")
        print("=" * 70)
        print(f"Resource Name: {remote_app.resource_name}")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
