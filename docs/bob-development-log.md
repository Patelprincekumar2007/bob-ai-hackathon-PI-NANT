# IBM Bob Development Log

## SmartRoute AI — PI-NANT Team
### IBM Bob AI Innovation Hackathon 2026 · Track: AI

---

## Overview

This log documents how IBM Bob was used as an SDLC partner throughout the SmartRoute AI project, from initial brainstorming through code review and live demonstration preparation.

---

## Development Sessions

### Session 1 — Architecture Design

**Bob usage:** Used IBM Bob to sanity-check the proposed modular architecture (5 core modules + MCP server + Streamlit UI) against the official problem statement (Supply Chain Disruption Assistant & Fleet Utilisation Optimizer).

**Outcome:** Bob confirmed the separation of concerns was sound and suggested enriching the watsonx.ai prompt with factor-level breakdown data, not just the final score — which was incorporated into the final `build_watsonx_prompt()` implementation.

**MCP tools called:**
- `explain_shipment` — used to verify that the mock fallback produced coherent output without live credentials.

---

### Session 2 — Risk Engine Validation

**Bob usage:** Asked Bob to review the five-factor risk scoring model weights (35/25/20/15/5) and confirm they were defensible for a maritime supply chain context.

**Bob's feedback:** Bob noted that the model correctly prioritises operational disruptions (35 pts) and current delay (25 pts) over static factors like priority level (15 pts), which is consistent with real-world logistics triage practice.

**MCP tools called:**
- `get_shipment_risk("SHP-006")` — confirmed score of 87/100 (CRITICAL) for the dual-disruption textiles shipment.
- `get_shipment_disruptions("SHP-006")` — verified both DISR-001 (Shanghai port congestion) and DISR-004 (vessel mechanical failure) were matched.

---

### Session 3 — Decision Engine Review

**Bob usage:** Presented the proposed decision engine recommended-action rules to Bob for review. Asked: "Are these rules operationally correct for a maritime logistics context?"

**Bob's feedback:** Bob validated the escalation threshold (HIGH + delay >= 10 days) and confirmed that CRITICAL + no alternatives → Escalate (not Reroute) was the correct decision boundary. Bob also suggested that the cold-chain "Why does this matter?" explanation would help non-specialist coordinators understand the urgency.

**Changes made based on Bob's review:**
- Added explicit "Why does this matter?" narrative to the cold-chain UI section.
- Added `match_reason` display in the Active Disruptions section so the coordinator can understand *why* a disruption was matched to their shipment.

**MCP tools called:**
- `get_temperature_alerts()` — reviewed cold-chain alerts for SHP-002 and SHP-004.
- `explain_shipment("SHP-002")` — verified that the enriched prompt (including cold-chain severity and recommended action) was reflected in the mock AI response.

---

### Session 4 — MCP Tool Testing with IBM Bob

**Bob usage:** Connected Bob to the local MCP server (`python src/mcp_server.py`) and ran a live end-to-end test session.

**Sample queries issued to Bob:**

| Query | Tools called | Result |
|---|---|---|
| "Which shipments are at critical risk?" | `get_shipment_risk` × 7 | SHP-006 (87), SHP-004 (81) returned |
| "What should I do about SHP-006?" | `explain_shipment("SHP-006")` | Recommended: Reroute + Escalate (IMMEDIATE) |
| "Is any cold-chain cargo at risk?" | `get_temperature_alerts()` | SHP-002 WARNING excursion returned |
| "What vessels are available?" | `get_fleet_status()` | 5 available, 75% utilisation |
| "Find the best ship for SHP-004" | `recommend_vehicle("SHP-004")` | MSC Adriana (reefer-capable) recommended |

**Outcome:** All seven tools responded correctly. Bob was able to chain tool calls naturally (e.g., get risk → get disruptions → recommend route) without manual prompting.

---

### Session 5 — Documentation Review

**Bob usage:** Asked Bob to review the README and solution-overview.md for clarity. Bob flagged that the original description of the AI role was misleading — it implied the LLM was calculating risk, when in fact the deterministic engine calculates risk and the LLM only explains the result.

**Changes made:**
- Clarified in all documentation that "IBM watsonx.ai (Granite LLM) explains the result in plain English — it does not replace the deterministic engine."
- Added this clarification to the AI explanation section in the Streamlit UI.

---

### Session 6 — Final Readiness Check

**Bob usage:** Final pre-submission walkthrough. Asked Bob: "Is the system ready to demonstrate the official problem statement — Supply Chain Disruption Assistant & Fleet Utilisation Optimizer?"

**Bob's assessment:**
- Disruption detection: ✅ 5-rule matching engine with match reason displayed
- Risk scoring: ✅ 5-factor deterministic model, fully tested (262 tests, 100% passing)
- Route alternatives: ✅ 6 pre-defined routes with delay/cost/disruption-avoidance data
- Fleet optimisation: ✅ Vehicle recommendation with reefer filtering and utilisation metrics
- Cold-chain monitoring: ✅ Excursion detection, severity classification, "Why does this matter?" explanation
- Decision engine: ✅ Deterministic action rules, escalation logic, structured result
- IBM watsonx.ai: ✅ Real integration + clearly-labelled mock fallback
- IBM Bob MCP server: ✅ 7 tools, all tested for consistency with core engine

**Bob's suggestion for demo:** Start with SHP-006 (CRITICAL, 16-day delay, two disruptions) to show the escalation banner and reroute recommendation, then switch to SHP-002 (CRITICAL pharma, Arabian Sea cyclone, temperature monitoring) to show the cold-chain workflow.

---

## Summary

IBM Bob was used at every stage of the SDLC:

| Phase | Bob's role |
|---|---|
| Design | Validated architecture, module separation, and risk factor weights |
| Development | Reviewed decision engine rules and escalation thresholds |
| Testing | Ran live MCP tool sessions; verified end-to-end decision workflow |
| Documentation | Reviewed README and solution overview for accuracy and clarity |
| Demo prep | Identified the highest-impact demo scenarios |

IBM Bob's MCP integration was central to the project: it was both a **development tool** (used to validate the system during build) and a **product feature** (IBM Bob can answer supply chain questions by calling SmartRoute AI tools in production).
