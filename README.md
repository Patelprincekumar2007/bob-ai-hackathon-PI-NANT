# SmartRoute AI — Supply Chain Disruption Assistant

> An AI-powered supply chain control tower that detects disruptions in real time, scores shipment risk, recommends alternative routes, and monitors cold-chain integrity — powered by IBM watsonx.ai and built with Python + Streamlit.

---

## Table of Contents

- [Overview](#overview)
- [Team](#team)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Running the Tests](#running-the-tests)
- [MCP Server](#mcp-server)
- [Demo & Screenshots](#demo--screenshots)
- [Known Limitations](#known-limitations)
- [What We're Most Proud Of](#what-were-most-proud-of)

---

## Overview

SmartRoute AI brings together disruption detection, risk scoring, route optimisation, fleet management, and cold-chain monitoring into a single Streamlit dashboard. It is backed by IBM watsonx.ai for natural-language shipment explanations and exposes seven MCP tools that let an IBM Bob agent query the entire supply chain system conversationally.

---

## Team

| Field | Value |
|---|---|
| **Team Name** | PI-NANT |
| **Hackathon Track** | AI |
| **Team Lead** | Kashyap Nasit — 24cs109@charusat.edu.in |
| **Members** | Patel Princekumar (24cs073@charusat.edu.in), Patel Rudrakumar (24cs074@charusat.edu.in) |

---

## Problem Statement

Supply chain operators managing global shipments face severe, costly disruptions — port congestion, extreme weather, industrial strikes, and vessel failures — causing delays, cargo loss, and fleet under-utilisation. Manual rerouting across fragmented carrier portals can take hours and often occurs too late to prevent damage, particularly for temperature-sensitive pharmaceutical and perishable cargo.

---

## Solution

SmartRoute AI is an end-to-end supply chain intelligence platform that:

- **Automatically detects** active disruptions across ports, weather events, strikes, and vessel failures.
- **Scores every shipment's risk** on a 0–100 scale with CRITICAL / HIGH / MEDIUM / LOW classification.
- **Recommends alternative routes and carriers** with estimated delay and cost impact.
- **Monitors cold-chain temperature** in real time, raising excursion alerts before damage occurs.
- **Explains decisions in plain English** using IBM watsonx.ai, enabling non-technical coordinators to act confidently.

A clearly labelled **Demo Mode** operates without live credentials, making evaluation and local testing friction-free.

---

## Key Features

| # | Feature | Description |
|---|---|---|
| 1 | **Real-time Risk Scoring** | 0–100 composite score per shipment with four severity tiers |
| 2 | **Disruption Detection** | Automated ingestion and matching of port, weather, strike, and vessel events |
| 3 | **Route Recommendations** | Alternative carrier and lane suggestions with delay / cost estimates |
| 4 | **Fleet Optimisation** | Capacity and reefer-requirement matching across available vehicles |
| 5 | **Cold-Chain Monitoring** | Continuous temperature tracking with excursion severity classification |
| 6 | **AI Explanations** | IBM watsonx.ai–generated, plain-English shipment analysis |
| 7 | **IBM Bob MCP Integration** | 7 MCP tools for natural-language supply chain queries via IBM Bob |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Dashboard (app.py)            │
│   Home · Shipment Analysis · Disruptions · Fleet ·       │
│   Cold Chain · AI Insights                               │
└──────────┬──────────────────────────────────────────────┘
           │ calls
┌──────────▼──────────────────────────────────────────────┐
│                    Core Modules (src/core/)              │
│  DisruptionDetector · RiskEngine · RouteAdvisor          │
│  FleetOptimizer · ColdChainMonitor · WatsonxClient       │
└──────────┬──────────────────────────────────────────────┘
           │ reads                        │ queries
┌──────────▼──────────┐        ┌──────────▼──────────────┐
│  Mock Data (JSON)   │        │  IBM watsonx.ai          │
│  shipments          │        │  (or Demo fallback)      │
│  disruptions        │        └─────────────────────────┘
│  vehicles           │
│  temperature_readings│
└────────────────────┘

           ┌───────────────────────────────┐
           │  IBM Bob MCP Server           │
           │  mcp_server.py — 7 tools      │
           │  Exposes supply chain data    │
           │  to IBM Bob agent             │
           └───────────────────────────────┘
```

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3.11+ |
| **Dashboard** | Streamlit ≥ 1.35, Plotly ≥ 5.18, Pandas ≥ 2.2 |
| **IBM Technologies** | IBM watsonx.ai, IBM Bob, Model Context Protocol (MCP) |
| **Testing** | pytest ≥ 8.0 (127+ tests across 3 test files) |
| **CI/CD** | GitHub Actions (`validate.yml`) |
| **Data** | JSON mock datasets (no external database required) |
| **Config** | python-dotenv 1.0.1 |

---

## Repository Structure

```
sample_repo_for_ibm/
├── src/                          # Application source code
│   ├── app.py                    # Streamlit multi-page dashboard
│   ├── mcp_server.py             # IBM Bob MCP server entry point
│   ├── core/                     # Core business-logic modules
│   │   ├── disruption_detector.py
│   │   ├── risk_engine.py
│   │   ├── route_advisor.py
│   │   ├── fleet_optimizer.py
│   │   ├── cold_chain_monitor.py
│   │   └── watsonx_client.py
│   ├── mcp/                      # MCP tool definitions
│   ├── data/                     # JSON mock datasets
│   │   ├── shipments.json
│   │   ├── disruptions.json
│   │   ├── vehicles.json
│   │   └── temperature_readings.json
│   ├── .env.example              # Environment variable template
│   └── requirements.txt          # Python dependencies
├── docs/                         # Written documentation
│   ├── architecture.md
│   ├── problem-statement.md
│   ├── solution-overview.md
│   └── setup-guide.md
├── tests/                        # pytest test suite (127+ tests)
│   ├── test_part1.py
│   ├── test_part2.py
│   └── test_part3.py
├── demo/                         # Demo artifacts
│   ├── screenshots/              # App UI screenshots
│   ├── demo-video-link.txt
│   └── live-demo-url.txt
├── presentation/
│   └── slides.pptx               # Hackathon slide deck
├── .github/
│   └── workflows/validate.yml    # CI validation workflow
├── submission.yaml               # Structured submission metadata
└── README.md
```

---

## Getting Started

### Prerequisites

- Python **3.11 or higher**
- `git`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Patelprincekumar2007/sample_repo_for_ibm.git
cd sample_repo_for_ibm

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. (Optional) Configure IBM watsonx.ai credentials
cp src/.env.example src/.env
# Open src/.env and fill in your credentials.
# Leave blank to run in Demo Mode — no credentials required.

# 5. Launch the dashboard
streamlit run src/app.py
```

The application opens at **http://localhost:8501**.  
No credentials are required; Demo Mode activates automatically when `.env` is not configured.

---

## Running the Tests

```bash
# From the repository root (with the virtual environment active)
pytest tests/ -v
```

The test suite contains **127+ tests** covering the core engine (Part 1), the MCP server tools (Part 2), and the Streamlit dashboard logic (Part 3).

---

## MCP Server

SmartRoute AI ships an IBM Bob–compatible MCP server that exposes **7 tools** for natural-language supply chain queries:

| Tool | Description |
|---|---|
| `get_shipments` | List all shipments with current status |
| `get_disruptions` | Retrieve active disruption events |
| `score_shipment_risk` | Compute 0–100 risk score for a shipment |
| `recommend_routes` | Suggest alternative routes for an affected shipment |
| `get_fleet_status` | Return vehicle availability and capacity |
| `get_cold_chain_status` | Report temperature excursions for a shipment |
| `explain_shipment` | Generate an AI explanation via IBM watsonx.ai |

```bash
# Start the MCP server standalone
python src/mcp_server.py
```

Refer to [`src/mcp/README.md`](src/mcp/README.md) for IBM Bob registration instructions.

---

## Demo & Screenshots

| Artifact | Link |
|---|---|
| **Demo Video** | [demo/demo-video-link.txt](demo/demo-video-link.txt) |
| **Live Demo** | [demo/live-demo-url.txt](demo/live-demo-url.txt) |
| **Screenshots** | [demo/screenshots/](demo/screenshots/) |
| **Slide Deck** | [presentation/slides.pptx](presentation/slides.pptx) |

---

## Known Limitations

- Route recommendations are based on a curated static knowledge base — no live carrier API integration.
- IBM watsonx.ai explanations fall back to deterministic demo text when credentials are not configured.
- Temperature and shipment data originate from mock JSON datasets, not live IoT sensors or carrier systems.
- No authentication or multi-user support (demonstration scope only).

---

## What We're Most Proud Of

The complete, end-to-end operator workflow — from real-time disruption detection and risk scoring through to AI-powered route recommendations and cold-chain oversight — running in a single, cohesive application. We are equally proud of the IBM Bob MCP integration, which allows a logistics coordinator to interrogate the entire supply chain system in plain English without leaving their AI assistant.

---

*SmartRoute AI — PI-NANT · CHARUSAT University · IBM Bob Hackathon*
