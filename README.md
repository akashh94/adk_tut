# hello-adk-agent

A minimal Google ADK agent that says hello and tells the time, using
**Vertex AI** as the model backend — meaning requests are billed to your
Google Cloud project (your Cloud credits/billing account), authenticated
via the `gcloud` ADC credentials you've already set up. No API key needed.

## Folder structure

```
hello-adk-agent/
├── requirements.txt
├── .env.example
└── hello_agent/              # the ADK agent package
    ├── __init__.py           # required by ADK: exposes the agent module
    ├── agent.py               # assembles root_agent from settings + tools
    ├── config.py              # loads/validates settings from env vars
    ├── .env                   # you create this (copy from .env.example)
    └── tools/
        ├── __init__.py
        └── greeting_tools.py   # get_greeting(), get_current_time()
```

This matches the layout ADK's CLI expects (`adk run`, `adk web`,
`adk api_server` look for a package with `__init__.py` + `agent.py`
exporting a `root_agent`).

## How SOLID maps onto this structure

- **S — Single Responsibility**: `config.py` only knows how to source and
  validate settings. `tools/greeting_tools.py` only contains tool logic.
  `agent.py` only wires things together. Nothing else touches `os.environ`.
- **O — Open/Closed**: new capabilities are added as new functions in
  `tools/` (or new files in that package) without touching `agent.py` or
  existing tools.
- **L — Liskov Substitution**: every tool is just a plain Python callable
  with type hints — any function matching that shape can be swapped in
  for another without breaking the agent.
- **I — Interface Segregation**: tools take only the parameters they
  need (`get_greeting(name)`, `get_current_time()`) rather than one
  do-everything function with a bag of optional args.
- **D — Dependency Inversion**: `build_agent(settings)` in `agent.py`
  depends on the `AgentSettings` abstraction, not on *how* settings are
  loaded. You could pass it hand-built settings in a unit test with zero
  changes to `agent.py`.

## Setup

1. **Install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate         # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Confirm gcloud auth + project** (you said you've already done this,
   but worth double-checking):

   ```bash
   gcloud auth application-default login   # only if not already done
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable aiplatform.googleapis.com
   ```

   `aiplatform.googleapis.com` is the Vertex AI API — it must be enabled
   on the project for Gemini calls to be billed to it.

3. **Create the env file**

   ```bash
   cp .env.example hello_agent/.env
   ```

   Edit `hello_agent/.env` and set `GOOGLE_CLOUD_PROJECT` to your project
   id (or run `gcloud config get-value project` to see it).

## Run it

From the **parent** directory (`hello-adk-agent/`, the one containing the
`hello_agent/` folder):

```bash
# Interactive terminal chat
adk run hello_agent

# Or a local web UI for testing/debugging
adk web
```

Try saying "Hi, I'm Alex" or "what time is it?" and the agent will use its
tools to respond.

## Notes

- Because `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, the ADK's underlying
  `google-genai` client routes calls through Vertex AI and authenticates
  with your local ADC credentials (`~/.config/gcloud/application_default_credentials.json`)
  — that's the file `gcloud auth application-default login` created. Usage
  is billed to `GOOGLE_CLOUD_PROJECT`.
- If you'd rather use a free Google AI Studio API key instead of Cloud
  billing, set `GOOGLE_GENAI_USE_VERTEXAI=FALSE` and add
  `GOOGLE_API_KEY=...` to the `.env` file.
