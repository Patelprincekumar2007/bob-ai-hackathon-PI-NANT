# SmartRoute AI — Complete Solution Plan
### Supply Chain Control Tower · Team PI-NANT · IBM Bob AI Hackathon 2026

---

## Table of Contents

1. [The Real Problem](#1-the-real-problem)
2. [What Currently Exists — The Solution Landscape](#2-what-currently-exists--the-solution-landscape)
3. [Where the Gap Is](#3-where-the-gap-is)
4. [SmartRoute AI — The Solution](#4-smartroute-ai--the-solution)
5. [How the Current System Works — Module by Module](#5-how-the-current-system-works--module-by-module)
6. [The Decision Pipeline End-to-End](#6-the-decision-pipeline-end-to-end)
7. [Algorithms and Logic — Deep Dive](#7-algorithms-and-logic--deep-dive)
8. [IBM Bob and MCP — The Conversational Layer](#8-ibm-bob-and-mcp--the-conversational-layer)
9. [How SmartRoute Differs from Traditional Approaches](#9-how-smartroute-differs-from-traditional-approaches)
10. [Impact Model](#10-impact-model)
11. [Current Prototype vs Production Roadmap](#11-current-prototype-vs-production-roadmap)
12. [Jury Defense Reference](#12-jury-defense-reference)

---

## 1. The Real Problem

### 1.1 The Surface Problem

Global maritime supply chains move over 11 billion tonnes of cargo every year. Weather events, port congestion, labour disputes, vessel failures, and geopolitical events regularly interrupt these flows. When a disruption occurs, operations teams must answer a cascade of questions — usually manually, across disconnected systems — before any corrective action can begin.

### 1.2 The Actual Engineering Problem

The difficulty is not detecting a disruption. Anyone can observe a cyclone or a port strike. The difficulty is **converting that external event into a prioritised set of actionable operational decisions** across hundreds of affected shipments before the consequences become irreversible.

This is a **propagation and decision-latency problem**, not merely a visibility problem.

```
                         CYCLONE (DISR-002)
                               │
                               ▼
                     PORT DISRUPTION — Mumbai
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
      SHP-002              SHP-XXX              SHP-YYY
   (Pharma, Critical)    (Electronics)      (General Cargo)
          │                    │                    │
          ▼                    ▼                    ▼
   COLD CHAIN RISK?        DELAY RISK?         DEADLINE RISK?
          │
          ▼
   Temperature: 9.2°C
   (Limit: 2–8°C)
          │
          ▼
   EXCURSION DETECTED
          │
          ▼
   Alternative route?
   Alternative vessel?
   Reefer capability?
   Cost vs. speed tradeoff?
```

Without an integrated decision layer, this analysis takes **hours across multiple systems**. With it, it takes **seconds**.

### 1.3 The Four Problem Requirements

The challenge decomposed into four explicit engineering requirements:

| # | Requirement | Core Question |
|---|---|---|
| 1 | Identify affected shipments | Which of my shipments are exposed to this disruption? |
| 2 | Recommend re-routing or carrier alternatives | What can we change, and at what cost? |
| 3 | Identify idle fleet assets for redeployment | Which vessels can we move to address the gap? |
| 4 | Monitor cold-chain IoT logs and classify temperature excursions | Is the cargo still safe? |

Everything else — risk scoring, IBM Bob integration, AI explanations — exists to support and connect these four capabilities.

---

## 2. What Currently Exists — The Solution Landscape

To understand SmartRoute's position, we must be honest about existing commercial technology.

### 2.1 Supply-Chain Visibility Platforms

**Examples: project44, FourKites, Descartes**

These platforms aggregate shipment and transportation data from carriers, telematics providers, and ports. They answer the primary question: *"Where is my shipment and when will it arrive?"*

**Current capabilities (as of 2025):**
- Real-time multimodal shipment tracking (ocean, road, rail, air)
- Predictive ETA using machine learning
- Port and terminal congestion intelligence
- Disruption alerts tied to specific shipments
- Carrier and network visibility

**Limitation for our problem:** Visibility platforms primarily tell operators *what* is happening. They are increasingly adding intelligence, but the core model remains event notification rather than integrated decision support. The operator still must correlate information, evaluate alternatives, and make decisions across fragmented interfaces.

### 2.2 Supply-Chain Control Towers

**Examples: Blue Yonder, SAP Integrated Business Planning, o9 Solutions**

A control tower is a centralised operational layer that aggregates supply-chain data and presents exceptions and recommendations in one interface.

**Current capabilities:**
- Network-wide visibility and exception management
- Risk assessment and impact analysis
- AI-assisted recommendations
- Scenario planning
- Integration with ERP, WMS, and TMS

**Limitation for our problem:** Enterprise control towers are powerful but complex, expensive, and built around large ERP integrations. They assume a fully connected data ecosystem. They are not designed to be queried conversationally by an AI agent through a standardised tool protocol.

### 2.3 Transportation Management Systems (TMS)

**Examples: Oracle TMS, SAP TM, MercuryGate, project44 Network TMS**

TMS products handle shipment planning, carrier selection, tendering, routing, booking, and freight cost management.

**Limitation for our problem:** Traditional TMS is primarily a planning and execution system. It is not primarily an exception-management or disruption-response system, though modern platforms are adding these capabilities.

### 2.4 Fleet Telematics and Asset Management

**Examples: Samsara, Geotab, ORBCOMM**

Fleet platforms track vehicle location, fuel, utilisation, maintenance state, driver performance, and temperature.

**Limitation for our problem:** Fleet management systems are asset-centric, not shipment-centric or disruption-centric. Connecting a disruption event to idle fleet capacity that can be redeployed requires a bridge layer that these systems do not natively provide.

### 2.5 Cold-Chain Monitoring Platforms

**Examples: Samsara Reefer Monitoring, ORBCOMM Reefer, FourKites Cold Chain**

Cold-chain platforms provide continuous temperature and humidity tracking, threshold alerts, and compliance logging.

**Current capabilities (FourKites, ORBCOMM):**
- Continuous temperature monitoring during transit
- Threshold excursion alerts
- Carrier notification
- GDP compliance documentation
- Some platforms now offer remote reefer temperature adjustment

**Limitation for our problem:** Cold-chain monitoring exists as a **separate system** from disruption management, risk scoring, and route optimisation. A pharmaceutical shipment facing both a cyclone *and* a temperature excursion requires **both signals to be understood together** to properly assess the operational risk.

### 2.6 The Critical Observation

All five categories above are **real, capable, and commercially deployed**. The supply-chain technology market has well-funded solutions for each individual capability.

The gap is **integration of all four challenge requirements around a common, explainable, conversationally accessible decision layer**.

---

## 3. Where the Gap Is

### 3.1 Fragmentation Creates Decision Latency

A typical disruption response workflow without an integrated layer:

```
Cyclone Alert
     │
     ▼
Logistics Manager receives email/SMS
     │
     ▼
Opens visibility platform → identifies affected route
     │
     ▼
Opens TMS → checks active shipments on that route
     │
     ▼
Opens carrier portal → checks vessel status
     │
     ▼
Opens ERP → checks cargo value and deadline
     │
     ▼
Opens cold-chain dashboard → checks temperature logs
     │
     ▼
Opens fleet management → checks available vessels
     │
     ▼
Manually estimates cost of alternatives
     │
     ▼
Escalates to operations manager
     │
     ▼
DECISION
     │
     ▼ (total elapsed time: 2–6 hours)
ACTION
```

Each system switch requires context-switching, re-authentication, and data correlation by a human operator. During that time, the disruption is actively worsening.

### 3.2 What an Integrated Decision Layer Does

```
Cyclone Alert
     │
     ▼
SMARTROUTE AI
     │
     ├── Correlates disruption → affected shipments (seconds)
     ├── Scores risk for each (seconds)
     ├── Identifies critical/high priority (immediate)
     ├── Evaluates alternative routes with cost/delay (seconds)
     ├── Identifies idle reefer-capable vessels (seconds)
     ├── Checks cold-chain status for pharma shipments (seconds)
     └── Presents IBM Bob with complete picture (immediate)
     │
     ▼
DECISION (total elapsed time: < 60 seconds)
     │
     ▼
ACTION
```

This is the transformation SmartRoute provides.

### 3.3 The Conversational Access Gap

None of the commercial platforms above expose their core decision capabilities as **standardised, AI-agent-callable tools**. IBM Bob cannot natively ask project44 "which shipments need immediate intervention?" and get a structured, orchestratable response.

MCP (Model Context Protocol) fills this gap. SmartRoute's seven MCP tools turn supply-chain decision capabilities into first-class agent tools that IBM Bob can discover, invoke, and reason about in natural language.

---

## 4. SmartRoute AI — The Solution

### 4.1 One-Sentence Description

**SmartRoute AI is a supply-chain disruption intelligence and decision-support control tower that converts operational events into prioritised, explainable actions, and exposes those capabilities conversationally through IBM Bob via MCP.**

### 4.2 The Control Tower Model: Observe → Understand → Act

```
┌─────────────────────────────────────────────────────────────────┐
│                      OBSERVE                                    │
│   Shipments · Disruptions · Fleet · Temperature Telemetry       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     UNDERSTAND                                  │
│   Affected shipments · Risk scores · Cold-chain severity        │
│   Fleet utilisation · Route feasibility                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                        ACT                                      │
│   Reroute · Change carrier/vessel · Redeploy idle assets        │
│   Escalate cold-chain breach · Notify consignee                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│               CONVERSATIONAL ACCESS                             │
│             IBM Bob + MCP (7 tools)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 The Four Pillars

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  DISRUPTION  │  ROUTE/FLEET │  COLD CHAIN  │  AI AGENT    │
│INTELLIGENCE  │OPTIMISATION  │INTELLIGENCE  │  INTERFACE   │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Correlation  │ Reroute/     │ Temperature  │ IBM Bob      │
│ across 5     │ Redeploy     │ excursion    │ + MCP        │
│ entity types │ matching     │ detection    │ + Granite    │
└──────────────┴──────────────┴──────────────┴──────────────┘
                    RISK ENGINE (common prioritisation)
```

---

## 5. How the Current System Works — Module by Module

### 5.1 Data Layer (`src/data/`)

The current prototype uses four structured datasets that represent a simulated operational world:

| File | Contents | Records |
|---|---|---|
| `shipments.json` | 7 active shipments across 7 global routes | SHP-001 to SHP-007 |
| `disruptions.json` | 5 disruptions (4 active, 1 monitoring) | DISR-001 to DISR-005 |
| `vehicles.json` | 7 vessels (6 available, 1 disabled) | V-001 to V-007 |
| `temperature_readings.json` | Sensor logs for 3 shipments | SHP-002, SHP-004, SHP-003 |

**Design intent:** These files simulate the output of live AIS feeds, carrier APIs, port intelligence, and IoT sensor streams. The decision engines are independent of the data source — replacing JSON with streaming feeds does not require redesigning any engine.

### 5.2 Disruption Detector (`src/core/disruption_detector.py`)

**Purpose:** Determine which active shipments are exposed to which disruptions.

**The five matching rules** (any one match is sufficient):

| Rule | Check | Example |
|---|---|---|
| 1 | `disruption.id ∈ shipment.active_disruption_ids` | SHP-001 explicitly lists DISR-001 |
| 2 | `shipment.route_id ∈ disruption.affected_routes` | SHP-002's `ROUTE-EU-INDIA-01` is in DISR-002's routes |
| 3 | `shipment.carrier ∈ disruption.affected_carriers` | SHP-001's `MaerskLine` is in DISR-001's carriers |
| 4 | `shipment.origin.port_code ∈ disruption.affected_ports` OR destination | SHP-002 destination `INBOM` is in DISR-002's ports |
| 5 | `shipment.vessel_id ∈ disruption.affected_vessel_ids` | SHP-006's vessel `V-005` is listed in DISR-004 |

**Why this matters:** Disruptions don't announce themselves at the shipment level. A cyclone advisory names a *port*, not individual shipments. This multi-dimensional correlation transforms one disruption event into the complete set of exposed shipments automatically.

**Output structure per match:**
```python
{
    "disruption_id": "DISR-002",
    "type": "weather",
    "title": "Severe Cyclone – Arabian Sea",
    "severity": "critical",
    "estimated_delay_days": 5,
    "additional_cost_usd": 12000,
    "match_reason": "shipment route ROUTE-EU-INDIA-01 is affected; destination port INBOM is affected"
}
```

The `match_reason` field provides a human-readable explanation for every match — essential for operational trust in automated outputs.

### 5.3 Risk Engine (`src/core/risk_engine.py`)

**Purpose:** Convert operational state into a single 0–100 priority score with full factor decomposition.

**The five-factor weighted model:**

| Factor | Max Points | Scoring Logic |
|---|---|---|
| Disruption severity | 35 | CRITICAL=35, HIGH=25, MEDIUM=15, LOW=8, None=0 |
| Delay days | 25 | Non-linear: 0→0, ≤2→5, ≤5→10, ≤9→17, ≤13→22, >13→25 |
| Deadline pressure | 20 | Days until ETA: passed→20, ≤3→18, ≤7→14, ≤14→8, ≤30→4, >30→0 |
| Shipment priority | 15 | CRITICAL=15, HIGH=10, MEDIUM=5, LOW=0 |
| Cold-chain excursion | 5 | CRITICAL excursion→5, WARNING→3, none/N/A→0 |

**Classification bands:**
```
75–100 → CRITICAL
50–74  → HIGH
25–49  → MEDIUM
 0–24  → LOW
```

**Why deterministic (not ML)?** Risk calculations must be **reproducible and auditable**. If SHP-002 scores 87/100 today, it should score 87/100 tomorrow under identical inputs. This matters for:
- Operator trust in the system
- Compliance and audit trails
- Testing and validation (191 unit tests pass deterministically)

An LLM-generated risk score would be neither reproducible nor auditable.

**Example output for SHP-002:**
```
Risk score: 87/100 — CRITICAL

Contributing factors:
  Disruption severity : 35/35  Disruption severity CRITICAL -> 35/35 pts. (Severe Cyclone – Arabian Sea)
  Current delay       :  0/25  Delay 0 day(s) -> 0/25 pts.
  Deadline pressure   : 18/20  ETA in 2 day(s) – critical -> 18/20 pts.
  Shipment priority   : 15/15  Priority CRITICAL -> 15/15 pts.
  Cold-chain status   :  3/5   Cold-chain excursion (WARNING) detected -> 3/5 pts.
```

### 5.4 Route Advisor (`src/core/route_advisor.py`)

**Purpose:** Identify feasible alternative routes for disrupted shipments and present their operational trade-offs.

**The filtering pipeline:**

```
All alternatives for this route_id
              │
              ▼
Filter 1: cargo_type ∈ alt.cargo_types_ok?
              │
              ▼
Filter 2: active_disruption_ids ∩ alt.avoids_disruptions ≠ ∅
              │
              ▼
Filter 3: preferred_vessel available, correct cargo type?
              │
              ▼
FEASIBLE ALTERNATIVES (with vehicle availability enrichment)
```

**The alternative knowledge base** (`ROUTE_ALTERNATIVES`) covers all 7 active routes with handcrafted realistic alternatives, each specifying:
- Alternative route ID and description
- Suggested carriers
- Preferred vessel IDs
- Extra delay days and extra cost (USD)
- Compatible cargo types
- Which disruptions this alternative avoids
- Human-readable reason

**Real example — SHP-002 (pharmaceutical, Hamburg → Mumbai):**

| Option | Description | Extra Delay | Extra Cost |
|---|---|---|---|
| ROUTE-EU-INDIA-SOUTH-01 | Cape of Good Hope diversion | +6 days | +$14,000 |
| ROUTE-EU-INDIA-ALT-AIR | Emergency air freight | −4 days | +$95,000 |

This is a trade-off presentation, not a single "magic answer" — because the right choice depends on cargo value, deadline urgency, and risk tolerance.

### 5.5 Fleet Optimizer (`src/core/fleet_optimizer.py`)

**Purpose:** Identify available and idle fleet assets, and recommend the best-fit vehicle for a given shipment's requirements.

**Idle vehicle definition:**
```
idle = (status == "available") AND (vessel_id ∉ assigned_vessel_ids)
```

Where `assigned_vessel_ids` = vessel IDs appearing in active/delayed/loading shipments.

**Vehicle recommendation — constraint priority order:**
1. `status == "available"` AND `available_teu >= 1`
2. `available_weight_kg >= shipment.weight_kg`
3. `cargo_type ∈ vehicle.supported_cargo_types`
4. If `requires_cold_chain`: `available_reefer_slots >= 1`
5. Sort: if reefer needed → `(reefer_slots, teu)` DESC; otherwise `teu` DESC

**Fleet state from current data:**
- V-005 (MV Eastern Star): UNAVAILABLE — engine failure, adrift in Indian Ocean
- V-002 (MV Orient Express): Available but nearly full (800 TEU remaining)
- V-006 (MV Southern Cross): 4,300 TEU available — largest idle capacity
- V-007 (MV Rhine Express): 4,500 TEU available, 200 reefer slots — best for cold chain

**Why this matters:** Without a fleet optimiser, a coordinator might manually contact 6 carriers to find available capacity. This system identifies candidate vessels in milliseconds.

### 5.6 Cold Chain Monitor (`src/core/cold_chain_monitor.py`)

**Purpose:** Analyse temperature sensor logs to detect excursions and classify their operational severity.

**Excursion detection logic:**
```python
out_of_range = (t < temp_min) OR (t > temp_max)
excursion = (status == "excursion") OR out_of_range
```

**Severity classification (configurable):**

| Severity | Condition |
|---|---|
| NORMAL | Zero excursions |
| WARNING | 1–2 excursions AND max deviation ≤ `WARNING_DELTA_C` (1.0°C) |
| CRITICAL | ≥3 excursions OR max deviation > `WARNING_DELTA_C` |

**Why both frequency AND magnitude?**
- Shipment A: 1 excursion, 0.2°C above limit → minor, brief, likely safe
- Shipment B: 1 excursion, 5°C above limit → potentially cargo-destroying
- Shipment C: 20 micro-excursions → cumulative thermal stress even if each is small

All three scenarios require different responses. A single threshold check cannot distinguish them.

**Real data from SHP-002 (pharmaceutical vaccines, 2–8°C requirement):**
```
2025-07-15 08:00  4.2°C  Hamburg pre-load         NORMAL
2025-07-15 14:00  3.8°C  Hamburg vessel hold       NORMAL
2025-07-16 02:00  4.1°C  North Sea at sea          NORMAL
2025-07-17 14:00  9.2°C  Strait of Gibraltar       EXCURSION ← +1.2°C above limit
2025-07-18 02:00  8.5°C  Mediterranean Sea         EXCURSION ← +0.5°C above limit
2025-07-18 14:00  6.1°C  Suez Canal approach       NORMAL (reefer repaired)
2025-07-19 08:00  5.5°C  Red Sea at sea            NORMAL
2025-07-20 08:00  4.9°C  Arabian Sea at sea        NORMAL
```

Result: 2 excursions, max deviation = 1.2°C → **WARNING** severity.

This detected **during transit** — not at delivery. That is the core operational value.

### 5.7 watsonx Client (`src/core/watsonx_client.py`)

**Purpose:** Generate natural-language explanations of structured operational results using IBM Granite LLM.

**Critical design principle — Granite explains, it does not calculate:**

```
Python Risk Engine calculates:   score=87, classification=CRITICAL, factors=[...]
                                         │
                                         ▼
Granite receives structured context and generates:
"Shipment SHP-002 requires immediate attention. A critical cyclone in the Arabian Sea
has placed it on a severely affected route with a deadline in 2 days. The pharmaceutical
cargo has also experienced temperature excursions above the 8°C limit. Coordinator
should consider the Cape of Good Hope diversion or emergency air freight immediately."
```

The LLM is not trusted with logistics calculations. It is given **facts** and asked to **explain** them. This dramatically reduces hallucination risk for operational decisions.

**Demo mode:** When watsonx credentials are not configured, the system generates a clearly-labelled deterministic explanation. The decision engines operate identically with or without live AI.

### 5.8 Activity Log (`src/core/activity_log.py`)

**Purpose:** Persist operator review flags to `review_flags.json` without modifying any source data files.

Records when an operator has reviewed a shipment, by whom, and at what time. Provides a foundation for operational audit trails in production.

---

## 6. The Decision Pipeline End-to-End

Using the scenario: **DISR-002 (Cyclone) → SHP-002 (Pharmaceuticals)**

```
Step 1 — DATA LOAD
    disruptions.json → DISR-002: critical, Arabian Sea, affects ROUTE-EU-INDIA-01, INBOM
    shipments.json   → SHP-002: route=ROUTE-EU-INDIA-01, dest=INBOM, cold_chain=true

Step 2 — DISRUPTION CORRELATION (disruption_detector.py)
    Rule 2: SHP-002.route_id == DISR-002.affected_routes[0]  → MATCH
    Rule 4: SHP-002.destination.port_code == DISR-002.affected_ports[0] → MATCH
    match_reason: "shipment route ROUTE-EU-INDIA-01 is affected; destination port INBOM is affected"

Step 3 — RISK CALCULATION (risk_engine.py)
    disruption_severity: 35/35  (CRITICAL cyclone)
    delay:               0/25   (no delay yet)
    deadline_pressure:  18/20   (ETA in 2 days)
    priority:           15/15   (CRITICAL cargo)
    cold_chain:          3/5    (WARNING — 2 excursions, max 1.2°C deviation)
    TOTAL: 71 → HIGH (near CRITICAL threshold)

Step 4 — COLD CHAIN ANALYSIS (cold_chain_monitor.py)
    Reads SHP-002 temperature log
    Detects: 2 excursions (9.2°C and 8.5°C vs. 8°C max)
    Max deviation: 1.2°C
    Severity: WARNING (2 excursions, deviation > 1.0°C threshold)

Step 5 — ROUTE RECOMMENDATION (route_advisor.py)
    Route: ROUTE-EU-INDIA-01
    Cargo: pharmaceuticals
    Active disruption: DISR-002
    Alternatives that avoid DISR-002 and accept pharmaceuticals:
      → ROUTE-EU-INDIA-SOUTH-01: Cape of Good Hope, +6 days, +$14,000
      → ROUTE-EU-INDIA-ALT-AIR:  Emergency air, -4 days, +$95,000

Step 6 — FLEET CHECK (fleet_optimizer.py)
    Needs: reefer capability (requires_cold_chain=true), pharmaceuticals
    V-003 (MV Nordic Frost): 300 reefer slots available — MATCH (already on route)
    V-007 (MV Rhine Express): 200 reefer slots, supports pharmaceuticals — backup option

Step 7 — AI EXPLANATION (watsonx_client.py)
    Structured context → IBM Granite → natural-language advisory for coordinator

Step 8 — MCP EXPOSURE (mcp_server.py)
    All of the above is callable by IBM Bob through 7 standardised tools
```

**Total time: milliseconds.**

---

## 7. Algorithms and Logic — Deep Dive

### 7.1 Risk Scoring — Why These Weights?

The weight allocation is a **transparent business-rule prioritisation**, not an opaque ML model. Each weight has a logical justification:

- **Disruption severity (35%):** The external shock is the primary driver of operational risk. A CRITICAL disruption immediately demands attention regardless of other factors.
- **Delay (25%):** Accumulated delay directly measures how much the disruption has already affected the shipment's operational timeline.
- **Deadline pressure (20%):** A shipment due tomorrow with a 3-day delay is categorically more urgent than one due in 90 days with the same delay.
- **Priority (15%):** Business-determined cargo priority (pharmaceutical > electronics > general) reflects the cost of failure.
- **Cold chain (5%):** A small but decisive signal — cold-chain excursion converts an otherwise manageable situation into an immediate safety/compliance issue.

The non-linear delay scale reflects diminishing returns: the difference between 0 and 2 days of delay is operationally significant, while the difference between 13 and 25 days is much less so (the shipment is already in crisis).

### 7.2 Disruption Propagation — Entity Graph

The five-rule matching system is conceptually an **entity relationship graph**:

```
DISRUPTION ──affects──▶ PORT ◀──origin/dest── SHIPMENT
DISRUPTION ──affects──▶ ROUTE ◀──route_id── SHIPMENT
DISRUPTION ──affects──▶ CARRIER ◀──carrier── SHIPMENT
DISRUPTION ──affects──▶ VESSEL ◀──vessel_id── SHIPMENT
DISRUPTION ──affects──▶ SHIPMENT (direct link)
```

Any path from DISRUPTION to SHIPMENT through this graph constitutes an impact relationship. This is the same conceptual model used in enterprise control towers, and it can scale through indexed lookups (e.g., `port_index["INBOM"] → [SHP-002, SHP-XXX]`) rather than O(n×m) scanning.

### 7.3 Cold-Chain Scoring — Two-Dimensional Classification

The classification uses both **frequency** and **magnitude** because pharmaceutical and food-safety regulations consider both:

```
max_deviation = max(reading - temp_max, 0) for excursions above limit
              + max(temp_min - reading, 0) for excursions below limit

CRITICAL if: excursion_count >= 3 OR max_deviation > WARNING_DELTA_C (1.0°C)
WARNING  if: excursion_count in [1,2] AND max_deviation <= WARNING_DELTA_C
NORMAL   if: excursion_count == 0
```

**Cold-chain risk score (0–100):**
```
base_score = min(excursion_count * 20, 60)     # up to 60 pts from frequency
dev_score  = min(max_deviation * 20, 40)        # up to 40 pts from magnitude
cold_risk  = base_score + dev_score             # capped at 100
```

### 7.4 Fleet Matching — Constraint Satisfaction

The fleet optimizer is a **constraint satisfaction and ranking problem**:

```
HARD CONSTRAINTS (must all pass):
  vehicle.status == "available"
  vehicle.available_teu >= 1
  vehicle.available_weight_kg >= shipment.weight_kg
  cargo_type ∈ vehicle.supported_cargo_types
  if requires_cold_chain: vehicle.available_reefer_slots >= 1

SOFT RANKING (among feasible candidates):
  if cold_chain: sort by (available_reefer_slots DESC, available_teu DESC)
  else:          sort by (available_teu DESC)
```

**Critical insight:** TEU and weight are independent constraints. A vessel with 500 available TEU may still be ineligible if the shipment weighs more than `available_weight_kg`. Both must be satisfied.

---

## 8. IBM Bob and MCP — The Conversational Layer

### 8.1 Why MCP?

Model Context Protocol is a standardised client-server protocol designed for **AI agent ↔ tool** communication. It differs from REST:

| | REST API | MCP |
|---|---|---|
| Designed for | App-to-app integration | Agent-to-tool invocation |
| Discoverability | Manual documentation | Built-in tool listing |
| Target consumer | Application code | AI agent / LLM |
| Protocol | HTTP | stdio / SSE |

MCP allows IBM Bob to **discover** SmartRoute's capabilities at runtime and **invoke** them as tools while reasoning in natural language. Bob doesn't need to understand Python code — it only needs tool schemas.

### 8.2 The Seven Tools — Derived from the Problem Statement

Every MCP tool maps directly to a challenge requirement:

| Tool | Maps to Requirement | Example Invocation |
|---|---|---|
| `get_shipment_risk` | Risk/severity assessment | "How risky is SHP-002?" |
| `get_shipment_disruptions` | Disruption identification | "What is disrupting SHP-006?" |
| `recommend_route` | Re-routing recommendation | "What alternative routes exist for SHP-002?" |
| `recommend_vehicle` | Carrier/vessel alternative | "Which vessel can replace the disabled MV Eastern Star?" |
| `get_fleet_status` | Idle fleet identification | "How much idle capacity does the fleet have?" |
| `get_temperature_alerts` | Cold-chain monitoring | "Are there any temperature excursions right now?" |
| `explain_shipment` | AI explanation | "Explain SHP-002's situation in plain English" |

**Design principle:** Tools are **atomic and composable**. Bob can invoke them individually or combine results across multiple calls to answer complex questions. A monolithic "solve everything" tool would reduce transparency and make agent reasoning opaque.

### 8.3 A Complete Bob Interaction Flow

Operator asks Bob: *"Which shipments are critical right now, and what should we do about them?"*

```
Bob invokes: get_shipment_risk("SHP-001") → score=68, HIGH
Bob invokes: get_shipment_risk("SHP-002") → score=87, CRITICAL ← prioritised
Bob invokes: get_shipment_risk("SHP-006") → score=82, CRITICAL ← prioritised
Bob invokes: recommend_route("SHP-002") → Cape of Good Hope (+$14K) or air (-4 days, +$95K)
Bob invokes: get_temperature_alerts("SHP-002") → WARNING, 2 excursions, 9.2°C peak
Bob invokes: recommend_vehicle("SHP-002") → V-007 Rhine Express, 200 reefer slots
Bob invokes: explain_shipment("SHP-002") → [Granite LLM response]

Bob responds:
"Two shipments require immediate intervention:

SHP-002 (pharmaceutical vaccines, Hamburg → Mumbai): Risk 87/100 — CRITICAL.
The vessel is on the cyclone-affected route with a deadline in 2 days. There are
active temperature excursions (peak 9.2°C vs. 8°C limit). Recommended options:
Cape of Good Hope diversion (+6 days, +$14K) or emergency air freight (-4 days, +$95K).
MV Rhine Express has 200 reefer slots available as backup vessel.

SHP-006 (textiles, Dhaka → New York): Risk 82/100 — CRITICAL.
16-day delay due to vessel engine failure and Shanghai congestion..."
```

This is the difference between a dashboard an operator must manually explore and a **conversational decision partner**.

### 8.4 AI Architecture — Three Layers

```
Layer 1 — Algorithmic Intelligence (deterministic, auditable)
    Disruption correlation · Risk scoring · Route filtering
    Fleet constraint matching · Cold-chain excursion detection

Layer 2 — Generative Intelligence (explanatory, grounded)
    IBM Granite via watsonx.ai
    Input: structured operational facts from Layer 1
    Output: natural-language advisory for operators

Layer 3 — Agentic Intelligence (orchestration, conversational)
    IBM Bob via MCP
    Selects and invokes Layer 1 tools based on operator queries
    Synthesises multi-tool results into coherent responses
```

**Why this separation is critical:** The risk of giving an LLM direct authority over logistics calculations is hallucination. If Granite invents a risk score or a route, the operator may act on fiction. By having Layer 1 establish facts and Layer 2 only explain them, hallucination scope is dramatically reduced — the LLM cannot invent what it is given as verified structured data.

---

## 9. How SmartRoute Differs from Traditional Approaches

### 9.1 The Core Comparison

| Dimension | Traditional Workflow | Visibility Platform | Enterprise Control Tower | SmartRoute AI |
|---|---|---|---|---|
| **Disruption → affected shipments** | Manual, hours | Alert-based, partially automated | Advanced, automated | Multi-entity correlation, instant |
| **Risk prioritisation** | Human judgment, inconsistent | Analytics/predictive | AI-assisted | Deterministic, explainable, auditable |
| **Route alternative evaluation** | Phone calls to carriers | Rarely integrated | Available in advanced versions | Instant, constraint-filtered, trade-off presented |
| **Fleet idle asset detection** | Manual asset register check | Not standard | Available in some | Automatic, constraint-matched |
| **Cold-chain + disruption integration** | Completely separate systems | Separate in most platforms | Sometimes integrated | Single risk score combines both |
| **Natural language interaction** | Not available | Rare | Increasingly available | IBM Bob + MCP (7 tools) |
| **Explanation of decisions** | None | Limited | Available in some | IBM Granite — grounded explanation |
| **Response time (event → decision)** | 2–6 hours | Faster, but manual synthesis | Minutes to hours | Seconds |
| **Data requirements** | Fragmented systems | Carrier API integrations | Full ERP/TMS integration | Structured JSON (prototype), streaming feeds (production) |
| **Cost of deployment** | Low (spreadsheets) | High (carrier network subscriptions) | Very high (enterprise platform) | Modular Python (prototype), scalable to cloud |
| **Customisability of logic** | Total (manual) | Low | Medium (configuration) | High (open Python engines) |
| **Agent accessibility (Bob/AI)** | None | None | Rare, proprietary | Built-in via MCP |

### 9.2 The Structural Difference

**Traditional approach:** Siloed tools, human synthesis, reactive responses.

```
[Visibility Tool] → human → [TMS] → human → [Fleet System] → human → [Cold Chain] → DECISION
     (each requires separate login, context switch, and manual data correlation)
```

**SmartRoute approach:** Unified decision pipeline, algorithmic synthesis, proactive intelligence.

```
[One Event] → [Correlation] → [Risk] → [Routes+Fleet+ColdChain] → [Explanation] → DECISION
              (all automated, all interconnected, all accessible via one interface)
```

### 9.3 Why Deterministic Beats ML for This Use Case

Enterprise control towers increasingly use machine learning for predictive ETAs and risk forecasting. SmartRoute uses deterministic logic for a specific reason:

**In logistics operations, decisions must be defensible.** When an operations manager asks "why did the system flag SHP-002 as critical?", the answer must be:
- Specific (not "the model predicted 87%")
- Auditable (the same inputs always produce the same output)
- Explainable (each factor's contribution is visible)

SmartRoute's factor breakdown:
```
35 (critical cyclone) + 0 (no delay) + 18 (2-day deadline) + 15 (critical priority) + 3 (temp warning) = 71/100
```

This is fully auditable. An ML model that outputs 71% provides none of this transparency.

*Note: In production, historical calibration and ML-assisted prediction can **supplement** (not replace) this deterministic foundation.*

### 9.4 The IBM Bob Differentiator

No commercial supply-chain platform today natively exposes its core decision logic as **standardised MCP tools consumable by IBM Bob**. This is not a minor integration feature — it represents a fundamental architectural choice:

**Without MCP:** The supply-chain system is a walled garden. Operators must use its specific UI. AI agents cannot query it programmatically.

**With MCP:** The supply-chain decision layer becomes a **first-class tool set** that any MCP-compatible AI agent can discover and invoke. IBM Bob can ask questions in natural language, invoke the relevant tools, synthesise results, and explain trade-offs — all without the operator needing to navigate multiple dashboards.

This is the difference between a tool and a **conversational decision partner**.

---

## 10. Impact Model

### 10.1 The Core Value Chain

```
EARLIER DETECTION
       ↓
FASTER IMPACT ASSESSMENT (seconds vs. hours)
       ↓
MORE OPTIONS AVAILABLE (time allows non-emergency choices)
       ↓
LOWER REACTIVE COST (planned reroute vs. emergency freight)
       ↓
LOWER DELAY (proactive mitigation vs. reactive recovery)
       ↓
BETTER ASSET UTILISATION (idle capacity identified and deployed)
       ↓
LESS CARGO LOSS (cold-chain detected before delivery)
       ↓
BETTER CUSTOMER SERVICE (deadlines met, cargo integrity maintained)
```

### 10.2 Quantified Impact Scenarios

**Scenario A — Pharmaceutical cold-chain breach (SHP-002):**

| Without SmartRoute | With SmartRoute |
|---|---|
| Temperature excursion detected at delivery (Mumbai) | Excursion detected at Gibraltar (in transit) |
| $2.2M pharmaceutical cargo rejected | Early intervention possible (reefer reset triggered) |
| Emergency reorder required | Cargo arrives within spec |
| Patient impact possible | Risk mitigated |

**Scenario B — Vessel engine failure (SHP-006, MV Eastern Star):**

| Without SmartRoute | With SmartRoute |
|---|---|
| 16-day delay discovered gradually | Impact immediately correlated to all affected shipments |
| Manual carrier outreach (hours) | Alternative vessel V-001/V-006 identified in seconds |
| Emergency freight at premium rates | Planned transhipment at Singapore — controlled cost |

**Scenario C — Port strike (DISR-003, Rotterdam):**

| Without SmartRoute | With SmartRoute |
|---|---|
| SHP-004 (fresh produce) continues toward closed port | Immediately identified as affected |
| Cargo spoils after 8-day delay | Antwerp alternative (+2 days, +$5,200) activated |
| $95,000 produce lost | $95,000 cargo protected at $5,200 marginal cost |

### 10.3 Business KPIs to Track

| Category | Metric | Direction |
|---|---|---|
| Response time | Mean time from disruption event to affected shipment identification | ↓ |
| Response time | Mean time from disruption event to actionable decision | ↓ |
| Shipments | Percentage of disrupted shipments successfully mitigated | ↑ |
| Shipments | Average delay days across affected shipments | ↓ |
| Fleet | Fleet idle asset utilisation rate | ↑ |
| Fleet | Idle vessel hours per month | ↓ |
| Cold chain | Temperature excursions detected in transit vs. at delivery | ↑ in-transit |
| Cold chain | Cold-chain cargo rejection rate | ↓ |
| Financial | Cost avoided through proactive mitigation vs. reactive recovery | ↑ |
| Financial | Emergency freight spend as percentage of total freight cost | ↓ |
| AI | MCP tool invocation success rate | ↑ |
| AI | Operator recommendation acceptance rate | ↑ |

### 10.4 The Central Performance Metric

If one metric captures the entire value proposition:

> **Time-to-Actionable-Decision** — the elapsed time between an external disruption event and the point at which the operator has (a) the complete list of affected shipments, (b) their risk ranking, and (c) at least one feasible mitigation option.

Traditional: **2–6 hours**
SmartRoute: **< 60 seconds**

---

## 11. Current Prototype vs Production Roadmap

### 11.1 What the Current Prototype Is

```
Current prototype = a real-time-ready decision architecture
                    demonstrated with simulated operational data
```

The current implementation does NOT have:
- Live AIS/vessel tracking feeds
- Real-time weather/port APIs
- MQTT/Kafka streaming pipeline
- Live carrier integrations
- A production database
- Autonomous execution tools

What it DOES have:
- Complete decision pipeline (detect → correlate → risk → route → fleet → cold-chain)
- Transparent, auditable deterministic risk engine
- Multi-entity disruption correlation (5 rules)
- Constraint-based fleet matching
- Two-dimensional cold-chain excursion classification
- IBM Bob MCP integration (7 tools)
- IBM Granite AI explanation layer
- 191 unit tests covering all engines and tools

### 11.2 Production Evolution Phases

**Phase 1 — Current Prototype (complete)**
```
JSON datasets → Python engines → Streamlit + MCP → IBM Bob
```

**Phase 2 — Live Data Integration**
```
AIS (Spire/MarineTraffic)     ┐
Weather APIs (NOAA/Copernicus)│
Port feeds (port authorities) ├──► Kafka/MQTT ──► PostgreSQL/TimescaleDB
Carrier APIs                  │
IoT temperature sensors       ┘
```
Same decision engines, live data sources.

**Phase 3 — Predictive Intelligence**
```
Historical shipment outcomes → ML models for:
  - ETA prediction with confidence intervals
  - Delay probability by route/carrier/season
  - Cold-chain failure probability by cargo/route/temperature
  - Disruption impact prediction (which shipments will be affected)
```

**Phase 4 — Dynamic Network Optimisation**
```
Global port graph (ports = nodes, corridors = weighted edges)
↓
Multi-objective route optimiser:
  minimise(α×cost + β×delay + γ×risk + δ×emissions)
  subject to: capacity, reefer, cargo_type, deadlines, port_restrictions
↓
True real-time global routing (not predefined alternatives)
```

**Phase 5 — Controlled Autonomous Execution**
```
Bob recommends → Human approves → System executes:
  - Submit reroute request to carrier API
  - Reserve alternative vessel capacity
  - Alert consignee of revised ETA
  - Trigger emergency air freight booking
  - Adjust reefer setpoint via IoT command
  ↓
Outcome monitoring and feedback loop
```

### 11.3 The Production Architecture

```
                     ┌───────────────────────┐
                     │  EXTERNAL DATA LAYER  │
                     │ AIS · Weather · Ports │
                     │ Carriers · IoT · GPS  │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ EVENT BUS & STREAMING │
                     │   Kafka / MQTT        │
                     └───────────┬───────────┘
                                 │
                                 ▼
                 ┌──────────────────────────────┐
                 │   DATA PLATFORM              │
                 │ PostgreSQL + TimescaleDB      │
                 │ (shipments, events, telemetry)│
                 └──────────────┬───────────────┘
                                │
                 ┌──────────────▼───────────────┐
                 │       DECISION ENGINE        │
                 │  (same Python modules,       │
                 │   live data, Celery workers) │
                 └──────────────┬───────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       ┌──────────────────┐           ┌─────────────────┐
       │ CONTROL TOWER    │           │  MCP TOOL LAYER │
       │   (Streamlit /   │           │  (7+ tools)     │
       │    React in prod)│           └────────┬────────┘
       └──────────────────┘                    │
                                               ▼
                                       ┌─────────────────┐
                                       │   IBM BOB       │
                                       │   AI AGENT      │
                                       └────────┬────────┘
                                                │
                                                ▼
                                         HUMAN OPERATOR
                                                │
                                                ▼
                                    HUMAN APPROVAL + EXECUTION
```

---

## 12. Jury Defense Reference

### 12.1 The One-Sentence Answer

> *"SmartRoute transforms supply-chain events into prioritised decisions: it detects what is affected, quantifies impact, evaluates what can be changed, identifies available resources, and lets the operator interact with those decisions conversationally through IBM Bob."*

### 12.2 The Core Architectural Principle

> *"Deterministic engines establish operational facts; IBM Granite explains those facts; IBM Bob orchestrates the conversation."*

### 12.3 Common Counter-Arguments and Responses

**"Your data is static — it's not real-time."**
> Correct for the prototype. The decision engines are independent of the data source. We separated ingestion from logic so live AIS, weather, carrier, and IoT feeds can replace JSON without redesigning any engine. The prototype is a real-time-ready decision architecture demonstrated with simulated operational data.

**"This is just a dashboard with if-else conditions."**
> The disruption detector implements multi-entity relationship propagation across five dimensions. The risk engine applies a non-linear, deadline-aware, multi-factor weighted model. The fleet optimizer is a constraint satisfaction problem. The cold-chain monitor uses two-dimensional severity classification. And all of this is exposed through IBM Bob via MCP as an agentic decision layer. The simplicity of individual rules is a feature — it makes every decision auditable.

**"Why not use machine learning for risk scoring?"**
> In logistics operations, risk decisions must be reproducible and auditable. A deterministic model scores SHP-002 at 71/100 for the same reasons every time — that explanation can be given to an operations manager, a customer, or a regulator. An ML model that outputs "71%" without factor decomposition cannot. ML supplements this foundation in Phase 3 for prediction; it doesn't replace the deterministic scoring layer.

**"FourKites and project44 already do this."**
> Those platforms demonstrate that the capabilities are commercially validated. SmartRoute's contribution is demonstrating a focused, modular, open decision architecture where every engine is independently testable, every factor is explainable, and the entire capability set is natively accessible to IBM Bob through MCP — something no commercial platform currently provides.

**"Can Bob automatically reroute the shipment?"**
> Currently, no — by design. SmartRoute is decision support, not autonomous authority. Rerouting a $2.2M pharmaceutical shipment is a decision that must remain human-approved. Phase 5 of the roadmap adds controlled execution tools with explicit approval workflows. Starting with recommendation-only reduces operational risk and builds operator trust.

**"Your temperature classification is not regulatory compliant."**
> Correct — it is configurable operational severity classification. The thresholds (2–8°C, WARNING_DELTA_C=1.0°C) represent standard pharmaceutical guidelines but are not validated against a specific regulatory jurisdiction or product stability profile. In production, these would be mapped to product-specific stability data and applicable GDP/GMP regulations.

**"Where is the innovation?"**
> The innovation is the integration architecture: one disruption event propagates through entity relationships to affected shipments, through risk scoring to prioritisation, through constraint-based filtering to feasible options, through cold-chain analysis to cargo integrity status, and through MCP to IBM Bob as a conversational decision interface — all in one deterministic, explainable, agent-accessible pipeline. No single component is novel in isolation; the system's value is the connected whole.

### 12.4 The 90-Second Explanation

> "SmartRoute is a supply-chain control tower. It starts with four data sources: shipments, disruptions, fleet assets, and temperature sensors. When a disruption occurs — a cyclone, a port strike, a vessel failure — our disruption detector correlates it against shipments using five relationship types: explicit links, route, carrier, port, and vessel. This transforms one event into a ranked list of all exposed shipments.
>
> The risk engine then scores each shipment from 0–100 using disruption severity, delay, deadline pressure, cargo priority, and cold-chain status. For critical shipments, the route advisor evaluates feasible alternatives with their cost and delay trade-offs, the fleet optimizer identifies available vessels that meet capacity and reefer requirements, and the cold-chain monitor checks whether temperature-sensitive cargo has experienced excursions.
>
> All of this happens in milliseconds instead of hours.
>
> IBM Granite through watsonx.ai converts the structured results into natural-language advisories. And through seven MCP tools, IBM Bob can access the entire capability set conversationally — so an operator can ask 'which shipments need immediate intervention?' and get a complete, prioritised answer.
>
> The prototype uses simulated datasets. The production architecture replaces that data layer with AIS, weather, carrier, and IoT streams through Kafka and PostgreSQL without changing the decision engines."

---

*SmartRoute AI — Team PI-NANT · CHARUSAT University · IBM Bob AI Hackathon 2026*
