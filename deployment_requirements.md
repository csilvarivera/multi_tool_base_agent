# Deployment Requirements: IAM & APIs

This document outlines the Google Cloud APIs and IAM permissions required to deploy and run this ADK agent on **Vertex AI Agent Runtime (Reasoning Engine)** using a **custom service account**.

---

## 1. Required Google Cloud APIs

The following Google Cloud APIs must be enabled in the target Google Cloud project:

| API Name | Endpoint | Description |
|----------|----------|-------------|
| **Vertex AI API** | `aiplatform.googleapis.com` | Manages the Agent Runtime, Reasoning Engines, and Gemini model calls. |
| **Cloud Storage API** | `storage.googleapis.com` | Hosts the staging bucket used for packaging and uploading the agent's source code. |
| **Identity and Access Management (IAM) API** | `iam.googleapis.com` | Manages service accounts, key delegation, and role bindings. |
| **Cloud Logging API** | `logging.googleapis.com` | Records agent execution stdout/stderr logs and debug traces. |
| **Cloud Monitoring API** | `monitoring.googleapis.com` | Captures performance, telemetry, and model usage metrics. |
| **Cloud Trace API** | `cloudtrace.googleapis.com` | Records and visualizes latency and execution trace spans of agent operations. |

### Enabling APIs via CLI
Run the following command in your terminal to enable these APIs:
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudtrace.googleapis.com \
  --project=YOUR_PROJECT_ID
```

## 2. Fine-Grained Custom Service Account IAM Permissions (`app_sa`)

Under the hood, the predefined roles assigned to the custom service account (`multi-tool-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`) grant the following **fine-grained IAM permissions** in the project:

| Permission Category | Fine-Grained IAM Permission | Resource Scope | Purpose | Predefined Role Providing This |
|---------------------|-----------------------------|----------------|---------|--------------------------------|
| **Vertex AI Prediction** | `aiplatform.endpoints.predict` | Project Level | Allows the agent to call the Gemini API to generate content. | `roles/aiplatform.user` |
| **Vertex AI Sessions** | `aiplatform.sessions.create`<br>`aiplatform.sessions.get`<br>`aiplatform.sessions.list`<br>`aiplatform.sessionEvents.append`<br>`aiplatform.sessionEvents.list` | Project Level | Required by ADK to create, read, and append conversation history to native Reasoning Engine sessions. | `roles/aiplatform.user` |
| **Vertex AI Memories** | `aiplatform.memories.create`<br>`aiplatform.memories.get`<br>`aiplatform.memories.list`<br>`aiplatform.memories.update`<br>`aiplatform.memories.retrieve`<br>`aiplatform.memories.generate` | Project Level | Required if the agent uses Memory Bank (managed long-term memories) to recall facts across user sessions. | `roles/aiplatform.user` |
| **Cloud Storage** | `storage.objects.get` <br>`storage.objects.list` | GCS Staging Bucket | Enables the Reasoning Engine runtime to download the agent source code package. | `roles/storage.objectViewer` |
| **Cloud Logging** | `logging.logEntries.create` | Project Level | Streams agent stdout/stderr logs and tracebacks to Cloud Logging. | `roles/logging.logWriter` |
| **Cloud Monitoring** | `monitoring.timeSeries.create` | Project Level | Publishes performance and latency metrics to Cloud Monitoring. | `roles/monitoring.metricWriter` |
| **Cloud Trace** | `cloudtrace.traces.patch` | Project Level | Streams execution latency and trace spans (from OpenTelemetry) to Cloud Trace. | `roles/cloudtrace.agent` |

> [!TIP]
> If your agent requires retrieving API keys or credentials dynamically from GCP Secret Manager, you must also grant the following fine-grained permission:
> - **`secretmanager.versions.access`** (to access the secret value) — provided by `roles/secretmanager.secretAccessor`.

---

## 3. Creating the Custom Service Account & Assigning Granular Roles

Run the following `gcloud` commands in your terminal to create the custom service account, configure a custom granular role for model calls, and bind all granular roles one by one:

### Step 1: Create the Service Account
```bash
gcloud iam service-accounts create multi-tool-agent-sa \
  --description="Custom service account for running ADK multi-tool agent" \
  --display-name="Multi-Tool Agent SA" \
  --project=YOUR_PROJECT_ID
```

### Step 2: (Optional but Recommended) Create a Custom Granular Runner Role
Predefined role `roles/aiplatform.user` is very broad. To grant *only* the required model prediction, conversation session, and long-term memories permissions, create a custom granular role:
```bash
gcloud iam roles create multi_tool_agent_runner \
  --project=YOUR_PROJECT_ID \
  --title="ADK Multi-Tool Agent Runner" \
  --description="Granular prediction, session, and memory permissions for the ADK multi-tool agent" \
  --permissions="aiplatform.endpoints.predict,aiplatform.sessions.create,aiplatform.sessions.get,aiplatform.sessions.list,aiplatform.sessionEvents.append,aiplatform.sessionEvents.list,aiplatform.memories.create,aiplatform.memories.get,aiplatform.memories.list,aiplatform.memories.update,aiplatform.memories.retrieve,aiplatform.memories.generate" \
  --stage=GA
```

### Step 3: Bind the Granular Roles One by One
Bind the custom runner role (or predefined `roles/aiplatform.user` if custom roles are not desired) and standard granular predefined roles to the service account:
```bash
# Set the service account email for convenience
SA_EMAIL="multi-tool-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# 1. Grant Custom Runner Role (or fallback: roles/aiplatform.user)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="projects/YOUR_PROJECT_ID/roles/multi_tool_agent_runner"

