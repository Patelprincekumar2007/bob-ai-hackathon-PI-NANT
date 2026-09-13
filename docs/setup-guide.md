# Setup Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | 3.12 and 3.13 also supported |
| pip | Any recent | Included with Python |
| Git | Any | For cloning the repository |
| IBM watsonx.ai account | Optional | Only needed for real AI explanations; app runs in Demo Mode without it |

## 1. Clone the Repository

```bash
git clone <repo-url>
cd bob-ai-hackathon-PI-NANT
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r src/requirements.txt
```

This installs:
- `streamlit>=1.35.0` — dashboard
- `pandas>=2.2.0` — data tables
- `python-dotenv==1.0.1` — environment variable loading
- `pytest>=8.0.0` — test runner

## 4. Environment Variables

All environment variables are **optional**. The application runs fully in Demo Mode without any configuration.

Copy the example file and edit it:

```bash
cp src/.env.example src/.env
# Then open src/.env in a text editor
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `WATSONX_API_KEY` | No | — | IBM Cloud API key for watsonx.ai |
| `WATSONX_PROJECT_ID` | No | — | watsonx.ai project ID |
| `WATSONX_URL` | No | `https://us-south.ml.cloud.ibm.com` | watsonx.ai inference endpoint |
| `WATSONX_MODEL_ID` | No | `ibm/granite-13b-instruct-v2` | Model to use for AI explanations |
| `STREAMLIT_SERVER_PORT` | No | `8501` | Port for the Streamlit server |
| `STREAMLIT_SERVER_HEADLESS` | No | `false` | Set to `true` to suppress browser auto-open |

When `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are not set, the app shows `[Demo Mode - Mock AI]` labels and returns pre-defined example responses.

## 5. Run the Tests

From the `bob-ai-hackathon-PI-NANT/src` directory:

```bash
cd bob-ai-hackathon-PI-NANT/src
python -m pytest ../tests/ -v
```

Or run individual test files:

```bash
python -m pytest ../tests/test_part1.py -v    # 49 tests — core modules
python -m pytest ../tests/test_part2.py -v    # 78 tests — fleet + cold chain
python -m pytest ../tests/test_part3.py -v    # Part 3 dashboard tests
```

Expected output: all tests pass with no errors.

## 6. Run the Application

From the **repository root** (`bob-ai-hackathon-PI-NANT`):

```bash
streamlit run src/app.py
```

The app opens automatically at **http://localhost:8501**.

If port 8501 is already in use, specify a different port:

```bash
streamlit run src/app.py --server.port 8502
```

## 7. Verify It Is Working

After the app opens:

1. **Dashboard page** should show KPI metrics (Total Shipments, At-Risk, etc.)
2. **Shipments page** should show a table of shipments with risk scores
3. **Disruptions page** should show active disruptions
4. **Fleet page** should show vehicle utilisation data
5. **Cold Chain page** should show temperature alerts

In the sidebar footer you should see either:
- `AI: watsonx.ai connected` — if credentials are configured
- `AI: Demo Mode (Mock AI)` — if no credentials (normal for local demo)

## 8. Run the MCP Server (for IBM Bob integration)

```bash
# Install the mcp package first
pip install mcp>=1.0.0

# Start the MCP server
cd bob-ai-hackathon-PI-NANT/src
python mcp_server.py
```

Register it in your IBM Bob MCP configuration as a stdio server.

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `Python 3.10 not supported` or import errors | Wrong Python version | Install Python 3.11+ and recreate the venv |
| `ModuleNotFoundError: No module named 'streamlit'` | Dependencies not installed | Run `pip install -r src/requirements.txt` |
| `Port 8501 is already in use` | Another Streamlit or process on 8501 | Use `--server.port 8502` or kill the other process |
| `ModuleNotFoundError: No module named 'core'` | Running from wrong directory | Run `streamlit run src/app.py` from the repo root |
| `No temperature data found for shipment X` | Shipment does not require cold chain | Normal behaviour — only cold-chain shipments have temperature data |
| watsonx API call fails | Wrong credentials or network | Check `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`; app will fall back to Demo Mode |
| `mcp` package not found | MCP not installed | Run `pip install mcp>=1.0.0` (only needed for MCP server) |
