# Multi Tool Agent

This sample demonstrates a multi-tool agent built using the Agent Development Kit (ADK). The agent has access to a weather lookup tool and a calculator tool.

## Features

- **Weather Lookup**: Retrieves weather information for a given location.
- **Calculator**: Performs basic mathematical calculations.

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
   Copy `.env-example` to `.env` and fill in your Google Cloud project details.

## Running the Agent

### Interactive Web UI (Recommended)
To run the agent locally using the ADK web playground interface:
```bash
uv run adk web .
```

## Deploying the Agent

To deploy the agent to Vertex AI Agent Runtime (from your virtual enviroment):
```bash
python -m deploy
```
