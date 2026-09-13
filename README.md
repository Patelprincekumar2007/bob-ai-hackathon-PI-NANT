# SmartRoute AI

> AI-powered supply chain control tower — disruption detection, risk scoring, and route recommendations.

---

## Team

| Field | Value |
|---|---|
| **Team Name** | PI-NANT |
| **Track** | AI |
| **Team Lead** | Kashyap Nasit — 24cs109@charusat.edu.in |
| **Members** | Kashyap Nasit, Patel Princekumar, Patel Rudrakumar |

---

## Problem Statement

Supply chain operators managing global shipments face severe, costly disruptions — port congestion, extreme weather, strikes, and vessel failures — causing delays, cargo loss, and fleet under-utilisation. Manual rerouting across carrier portals takes hours and often occurs too late to prevent damage, especially for temperature-sensitive pharmaceutical and perishable cargo.

---

## Solution

SmartRoute AI is an AI-powered supply chain control tower that automatically detects active disruptions, scores every shipment's risk 0-100, and recommends alternative routes and carriers in real time. It monitors cold-chain temperature excursions, optimises fleet utilisation, and uses IBM watsonx.ai (via an IBM Bob MCP server) to generate plain-English explanations and escalation advice for logistics coordinators.

---

## Key Features

- **Real-time shipment risk scoring (0-100)** with CRITICAL/HIGH/MEDIUM/LOW classification
- **Automated disruption detection** across port, weather, strike, and vessel events
- **Alternative route and carrier recommendations** with delay and cost estimates
- **Cold-chain temperature monitoring** with excursion alerts and risk scoring
- **IBM Bob MCP integration** with 7 tools for natural-language supply chain queries

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | Streamlit |
| **IBM Technologies** | watsonx.ai, IBM Bob, IBM Bob MCP Server |
| **Databases** | None — JSON mock data |
| **Other** | python-dotenv, pytest, GitHub Actions |

---

## Repository Structure

```
├── src/                  # All source code
│   ├── app.py            # Streamlit dashboard (Part 3)
│   ├── mcp_server.py     # IBM Bob MCP server (Part 2)
│   ├── core/             # Core logic modules
│   │   ├── disruption_detector.py
│   │   ├── risk_engine.py
│   │   ├── route_advisor.py
│   │   ├── fleet_optimizer.py
│   │   ├── cold_chain_monitor.py
│   │   └── watsonx_client.py
│   ├── data/             # JSON mock data files
│   └── requirements.txt
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt
├── tests/                # Pytest test suite (127+ tests)
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## How to Run

```bash
# 1. Clone the repo
git clone <repo-url>
cd bob-ai-hackathon-PI-NANT

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. (Optional) Configure watsonx.ai credentials
cp src/.env.example src/.env
# Edit src/.env — leave blank to run in Demo Mode

# 5. Run the Streamlit dashboard
streamlit run src/app.py
```

The app opens at **http://localhost:8501** — no credentials needed for Demo Mode.

---

## Demo

| Artifact | Link |
|---|---|
| Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| Screenshots | [See demo/screenshots/](demo/screenshots/) |
| Presentation | [See presentation/](presentation/) |

---

## Known Limitations

- Route recommendations use a curated static knowledge base, not live carrier APIs
- watsonx.ai explanations fall back to mock text when credentials are not configured
- Temperature data is from mock IoT sensor readings, not live sensors
- No authentication or user management (demo only)

---

## What We're Most Proud Of

The end-to-end operator workflow from disruption detection to AI-powered recommendation, and the IBM Bob MCP integration that lets a logistics coordinator query the entire supply chain system in natural language.
