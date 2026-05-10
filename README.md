# Multi Tool Agent

This sample demonstrates a multi-tool agent built using the Agent Development Kit (ADK). The agent has access to a weather lookup tool and a calculator tool.

## Features

- **Weather Lookup**: Retrieves weather information for a given location.
- **Calculator**: Performs basic mathematical calculations.

## Prerequisites

Before you begin, make sure you have the following installed:
- **Python**: Version `>=3.11` (as required by `numpy` and other dependencies).
- **Git**: For checking out the codebase.
- **Google Cloud Storage Bucket**: A GCS bucket (e.g., `gs://my-agent-staging-bucket`) in your project to stage the packaged agent source code during deployment to Agent Runtime.

### Getting Started

Clone the repository to your local machine:
```bash
git clone https://github.com/csilvarivera/multi_tool_base_agent
cd multi_tool_base_agent
```

## Setup

1. **Create & Initialize Virtual Environment**:
   It is highly recommended to use [uv](https://github.com/astral-sh/uv) to manage your environment and dependencies:
   ```bash
   uv sync
   ```
   This will automatically create a virtual environment (`.venv`) and install all dependencies.

   Alternatively, you can use the standard `venv` module and `pip`:
   ```bash
   # Create the virtual environment
   python3 -m venv .venv

   # Activate the virtual environment
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env-example` to `.env` and configure the following variables:
   - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
   - `GOOGLE_CLOUD_LOCATION`: Your deployment region (e.g., `europe-west1`).
   - `GOOGLE_CLOUD_STORAGE_BUCKET`: Your GCS staging bucket URL (e.g., `gs://my-agent-staging-bucket`).
   - `CUSTOM_SERVICE_ACCOUNT`: Your custom service account email (e.g., `multi-tool-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`).

## Running the Agent

### Interactive Web UI (Recommended)
To run the agent locally using the ADK web playground interface:
```bash
uv run adk web .
```

## Deploying the Agent

Before deploying, ensure all Google Cloud API and IAM permission prerequisites are met. Review the [Deployment Requirements Guide](deployment_requirements.md) for the full specification.

To deploy the agent to Vertex AI Agent Runtime (from your virtual environment):
```bash
python -m deploy
```
