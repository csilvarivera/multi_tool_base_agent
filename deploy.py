"""Deployment script for MRNA."""

import os
import sys

# Now use an absolute import from the project root
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
from multi_tool_base_agent.agent import root_agent


# load the environment
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
CUSTOM_SERVICE_ACCOUNT = os.getenv("CUSTOM_SERVICE_ACCOUNT","")


print("Project ID:", PROJECT_ID)
print("Location:", LOCATION)
print("Staging bucket:", GOOGLE_CLOUD_STORAGE_BUCKET)
print("Custom service account:", CUSTOM_SERVICE_ACCOUNT)
if not PROJECT_ID or not LOCATION or not GOOGLE_CLOUD_STORAGE_BUCKET:
  print(
      "Missing GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, or STAGING_BUCKET",
      file=sys.stderr,
  )
  sys.exit(1)

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=GOOGLE_CLOUD_STORAGE_BUCKET,
)

def deploy_agent():
  # Deploy to AgentEngine - Check Cloud Logging for detailed issues.
  remote_agent = agent_engines.create(
      root_agent,
          requirements=[
        "google-cloud-aiplatform[adk,agent-engines]",
        "google-adk(>=1.23.0, <1.32.0)",
        "python-dotenv",
        "pydantic>=2.11.3",
        "numpy>=2.3.1",
        "opentelemetry-sdk>=1.36.0",
        "opentelemetry-exporter-otlp-proto-http>=1.36.0",
      ],
      extra_packages=["multi_tool_base_agent/agent.py",
      "multi_tool_base_agent/tools.py"],
      display_name="multi_tool_base_agent_v2",
      service_account=f"{CUSTOM_SERVICE_ACCOUNT}",
      env_vars = {
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
      }

    
  )
  print(f"\nSuccessfully created agent: {remote_agent.resource_name}")

def call_agent():
  # Change to your agent engine ID
  AGENT_ENGINE_ID=""
  agent = agent_engines.get(AGENT_ENGINE_ID)

  remote_session = agent.create_session(user_id="u_123")
  print (f" calling agent {AGENT_ENGINE_ID} with session {remote_session['id']}")
  for event in agent.stream_query(
    user_id="u_123",
    session_id=remote_session['id'],
    # session_id="5286711940846977024",
    message="Hello how can you help",
  ):
    print(event)


if __name__ == "__main__":
    try:
        # Call the deployment function with the obtained values
        deploy_agent()
        print("\nDeployment script finished.")
        #call_agent()
        
    except (ValueError, FileNotFoundError) as e: # Catch specific known errors
         print(f"Configuration Error: {e}", file=sys.stderr)
         sys.exit(1)
    except Exception as e: # Catch any other unexpected errors during the process
        print(f"Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)

