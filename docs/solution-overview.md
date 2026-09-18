# Solution Overview

## What We Built

SmartRoute AI is an end-to-end operational decision-support system for maritime supply chain disruptions. It ingests shipment, disruption, vehicle, and cold-chain temperature data, runs a deterministic multi-factor risk engine, and produces **actionable recommended actions with escalation indicators** — all traceable, reproducible, and testable without any external API or database.

The system is designed as a **control tower**: a single screen where a logistics coordinator can see the full fleet at a glance, drill into any shipment, and receive a structured operational decision: *what happened → what the risk is → what to do now → who to notify → why*.

## How It Works — End-to-End Decision Workflow

The data flow from raw data to operational decision follows nine steps:

1. **Disruption detected** — `disruption_detector` matches active disruptions to shipments using five rules: explicit link, route match, carrier match, port match, and vessel match.

2. **Risk scored** — `risk_engine` calculates a 0-100 risk score using five weighted factors: disruption severity (35 pts), current delay (25 pts), deadline pressure (20 pts), shipment priority (15 pts), and cold-chain excursion (5 pts). Classified as CRITICAL (75+), HIGH (50+), MEDIUM (25+), or LOW.

3. **Alternatives generated** — `route_advisor` looks up the shipment's route in a knowledge base, filters by cargo type and disruption avoidance, and enriches each option with available vessel data.

4. **Fleet optimised** — `fleet_optimizer` identifies available vehicles matching cargo type, cold-chain requirements, weight, and TEU. Returns the best match with alternatives.

5. **Cold chain verified** — `cold_chain_monitor` analyses temperature readings, counts excursions, calculates deviation from safe range, and classifies severity as NORMAL, WARNING, or CRITICAL.

6. **Decision orchestrated** — **`decision_engine`** (new) calls all five modules above, applies deterministic recommended-action rules, and produces a single structured result including `recommended_action`, `action_priority`, `action_reason`, `escalation_required`, and `data_sources`.

   **Recommended-action rules (deterministic, no randomness):**

   | Condition | Action |
   |---|---|
   | CRITICAL + alternatives | Reroute Shipment + Escalate |
   | CRITICAL, no alternatives | Escalate to Logistics Manager |
   | HIGH + CRITICAL cold excursion + alternatives | Reroute + Cold-Chain Intervention |
   | HIGH + alternatives | Reroute Shipment |
   | HIGH + suitable vehicle | Assign Alternative Vehicle |
   | CRITICAL cold excursion only | Cold-Chain Intervention Required |
   | WARNING cold excursion | Monitor Temperature Closely |
   | MEDIUM | Continue Monitoring |
   | LOW | No Action Required |

   **Escalation is triggered when**: risk is CRITICAL; OR risk is HIGH AND cold excursion is CRITICAL; OR risk is HIGH AND delay >= 10 days.

7. **AI prompt enriched** — `watsonx_client` receives a rich structured prompt (built by `decision_engine.build_watsonx_prompt`) that includes risk factors, route options, vehicle status, cold-chain details, and the recommended action. The LLM *explains* the deterministic result in plain English — it does not recalculate risk.

8. **Dashboard displayed** — The Streamlit dashboard assembles all data across five pages (Dashboard, Shipments, Disruptions, Fleet, Cold Chain). The Shipments detail view shows the full end-to-end decision workflow: disruptions → risk → "Why is this risky?" → recommended action + escalation indicator → route alternatives → vehicle → cold-chain + "Why does this matter?" → AI explanation → technical details + MCP tool panel.

9. **IBM Bob integration** — `mcp_server.py` exposes all seven tools. The `explain_shipment` tool now uses the enriched prompt from the decision engine, returning `recommended_action`, `risk_level`, `escalation_required`, and `action_priority` in its structured response.

## Architecture Summary

The application has four layers:

- **Data layer** — Four JSON files in `src/data/` (shipments, disruptions, vehicles, temperature_readings). No database required.
- **Logic layer** — Five domain modules in `src/core/` plus `watsonx_client`.
- **Orchestration layer** — `src/core/decision_engine.py` wires all domain modules into one structured result without duplicating any logic.
- **Interface layer** — `src/app.py` (Streamlit dashboard) and `src/mcp_server.py` (IBM Bob MCP server with 7 tools).

See [`architecture.md`](architecture.md) for the full component diagram.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Python + Streamlit** | Zero-friction setup — no frontend build step, runs in a single `pip install + streamlit run`. |
| **JSON mock data** | Judges can run the project instantly without a database, credentials, or seeding script. |
| **Deterministic risk scoring** | Reproducible, explainable scores that pass automated tests — no ML model to train or deploy. |
| **Decision engine as thin orchestrator** | `decision_engine.py` calls existing modules — no logic duplication. One structured result powers both the UI and the MCP server. |
| **Deterministic recommended actions** | Rules are based on existing risk thresholds, ensuring the action is always consistent with the score shown. |
| **IBM Bob MCP server** | Exposes all seven supply chain tools so IBM Bob can answer natural-language questions using the same logic as the dashboard. |
| **Mock AI fallback** | When `WATSONX_API_KEY` is not set, `watsonx_client` returns a labelled mock response. The app always runs. |
| **`@st.cache_data`** | Expensive data loads are cached in the Streamlit session to keep the demo snappy. |

## IBM Technologies Used

### IBM watsonx.ai

The `watsonx_client` module uses the `ibm-watsonx-ai` SDK to call the Granite 13B Instruct model. It receives a rich, structured prompt from `decision_engine.build_watsonx_prompt()` that includes the shipment ID, risk score, factor breakdown, active disruptions, route options, vehicle recommendation, cold-chain status, and the recommended action. The LLM explains the already-calculated result in plain English. Output is displayed with a clear `● watsonx.ai Live` or `○ Demo Mode — Mock AI` label.

### IBM Bob MCP Server

`src/mcp_server.py` implements seven MCP tools that IBM Bob can call:

| Tool | What it returns |
|---|---|
| `get_shipment_risk` | Risk score, classification, factor breakdown |
| `get_shipment_disruptions` | Active disruptions affecting a shipment |
| `recommend_route` | Alternative route options for a disrupted shipment |
| `recommend_vehicle` | Best available vessel for a shipment |
| `get_fleet_status` | Fleet-wide utilisation KPIs |
| `get_temperature_alerts` | Cold-chain temperature excursion alerts |
| `explain_shipment` | AI explanation + recommended action + escalation status |

A logistics coordinator can ask IBM Bob — *"Which shipments need immediate attention?"* or *"What should I do about SHP-006?"* — and Bob will call the MCP tools and return a structured answer including the recommended action and escalation status.
