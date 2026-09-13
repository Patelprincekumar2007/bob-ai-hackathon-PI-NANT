# Solution Overview

## What We Built

SmartRoute AI is a five-module Python application with a Streamlit dashboard and an IBM Bob MCP server. It ingests supply chain data (shipments, disruptions, vehicles, temperature readings), scores every shipment's risk deterministically, detects which disruptions affect which shipments, and surfaces actionable recommendations — all without requiring an external API or database.

The system is designed as a **control tower**: a single screen where a logistics coordinator can see the entire fleet at a glance, drill into any shipment, and get a plain-English AI explanation of what is happening and what to do.

## How It Works

The data flow from disruption to recommendation follows these steps:

1. **Disruption detected** — The `disruption_detector` module loads the disruptions JSON and matches each active disruption to affected shipments using five rules: explicit link, route match, carrier match, port match, and vessel match.

2. **Risk scored** — The `risk_engine` module calculates a 0-100 risk score for each shipment using five weighted factors: disruption severity (35 pts), current delay (25 pts), deadline pressure (20 pts), shipment priority (15 pts), and cold-chain excursion (5 pts). Scores are classified as CRITICAL (75+), HIGH (50+), MEDIUM (25+), or LOW.

3. **Alternatives generated** — The `route_advisor` module looks up the shipment's route in a knowledge base of pre-defined alternative routes, filters by cargo type compatibility and which disruptions the alternative avoids, then enriches each option with available vehicle data.

4. **Fleet checked** — The `fleet_optimizer` module identifies available vehicles that match the shipment's cargo type, cold-chain requirements, weight, and TEU needs. It ranks candidates and returns the best match with up to three alternatives.

5. **Cold chain verified** — The `cold_chain_monitor` module analyses temperature readings for cold-chain shipments, counts excursions, calculates deviation from safe range, and classifies severity as NORMAL, WARNING, or CRITICAL.

6. **AI explanation generated** — The `watsonx_client` module sends a structured prompt to IBM watsonx.ai (Granite 13B) and returns a plain-English explanation and recommended action. When credentials are absent, a clearly labelled mock response is returned so the demo always runs.

7. **Dashboard displayed** — The Streamlit dashboard assembles all of the above data in five pages: Dashboard, Shipments, Disruptions, Fleet, and Cold Chain. Each page uses `st.metric` for KPI cards and colour-coded badges for risk levels.

## Architecture Summary

The application has three layers:

- **Data layer** — Four JSON files in `src/data/` (shipments, disruptions, vehicles, temperature_readings). No database required.
- **Logic layer** — Five Python modules in `src/core/` (disruption_detector, risk_engine, route_advisor, fleet_optimizer, cold_chain_monitor) plus `watsonx_client`.
- **Interface layer** — `src/app.py` (Streamlit dashboard) and `src/mcp_server.py` (IBM Bob MCP server with 7 tools).

See [`architecture.md`](architecture.md) for the full component diagram and data flow.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Python + Streamlit** | Zero-friction setup for a hackathon demo — no frontend build step, no JavaScript, runs in a single `pip install + streamlit run`. |
| **JSON mock data** | Judges can run the project instantly without a database, credentials, or seeding script. Real data can replace the JSON files without any code change. |
| **Deterministic risk scoring** | Reproducible, explainable scores that pass automated tests — no ML model to train or deploy. |
| **IBM Bob MCP server** | Exposes all seven supply chain tools as MCP tools so IBM Bob can answer natural-language questions by calling the same logic the dashboard uses. |
| **Mock AI fallback** | When `WATSONX_API_KEY` is not set, `watsonx_client` returns a labelled mock response. The dashboard clearly shows `[Demo Mode - Mock AI]` so judges know the status without configuration failing. |
| **`@st.cache_data`** | Expensive data loads (scoring all shipments, loading all disruptions) are cached in the Streamlit session to keep the demo snappy on repeated navigation. |

## IBM Technologies Used

### IBM watsonx.ai

The `watsonx_client` module uses the `ibm-watsonx-ai` SDK to call the Granite 13B Instruct model. It constructs a supply chain-specific prompt that includes the shipment ID, risk score, classification, and active disruption titles, then asks the model to explain the situation and recommend next steps in plain English. The output is displayed in the Streamlit dashboard under each shipment's detail view with a clear `[AI - watsonx]` label.

### IBM Bob MCP Server

`src/mcp_server.py` implements seven MCP tools that IBM Bob can call:

| Tool | What it does |
|---|---|
| `get_shipment_risk` | Returns the risk score and classification for one shipment |
| `get_shipment_disruptions` | Lists active disruptions affecting a shipment |
| `recommend_alternative_routes` | Returns alternative route options for a disrupted shipment |
| `get_fleet_summary` | Returns fleet-wide KPIs |
| `recommend_vehicle_for_shipment` | Returns the best available vehicle for a shipment |
| `get_cold_chain_status` | Returns temperature status and excursion details |
| `get_disruption_summary` | Returns fleet-wide disruption KPIs |

A logistics coordinator can ask IBM Bob in plain English — "Which shipments are at critical risk?" or "What should I do about SHP-003?" — and Bob will call the appropriate MCP tools and present a structured answer.
