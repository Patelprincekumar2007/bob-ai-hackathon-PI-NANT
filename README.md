# SmartRoute AI — Supply Chain Control Tower 🚢

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/IBM%20watsonx.ai-Granite%20LLM-052FAD?style=for-the-badge&logo=ibm&logoColor=white" alt="IBM watsonx.ai" />
  <img src="https://img.shields.io/badge/Pytest-191%20Passed-2EA44F?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
  <img src="https://img.shields.io/badge/Design-Stitch%20Executive-00E5FF?style=for-the-badge" alt="Stitch Executive Design" />
</p>

> An enterprise-grade **Supply Chain Control Tower** powered by **IBM watsonx.ai** and built with **Python + Streamlit**. Automatically detects port/weather disruptions in real time, computes multi-factor shipment risk scores, recommends alternative maritime routes, optimizes fleet utilization, and monitors cold-chain thermal integrity — styled with a hyper-polished **Stitch Executive Glassmorphic Design System**.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Team Information](#-team-information)
- [Problem Statement](#-problem-statement)
- [The SmartRoute AI Solution](#-the-smartroute-ai-solution)
- [Stitch UI & Visual Design System](#-stitch-ui--visual-design-system)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
- [Configuring IBM watsonx.ai](#-configuring-ibm-watsonxai)
- [Running the 191 Test Suite](#-running-the-191-test-suite)
- [IBM Bob MCP Integration](#-ibm-bob-mcp-integration)
- [Real-Time Production Roadmap](#-real-time-production-roadmap)

---

## VideoLink of execution:
https://drive.google.com/file/d/1BKWKyST6HrQKQtWT4d3rUH1JzfjM_zDI/view?usp=sharing

---
## 🌐 Overview

**SmartRoute AI** unifies disruption detection, dynamic risk scoring, route optimization, fleet capacity matching, and cold-chain thermal monitoring into an interactive dashboard. 

It is backed by **IBM watsonx.ai (Granite LLM)** for natural-language operational explanations and exposes an **IBM Bob MCP Server (7 tools)** allowing an AI agent to interrogate the entire supply chain conversationally in plain English.

---

## 👥 Team Information

| Field | Details |
|---|---|
| **Team Name** | **PI-NANT** |
| **Hackathon Track** | AI / IBM Bob AI Hackathon 2026 |
| **Team Lead** | Kashyap Nasit (`24cs109@charusat.edu.in`) |
| **Team Members** | Patel Princekumar (`24cs073@charusat.edu.in`), Patel Rudrakumar (`24cs074@charusat.edu.in`) |
| **Institution** | CHARUSAT University |

---

## ⚠️ Problem Statement

Global supply chain operators managing maritime & intermodal freight face costly disruptions:
- **Port Congestion & Bottlenecks** leading to multi-day container delays.
- **Extreme Weather & Typhoons** stranding vessels on critical ocean routes.
- **Labor Strikes & Vessel Failures** causing unexpected route detours.
- **Cold-Chain Excursions** causing thermal degradation of temperature-sensitive pharmaceuticals and perishable food cargo.

Manual resolution across fragmented carrier portals takes hours and often happens after financial damage or cargo spoilage has occurred.

---

## 💡 The SmartRoute AI Solution

SmartRoute AI provides an automated, end-to-end supply chain intelligence platform:

1. **Automated Disruption Matching**: Maps live port congestions, strikes, and weather alerts to affected shipments, carriers, and vessels.
2. **Multi-Factor Risk Engine**: Computes a dynamic `0–100` risk score for every shipment categorized into **CRITICAL**, **HIGH**, **MEDIUM**, or **LOW** severity tiers.
3. **AI Route & Vessel Advisor**: Recommends alternative sea lanes and available fleet vessels with delay savings and additional cost impacts (`USD`).
4. **Cold-Chain Thermal Tracking**: Continuously monitors container sensors, detecting excursion severity outside safe bands (e.g. `2°C – 8°C`).
5. **IBM watsonx.ai Explanations**: Generates plain-English coordinator reports powered by IBM Granite LLM models.

---

## 🎨 Stitch UI & Visual Design System

SmartRoute AI features a custom **Stitch Executive Glassmorphic UI** built directly in Python & Vanilla CSS, requiring zero React overhead:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Stitch Executive Design System                    │
├────────────────────────────────────────────────────────────────────────┤
│ • Palette: Obsidian Space (#0B0F19), Cyber Dark Slate (#141A29)        │
│ • Accents: Neon Cyan (#00E5FF), Crimson (#FF3366), Amber (#FF9900)    │
│ • Glassmorphism: Backdrop blur (16px), subtle radial gradient glows    │
│ • Controls: Clean custom components with ZERO raw SVG text leaks        │
│ • Maps: Interactive Plotly Scattergeo Natural Earth Projection Map     │
└────────────────────────────────────────────────────────────────────────┘
```

### Key UI Components
- **Global Control Tower Route Map**: Interactive Plotly map visualizer rendering origin-destination ocean shipping lanes, risk color codes, and port disruption hotspot markers.
- **Clickable Risk Cards**: Interactive risk breakdown widgets that automatically navigate and filter the Shipment Register.
- **Interactive Cold-Chain Excursion Chart**: Plotly time-series chart featuring target safe range shading (`2°C – 8°C`) and sensor reading tooltips.
- **One-Click Clipboard Actions**: Custom embedded JavaScript buttons to copy Shipment IDs and AI Explanations instantly.

---

## ✨ Key Features

| # | Feature | Description |
|:---:|---|---|
| 1 | **Multi-Factor Risk Scoring** | Dynamic `0–100` composite score calculated from disruption severity, delay days, deadline pressure, cargo priority, and thermal sensitivity. |
| 2 | **Disruption Detection** | Real-time matching of active port, weather, labor, and vessel failure events. |
| 3 | **Route Advisor** | Evaluates alternative sea lanes and carrier options with cost/delay impact breakdowns. |
| 4 | **Fleet Capacity Optimizer** | Matches at-risk cargo to available fleet vessels based on TEU capacity and reefer requirements. |
| 5 | **Cold-Chain Sensor Monitor** | Time-series telemetry tracking with excursion severity classification. |
| 6 | **IBM watsonx.ai Granite LLM** | Plain-English operational explanations generated via IBM Granite LLMs. |
| 7 | **IBM Bob MCP Integration** | 7 Model Context Protocol (MCP) tools for conversational supply chain control. |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Streamlit Control Tower (app.py)                    │
│   Dashboard · Shipments · Disruptions · Fleet · Cold Chain · AI Insights│
└────────────────────────────┬────────────────────────────────────────────┘
                             │ calls
┌────────────────────────────▼────────────────────────────────────────────┐
│                      Core Engine (src/core/)                            │
│  DisruptionDetector · RiskEngine · RouteAdvisor · FleetOptimizer        │
│  ColdChainMonitor · WatsonxClient · ActivityLog                         │
└──────────────┬───────────────────────────────────────────┬──────────────┘
               │ reads                                     │ queries
┌──────────────▼─────────────┐                ┌────────────▼─────────────┐
│   Structured Data (JSON)   │                │     IBM watsonx.ai       │
│   shipments.json           │                │  Granite-13B-Instruct    │
│   disruptions.json         │                │  (or Demo fallback)      │
│   vehicles.json            │                └──────────────────────────┘
│   temperature_readings.json│
└────────────────────────────┘

               ┌───────────────────────────────────────────┐
               │         IBM Bob MCP Server                │
               │         src/mcp_server.py (7 Tools)        │
               │         Exposes supply chain tools        │
               │         to conversational AI agents       │
               └───────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Core Runtime**: Python `3.11+`
- **Frontend & Visualization**: Streamlit `≥ 1.35`, Plotly `≥ 5.18`, Pandas `≥ 2.2`
- **AI & Integration**: IBM watsonx.ai (`ibm-watsonx-ai`), Model Context Protocol (`mcp ≥ 1.0.0`), `python-dotenv`
- **Design System**: Vanilla CSS3 (Glassmorphism, CSS Grid, Custom Controls)
- **Testing**: pytest `≥ 8.0` (**191 unit tests, 100% passing**)

---

## 📁 Repository Structure

```
sample_repo_for_ibm/
├── src/                          # Application source code
│   ├── app.py                    # Streamlit multi-page dashboard & UI
│   ├── mcp_server.py             # IBM Bob MCP server entry point
│   ├── core/                     # Core business logic modules
│   │   ├── disruption_detector.py # Disruption matching & route lookup
│   │   ├── risk_engine.py         # 0-100 Multi-factor risk scoring
│   │   ├── route_advisor.py       # Rerouting engine & cost calculator
│   │   ├── fleet_optimizer.py     # Capacity & vessel matching
│   │   ├── cold_chain_monitor.py  # Thermal excursion sensor tracking
│   │   ├── watsonx_client.py      # IBM watsonx.ai Granite LLM client
│   │   └── activity_log.py        # Operations review tracking
│   ├── mcp/                      # MCP tool definitions
│   ├── data/                     # Structured JSON datasets
│   ├── .env                      # Local environment configuration
│   └── requirements.txt          # Python dependencies
├── tests/                        # Full Pytest suite (191 tests)
│   ├── test_part1.py             # Engine logic tests
│   ├── test_part2.py             # MCP tool server tests
│   └── test_part3.py             # Dashboard & helper function tests
├── submission.yaml               # IBM Bob Hackathon submission manifest
└── README.md                     # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python **3.11 or higher**
- `git`

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/Patelprincekumar2007/sample_repo_for_ibm.git
cd sample_repo_for_ibm

# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r src/requirements.txt
```

### 3. Launch the Control Tower Dashboard
```bash
python -m streamlit run src/app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🔑 Configuring IBM watsonx.ai

SmartRoute AI runs in **Demo Mode** out of the box. To connect your live IBM watsonx.ai account:

Open `src/.env` and fill in your IBM Cloud credentials:

```env
WATSONX_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
```

*(Both `WATSONX_API_KEY` and `WATSONX_APIKEY` formats are supported).*

Install the official IBM SDK:
```bash
pip install ibm-watsonx-ai
```

Upon restart, the dashboard top-bar badge will update to **`🟢 watsonx.ai`** and query live IBM Granite models.

---

## 🧪 Running the 191 Test Suite

The repository includes **191 unit tests** with 100% pass coverage across core modules, MCP tools, and app logic.

```bash
# Run full test suite
python -m pytest
```

---

## 🤖 IBM Bob MCP Integration

SmartRoute AI includes an **MCP (Model Context Protocol) Server** exposing 7 tools to conversational agents like IBM Bob:

| Tool Name | Parameters | Description |
|---|---|---|
| `get_shipments` | `risk_level`, `status` | List shipments filtered by risk tier or status |
| `get_disruptions` | `severity` | Retrieve active port, weather, or strike disruptions |
| `score_shipment_risk` | `shipment_id` | Return detailed 0–100 factor breakdown for a shipment |
| `recommend_routes` | `shipment_id` | Suggest alternative routes with delay/cost estimates |
| `get_fleet_status` | `carrier` | Return vehicle availability, TEU capacity, and reefer specs |
| `get_cold_chain_status` | `shipment_id` | Report thermal excursions & temperature logs |
| `explain_shipment` | `shipment_id` | Generate an AI explanation via IBM Granite LLM |

```bash
# Start MCP server standalone
python src/mcp_server.py
```

---

## 🔮 Real-Time Production Roadmap

To transition SmartRoute AI from local demonstration to enterprise production:

```
[ AIS Ship Telemetry ] ──────┐
[ IoT Container Sensors ] ───┼──► [ Kafka Stream ] ──► [ PostgreSQL / TimescaleDB ] ──► [ Core Engine ]
[ Port & Weather Feeds ] ────┘
```

1. **Maritime AIS Feeds**: Ingest live vessel positions via Spire Maritime / MarineTraffic APIs.
2. **Container IoT Telemetry**: Stream container temperature sensor events over MQTT into `cold_chain_monitor.py`.
3. **Database Storage**: Migrate JSON datasets to PostgreSQL & TimescaleDB time-series storage.
4. **Automated Triggers**: Run Celery workers to continuously re-evaluate shipment risk as live telemetry updates arrive.

---

<p align="center">
  <b>SmartRoute AI</b> — Team PI-NANT · CHARUSAT University · IBM Bob AI Hackathon 2026
</p>
