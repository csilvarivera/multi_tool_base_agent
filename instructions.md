# ADK Multi-Tool Agent training — attendee prerequisites

Welcome! Before the session, please spend ~15 minutes getting your laptop ready so we can start coding straight away. If anything below doesn't work, ping the trainer in the chat — we'd rather sort it now than during the workshop.

We'll be working through the [csilvarivera/multi_tool_base_agent](https://github.com/csilvarivera/multi_tool_base_agent) repo, deploying to a shared GCP sandbox project (`ai-apps-sandbox`, region `europe-west1`).

---

## 0. Trainer-supplied details

Your trainer will share these out of band — please have them to hand before you start:

| Item | Value |
|---|---|
| Workforce login config file | `<TRAINER_TO_FILL: link or attachment for workforce-login-config.json>` |
| Workforce pool provider ID | `<TRAINER_TO_FILL: e.g. azure-oidc-corp>` |
| Azure AD group you should already be in | `<TRAINER_TO_FILL: e.g. AI-GCP-Training>` |

Everything else (project, bucket, service account, IAM bindings) is already provisioned for you in `ai-apps-sandbox` — you don't need to run any setup scripts.

---

## 1. Install local tools

You need these on your machine (any OS — macOS, Linux, or Windows/WSL2 all fine):

- **Python 3.11 or newer** — `python3 --version` to check.
- **Git** — `git --version`.
- **Google Cloud CLI (`gcloud`)** — install from <https://cloud.google.com/sdk/docs/install>. After installing, run `gcloud version` and confirm it's **≥ 480.0.0** so it has full workforce-pool support.
- **`uv`** (recommended) — fast Python package manager used by the training repo. Install with:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  (Plain `pip` + `venv` also works if you'd rather — instructions are in the repo's README.)

---

## 2. Sign in to GCP via the corporate (Azure) workforce identity

You won't use a personal `@gmail.com` or `@playtech.com` Google account for this — instead you'll authenticate through the same Azure AD login you already use, via a **workforce identity pool**.

You'll do this in **two** steps. The first signs in the `gcloud` CLI itself; the second sets up *Application Default Credentials* (ADC), which is what the Python ADK actually reads at runtime. Both use the same login-config file from the trainer.

```bash
# Save the file the trainer shared (e.g. to your home directory)
# so the path below resolves on your machine.
LOGIN_CONFIG="$HOME/workforce-login-config.json"

# 1. gcloud CLI session — opens a browser, redirects through Azure
gcloud auth login --login-config="$LOGIN_CONFIG"

# 2. Application Default Credentials — opens a second browser flow
gcloud auth application-default login --login-config="$LOGIN_CONFIG"

# 3. Tell ADC which project to bill API calls against (workforce identities
#    don't have a default home project, so this is required, not optional)
gcloud auth application-default set-quota-project ai-apps-sandbox

# 4. Set the active project for the gcloud CLI
gcloud config set project ai-apps-sandbox
```

> **Heads-up:** when the browser pops up you should see your Azure / Microsoft sign-in page, **not** a Google account chooser. If you see "Choose an account" with `@gmail.com` accounts, the login config wasn't picked up — check the `--login-config` path and try again.

---

## 3. Verify auth works

Quick sanity check that you're signed in *and* that Vertex AI is reachable from your laptop:

```bash
# Should show your federated workforce identity, not a Google email
gcloud auth list

# Should print "ai-apps-sandbox"
gcloud config get-value project

# Should return a JSON blob of available foundation models without errors
gcloud ai models list --region=europe-west1 --project=ai-apps-sandbox
```

If the `models list` call returns a `403` or `PERMISSION_DENIED`, stop and message the trainer with the exact error — most likely your Azure AD group membership hasn't propagated yet.

---

## 4. Clone the repo and configure environment

```bash
git clone https://github.com/csilvarivera/multi_tool_base_agent
cd multi_tool_base_agent
cp .env-example .env
```

Open `.env` in your editor and set the following values exactly:

```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=ai-apps-sandbox
GOOGLE_CLOUD_LOCATION=europe-west1
GOOGLE_CLOUD_STORAGE_BUCKET=gs://ai-apps-sandbox-adk-agent-staging
CUSTOM_SERVICE_ACCOUNT=multi-tool-agent-sa@ai-apps-sandbox.iam.gserviceaccount.com
```

Then install the project's dependencies:

```bash
uv sync
```

(Or, with plain Python: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.)

---

## 5. Smoke-test the agent locally

This is the final check that everything is wired up. It launches the ADK web playground on your laptop, talking to Vertex AI in `ai-apps-sandbox`:

```bash
uv run adk web .
```

Open the URL it prints (usually <http://localhost:8000>), pick the multi-tool agent, and ask it something like *"What's the weather in London? Then add 12 and 30 for me."* If you get a sensible reply, you're done — see you at the session.

---

## Troubleshooting cheat sheet

| Symptom | Likely cause | Fix |
|---|---|---|
| Browser shows Google account chooser instead of Azure sign-in | `--login-config` flag missing or pointed at wrong file | Re-run with the correct `--login-config="$LOGIN_CONFIG"` |
| `Reauthentication required` loop | gcloud cached an old non-workforce session | `gcloud auth revoke --all`, then redo step 2 |
| `quota_project` / `billing project` errors from Vertex AI | Forgot the `set-quota-project` step | Run `gcloud auth application-default set-quota-project ai-apps-sandbox` |
| `403 PERMISSION_DENIED` calling `aiplatform.googleapis.com` | Not yet a member of the training Azure AD group, or membership hasn't propagated | Confirm group membership with the trainer; sign out and back in |
| `gcloud: unrecognized argument: --login-config` | gcloud CLI is too old | Upgrade with `gcloud components update` (or reinstall from the link in §1) |
| Behind the corporate VPN, browser auth hangs | Proxy intercepts the OIDC redirect | Disconnect from Playtech VPN for the **login** step only, then reconnect |

---

## What you'll have at the end

- A `gcloud` CLI session and ADC credentials on your laptop, both as your **federated Azure identity**, scoped to `ai-apps-sandbox`.
- A clone of the training repo with a `.env` pointing at the shared sandbox.
- A working local ADK web playground talking to Vertex AI.

That's everything. Looking forward to the session!