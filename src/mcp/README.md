# SmartRoute AI — IBM Bob MCP Server

This directory contains documentation for the SmartRoute AI MCP server that enables IBM Bob to interact with the supply chain assistant.

---

## What the MCP Server Does

The MCP server exposes SmartRoute AI capabilities as callable tools that IBM Bob can invoke during a conversation. Every tool calls the real project functions — there are no hardcoded or fake responses.

---

## Tools Exposed

| Tool | Required Input | What It Returns |
|---|---|---|
| `get_shipment_risk` | `shipment_id` | Risk score (0-100), classification (LOW/MEDIUM/HIGH/CRITICAL), explanation |
| `get_shipment_disruptions` | `shipment_id` | List of active disruptions affecting the shipment |
| `recommend_route` | `shipment_id` | Alternative route and carrier recommendations |
| `recommend_vehicle` | `shipment_id` | Best available vessel/vehicle recommendation |
| `get_fleet_status` | *(none)* | Fleet utilisation summary (total, available, idle, assigned) |
| `get_temperature_alerts` | `shipment_id` *(optional)* | Cold-chain temperature excursion alerts |
| `explain_shipment` | `shipment_id` | AI-generated plain-English explanation (watsonx.ai or mock) |

---

## Prerequisites

- Python 3.11+
- Install dependencies:

```bash
cd bob-ai-hackathon-PI-NANT/src
pip install -r requirements.txt
```

---

## Install MCP Dependency

```bash
pip install mcp
```

---

## Starting the MCP Server

```bash
cd bob-ai-hackathon-PI-NANT/src
python mcp_server.py
```

The server communicates over **stdio** (standard input/output) as required by the MCP protocol.

---

## Connecting IBM Bob

To connect IBM Bob to this MCP server, add the following to your Bob MCP configuration file (`.bob/mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "smartroute-ai": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "cwd": "/path/to/bob-ai-hackathon-PI-NANT"
    }
  }
}
```

Replace `/path/to/bob-ai-hackathon-PI-NANT` with the actual path on your machine.

---

## Environment Variables (for AI explanations)

The `explain_shipment` tool uses IBM watsonx.ai when credentials are set. Without credentials, it returns a clearly labelled mock response — the application still works.

| Variable | Required | Description |
|---|---|---|
| `WATSONX_API_KEY` | For real AI | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | For real AI | watsonx.ai project ID |
| `WATSONX_URL` | Optional | Defaults to `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_MODEL_ID` | Optional | Defaults to `ibm/granite-13b-instruct-v2` |

Set these in your shell or a `.env` file (never commit `.env`):

```bash
export WATSONX_API_KEY=your_api_key_here
export WATSONX_PROJECT_ID=your_project_id_here
```

---

## Example Tool Calls

### Get risk for SHP-001
```json
{ "tool": "get_shipment_risk", "arguments": { "shipment_id": "SHP-001" } }
```
**Returns:**
```json
{
  "shipment_id": "SHP-001",
  "score": 65,
  "classification": "HIGH",
  "explanation": "Risk score: 65/100 — HIGH\n\nContributing factors:..."
}
```

### Get fleet status
```json
{ "tool": "get_fleet_status", "arguments": {} }
```
**Returns:**
```json
{
  "total": 7,
  "available": 6,
  "unavailable": 1,
  "assigned": 4,
  "idle": 2,
  "utilisation_pct": 57.1
}
```

### Get temperature alerts for all shipments
```json
{ "tool": "get_temperature_alerts", "arguments": {} }
```

### Get temperature alerts for one shipment
```json
{ "tool": "get_temperature_alerts", "arguments": { "shipment_id": "SHP-002" } }
```

---

## Running Without IBM Bob (Testing)

You can test all tool functions directly in Python without the MCP SDK:

```python
import sys
sys.path.insert(0, 'src')
from mcp_server import call_tool

# Test any tool
result = call_tool("get_shipment_risk", {"shipment_id": "SHP-001"})
print(result)

result = call_tool("get_fleet_status", {})
print(result)
```

---

## Limitations

- The MCP server uses `stdio` transport (not HTTP). IBM Bob must support stdio MCP servers.
- Route recommendations use a static knowledge base, not live carrier APIs.
- Temperature data is from mock JSON files — not live IoT sensors.
- The `explain_shipment` tool falls back to mock text if watsonx.ai credentials are not configured.