# 2. Grant Storage Object Viewer (to download packaging source from staging bucket)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectViewer"

# 3. Grant Logs Writer (to write execution logs to Cloud Logging)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter"

# 4. Grant Monitoring Metric Writer (to capture telemetry metrics)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.metricWriter"

# 5. Grant Cloud Trace Agent (to capture latency and trace spans)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudtrace.agent"
```

---

## 4. Service Agent Delegation (CRITICAL)

The platform-managed **Vertex AI Service Agent** is responsible for orchestrating the deployment of Reasoning Engines. To allow it to deploy using your custom service account, it must be granted **Service Account User** (`roles/iam.serviceAccountUser`) on the custom service account.

### Step 1: (Optional) Verify or Create the Vertex AI Service Agent
> [!NOTE]
> **Why is it not showing in the GCP IAM Console?**
If the service agent does not exist or was never provisioned in your project yet, you can explicitly force its creation by running (see the [gcloud beta services identity create CLI Reference](https://cloud.google.com/sdk/gcloud/reference/beta/services/identity/create) for details):
```bash
gcloud beta services identity create \
  --service=aiplatform.googleapis.com \
  --project=YOUR_PROJECT_ID
```

### Step 2: Granting the Delegation Permission
Once the service agent exists, run the following command to allow it to act as your custom service account:
```bash
gcloud iam service-accounts add-iam-policy-binding \
  multi-tool-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.serviceAccountUser" \
  --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-aiplatform.iam.gserviceaccount.com" \
  --project=YOUR_PROJECT_ID
```

---

## 5. Deployment Identity Permissions

The identity running the `deploy.py` script (e.g., a developer's user account or a CI/CD runner service account) requires the following **precise granular IAM permissions** (which can be packaged into a custom role or mapped from predefined roles):

| Permission Category | Fine-Grained IAM Permission | Resource Scope | Purpose | Predefined Role Providing This |
|---------------------|-----------------------------|----------------|---------|--------------------------------|
| **Vertex AI Reasoning Engine** | `aiplatform.reasoningEngines.create` | Project Level | Creates/registers the new agent engine instance. | `roles/aiplatform.reasoningEngineAdmin` |
| **Vertex AI Reasoning Engine** | `aiplatform.reasoningEngines.update` | Project Level | Redeploys/updates the existing agent engine instance. | `roles/aiplatform.reasoningEngineAdmin` |
| **Vertex AI Reasoning Engine** | `aiplatform.reasoningEngines.get` | Project Level | Retrieves the deployed agent status to confirm success. | `roles/aiplatform.reasoningEngineAdmin` |
| **Vertex AI Reasoning Engine** | `aiplatform.reasoningEngines.list` | Project Level | Lists existing reasoning engines during resolution checks. | `roles/aiplatform.reasoningEngineAdmin` |
| **Vertex AI Operations** | `aiplatform.operations.get` | Project Level | Polls and tracks the status of the long-running deployment asynchronous operation. | `roles/aiplatform.reasoningEngineAdmin` |
| **Cloud Storage** | `storage.buckets.get`<br>`storage.objects.create`<br>`storage.objects.get` | GCS Staging Bucket | Verifies the bucket, uploads the source bundle, and confirms successful package upload. | `roles/storage.objectAdmin` |
| **Service Account** | `iam.serviceAccounts.actAs` | Custom Service Account | Enables the deployer to run the Reasoning Engine as the custom service account. | `roles/iam.serviceAccountUser` |

> [!IMPORTANT]
> **Security Best Practice for `iam.serviceAccounts.actAs`:**
> To prevent the deployer (developer or CI/CD identity) from being able to impersonate *any* service account in the project, do **not** grant `roles/iam.serviceAccountUser` at the project level. 
> Instead, grant it **exclusively on the custom service account resource itself** using the command below. This isolates the impersonation capability strictly to this specific service account:
>
> ```bash
> gcloud iam service-accounts add-iam-policy-binding \
>   multi-tool-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
>   --role="roles/iam.serviceAccountUser" \
>   --member="user:developer@example.com" \
>   --project=YOUR_PROJECT_ID
> ```


---

## 6. Gemini Enterprise Service Agent Setup (Cross-Project Registration)

If your deployed agent needs to be registered and managed under a **Gemini Enterprise app** located in a **different Google Cloud project** (cross-project setup), you must grant the Gemini Enterprise Service Agent access to the agent project hosting your Reasoning Engine.

### Step 1: Identify the Gemini Enterprise Service Agent
The Gemini Enterprise service agent is created in the project containing your **Gemini Enterprise app**. 

Construct the service agent's email address using this format:
```text
service-GEMINI_ENTERPRISE_PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com
```
*(Note: Replace `GEMINI_ENTERPRISE_PROJECT_NUMBER` with the project number of your Gemini Enterprise project).*

### Step 2: Grant Permissions in the Agent Project
Grant the Service Agent the **Discovery Engine Service Agent** role in the project where the ADK agent is hosted and deployed as described in https://docs.cloud.google.com/gemini/enterprise/docs/configure-cross-project-adk-agents or:
#### Equivalent CLI Command:
```bash
gcloud projects add-iam-policy-binding YOUR_AGENT_PROJECT_ID \
  --member="serviceAccount:service-GEMINI_ENTERPRISE_PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/discoveryengine.serviceAgent"
```

Once granted, the Gemini Enterprise app will have the necessary permissions to discover, list, and cross-communicate with your deployed ADK reasoning engine.


