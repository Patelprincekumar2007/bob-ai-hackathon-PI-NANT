"""
app.py — SmartRoute AI Streamlit Dashboard
===========================================
Five-page supply chain control tower.

Run: streamlit run src/app.py

Pages
-----
1. Dashboard   — fleet-wide KPI cards
2. Shipments   — risk-scored table + per-shipment detail view
3. Disruptions — active disruption table
4. Fleet       — fleet KPIs, per-vehicle utilisation, vehicle picker
5. Cold Chain  — temperature alerts, excursion history chart

All data comes from the core/ modules — nothing is hardcoded.
"""

import os
import sys

# ---------------------------------------------------------------------------
# Path fix: make `core/` importable when running as "streamlit run src/app.py"
# from any working directory.
# ---------------------------------------------------------------------------
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import streamlit as st

# Core imports — absolute imports using sys.path fix above
from core.disruption_detector import (
    load_disruptions,
    load_shipments,
    get_disruption_summary,
    get_shipment_disruptions,
)
from core.risk_engine import get_risk_summary, score_all_shipments, calculate_risk_by_id
from core.route_advisor import recommend_alternative_routes
from core.fleet_optimizer import (
    get_fleet_summary,
    get_vehicle_utilisation,
    recommend_vehicle_for_shipment,
)
from core.cold_chain_monitor import (
    get_cold_chain_summary,
    get_temperature_alerts,
    get_shipment_temperature_status,
)
from core.watsonx_client import generate_ai_explanation, is_watsonx_configured

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
RISK_COLORS = {
    "CRITICAL": "#e53e3e",   # red
    "HIGH":     "#dd6b20",   # orange
    "MEDIUM":   "#d69e2e",   # yellow/amber
    "LOW":      "#38a169",   # green
}

SEV_COLORS = {
    "critical": "#e53e3e",
    "high":     "#dd6b20",
    "medium":   "#d69e2e",
    "low":      "#38a169",
    "CRITICAL": "#e53e3e",
    "HIGH":     "#dd6b20",
    "MEDIUM":   "#d69e2e",
    "LOW":      "#38a169",
    "WARNING":  "#dd6b20",
    "NORMAL":   "#38a169",
}


def _badge(label, color):
    """Return an HTML colored badge span."""
    return (
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:4px;font-size:0.8em;font-weight:bold">{label}</span>'
    )


def _risk_badge(level):
    return _badge(level, RISK_COLORS.get(level, "#718096"))


# ---------------------------------------------------------------------------
# Cached data helpers (all pure functions, no st.* calls)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30)
def cached_shipments():
    """All shipment records from shipments.json."""
    return load_shipments()


@st.cache_data(ttl=30)
def cached_disruptions():
    """All disruption records from disruptions.json."""
    return load_disruptions()


@st.cache_data(ttl=30)
def cached_scored_shipments():
    """All shipments with risk scores, sorted highest first."""
    return score_all_shipments()


@st.cache_data(ttl=30)
def cached_risk_summary():
    return get_risk_summary()


@st.cache_data(ttl=30)
def cached_disruption_summary():
    return get_disruption_summary()


@st.cache_data(ttl=30)
def cached_fleet_summary():
    return get_fleet_summary()


@st.cache_data(ttl=30)
def cached_vehicle_utilisation():
    return get_vehicle_utilisation()


@st.cache_data(ttl=30)
def cached_cold_chain_summary():
    return get_cold_chain_summary()


@st.cache_data(ttl=30)
def cached_temperature_alerts():
    return get_temperature_alerts()


def get_shipment_detail(shipment_id):
    """Aggregate all detail data for one shipment (not cached — changes with selection)."""
    risk = calculate_risk_by_id(shipment_id)
    disruptions = get_shipment_disruptions(shipment_id)
    routes = recommend_alternative_routes(shipment_id)
    vehicle = recommend_vehicle_for_shipment(shipment_id)
    # Find raw shipment record for requires_cold_chain check
    raw = next((s for s in load_shipments() if s["id"] == shipment_id), None)
    cold = None
    if raw and raw.get("requires_cold_chain"):
        cold = get_shipment_temperature_status(shipment_id)
    return {
        "risk": risk,
        "disruptions": disruptions,
        "routes": routes,
        "vehicle": vehicle,
        "cold": cold,
        "raw": raw,
    }


def filter_scored_shipments(scored, risk_filter, status_filter, priority_filter):
    """Filter a list of scored shipment dicts based on UI selections."""
    out = scored
    if risk_filter and risk_filter != "All":
        out = [s for s in out if s["classification"] == risk_filter]
    if status_filter and status_filter != "All":
        out = [s for s in out if s.get("status", "").lower() == status_filter.lower()]
    if priority_filter and priority_filter != "All":
        out = [s for s in out if s.get("priority", "").lower() == priority_filter.lower()]
    return out


def build_ai_prompt(shipment_id, risk_data, disruptions):
    """Build a concise watsonx prompt for a shipment."""
    risk_cls = risk_data.get("classification", "UNKNOWN") if risk_data else "UNKNOWN"
    risk_score = risk_data.get("score", 0) if risk_data else 0
    disr_titles = "; ".join(d["title"] for d in disruptions) if disruptions else "None"
    return (
        f"You are a supply chain risk analyst. "
        f"Shipment {shipment_id} has a risk score of {risk_score}/100 ({risk_cls}). "
        f"Active disruptions: {disr_titles}. "
        f"Provide a brief, actionable explanation for a logistics coordinator: "
        f"what is happening, why it matters, and what they should do next."
    )


# ---------------------------------------------------------------------------
# Page renderers (all st.* calls live here)
# ---------------------------------------------------------------------------

def page_dashboard():
    st.title("SmartRoute AI — Supply Chain Control Tower")
    st.markdown("Real-time shipment risk scoring, disruption detection, and fleet optimisation.")

    risk = cached_risk_summary()
    disr = cached_disruption_summary()
    fleet = cached_fleet_summary()
    cold = cached_cold_chain_summary()

    st.subheader("Fleet Overview")
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("Total Shipments",   risk["total_shipments"])
    c2.metric("At-Risk Shipments", disr["total_affected_shipments"])
    c3.metric("Critical Risk",     risk["critical_count"])
    c4.metric("Active Disruptions", disr["total_active_disruptions"])
    c5.metric("Available Vehicles", fleet["available"])
    c6.metric("Fleet Utilisation",  f"{fleet['utilisation_pct']}%")
    c7.metric("Cold-Chain Alerts",  cold["shipments_with_excursions"])

    st.divider()
    st.subheader("Risk Breakdown")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("CRITICAL", risk["critical_count"], help="Score 75-100")
    r2.metric("HIGH",     risk["high_count"],     help="Score 50-74")
    r3.metric("MEDIUM",   risk["medium_count"],   help="Score 25-49")
    r4.metric("LOW",      risk["low_count"],      help="Score 0-24")

    st.divider()
    st.subheader("Top At-Risk Shipments")
    scored = cached_scored_shipments()
    top = [s for s in scored if s["classification"] in ("CRITICAL", "HIGH")][:5]
    if not top:
        st.info("No CRITICAL or HIGH risk shipments at this time.")
    else:
        import pandas as pd
        rows = []
        for s in top:
            color = RISK_COLORS.get(s["classification"], "#718096")
            rows.append({
                "ID":           s["shipment_id"],
                "Description":  s["description"],
                "Risk Score":   s["score"],
                "Risk Level":   s["classification"],
                "Status":       s.get("status", ""),
                "Delay (days)": s.get("delay_days", 0),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)


def page_shipments():
    st.title("Shipments")
    scored = cached_scored_shipments()

    # Filters
    st.sidebar.subheader("Filters")
    risk_levels  = ["All"] + ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    statuses     = ["All"] + sorted({s.get("status", "") for s in scored if s.get("status")})
    priorities   = ["All"] + sorted({s.get("priority", "") for s in scored if s.get("priority")})

    risk_filter     = st.sidebar.selectbox("Risk Level",  risk_levels,  key="filter_risk")
    status_filter   = st.sidebar.selectbox("Status",      statuses,     key="filter_status")
    priority_filter = st.sidebar.selectbox("Priority",    priorities,   key="filter_priority")

    filtered = filter_scored_shipments(scored, risk_filter, status_filter, priority_filter)

    st.subheader(f"All Shipments ({len(filtered)} shown)")
    if not filtered:
        st.warning("No shipments match the selected filters.")
        return

    import pandas as pd
    rows = []
    for s in filtered:
        disr_count = len(s.get("disruptions", []))
        rows.append({
            "ID":             s["shipment_id"],
            "Description":    s["description"],
            "Risk Score":     s["score"],
            "Risk Level":     s["classification"],
            "Status":         s.get("status", ""),
            "Priority":       s.get("priority", ""),
            "Delay (days)":   s.get("delay_days", 0),
            "Disruptions":    disr_count,
            "Cold Chain":     "Yes" if s.get("requires_cold_chain") else "No",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Shipment Detail")
    ids = [s["shipment_id"] for s in filtered]
    selected_id = st.selectbox("Select a shipment for detail view", ids, key="sel_shipment")

    if not selected_id:
        return

    detail = get_shipment_detail(selected_id)
    risk   = detail["risk"]
    raw    = detail["raw"]

    if risk is None:
        st.error(f"Could not load risk data for {selected_id}.")
        return

    # Shipment Info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Shipment Info**")
        orig = (raw or {}).get("origin", {})
        dest = (raw or {}).get("destination", {})
        st.write(f"**Carrier:** {(raw or {}).get('carrier', 'N/A')}")
        st.write(f"**Origin:** {orig.get('city','')}, {orig.get('country','')}")
        st.write(f"**Destination:** {dest.get('city','')}, {dest.get('country','')}")
        st.write(f"**Status:** {(raw or {}).get('status', 'N/A')}")
        st.write(f"**Priority:** {(raw or {}).get('priority', 'N/A')}")
        st.write(f"**Cargo Type:** {(raw or {}).get('cargo_type', 'N/A')}")
    with col2:
        st.markdown("**Risk Assessment**")
        risk_color = RISK_COLORS.get(risk["classification"], "#718096")
        st.markdown(
            f"**Score:** {risk['score']}/100 "
            + _risk_badge(risk["classification"]),
            unsafe_allow_html=True,
        )
        fb = risk.get("factor_breakdown", {})
        st.write(f"Disruption severity: {fb.get('disruption_severity', 0)}/35")
        st.write(f"Delay factor:        {fb.get('delay', 0)}/25")
        st.write(f"Deadline pressure:   {fb.get('deadline_pressure', 0)}/20")
        st.write(f"Priority factor:     {fb.get('priority', 0)}/15")
        st.write(f"Cold-chain factor:   {fb.get('cold_chain', 0)}/5")

    # Disruptions
    st.markdown("**Active Disruptions**")
    disrs = detail["disruptions"]
    if not disrs:
        st.success("No active disruptions affecting this shipment.")
    else:
        for d in disrs:
            sev_color = SEV_COLORS.get(d["severity"].upper(), "#718096")
            st.markdown(
                f"{_badge(d['severity'].upper(), sev_color)} "
                f"**{d['title']}** — {d['type']} | "
                f"+{d['estimated_delay_days']}d delay | "
                f"+${d['additional_cost_usd']:,} cost",
                unsafe_allow_html=True,
            )
            st.caption(d["description"])

    # Route alternatives
    st.markdown("**Route Alternatives**")
    routes = detail["routes"]
    alts = routes.get("alternatives", [])
    if not alts:
        if routes.get("action_required"):
            st.warning("No pre-defined alternatives for this route. Contact carrier directly.")
        else:
            st.success("No rerouting required — shipment is on schedule.")
    else:
        for i, alt in enumerate(alts, 1):
            ed = alt["extra_delay_days"]
            delay_str = f"+{ed}d delay" if ed >= 0 else f"{abs(ed)}d faster"
            with st.expander(f"Option {i}: {alt['description']} ({delay_str}, +${alt['extra_cost_usd']:,})"):
                st.write(alt["reason"])
                veh_list = alt.get("available_vehicles", [])
                if veh_list:
                    veh_names = ", ".join(v["name"] for v in veh_list)
                    st.write(f"Available vessels: {veh_names}")
                else:
                    st.write("Arrange vessel with suggested carriers: "
                             + ", ".join(alt.get("suggested_carriers", [])))

    # Vehicle recommendation
    st.markdown("**Vehicle Recommendation**")
    veh_rec = detail["vehicle"]
    best_veh = veh_rec.get("recommended_vehicle")
    if best_veh:
        st.success(veh_rec["reason"])
        alts_v = veh_rec.get("alternatives", [])
        if alts_v:
            st.caption(f"Alternatives: " + ", ".join(v["name"] for v in alts_v))
    else:
        st.warning(veh_rec.get("reason", "No vehicle recommendation available."))

    # Cold chain
    cold = detail["cold"]
    if cold:
        st.markdown("**Cold-Chain Status**")
        sev_color = SEV_COLORS.get(cold["excursion_severity"], "#718096")
        st.markdown(
            _badge(cold["excursion_severity"], sev_color) + f" {cold['explanation']}",
            unsafe_allow_html=True,
        )

    # AI Explanation
    st.divider()
    ai_configured = is_watsonx_configured()
    ai_label = "[AI - watsonx]" if ai_configured else "[Demo Mode - Mock AI]"
    if st.button(f"Generate AI Explanation {ai_label}", key=f"ai_{selected_id}"):
        prompt = build_ai_prompt(selected_id, risk, disrs)
        with st.spinner("Calling watsonx.ai..."):
            result = generate_ai_explanation(prompt)
        source_label = "[AI - watsonx]" if result["source"] == "watsonx" else "[Demo Mode - Mock AI]"
        st.markdown(f"**{source_label}**")
        st.info(result["text"])
        if result.get("error"):
            st.caption(f"Note: {result['error']}")


def page_disruptions():
    st.title("Active Disruptions")
    disruptions = cached_disruptions()
    active = [d for d in disruptions if d.get("status") in ("active", "monitoring")]

    summary = cached_disruption_summary()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Disruptions",   summary["total_active_disruptions"])
    c2.metric("Affected Shipments",   summary["total_affected_shipments"])
    c3.metric("Critical Disruptions", summary["critical_count"])
    c4.metric("High Disruptions",     summary["high_count"])

    st.divider()
    if not active:
        st.success("No active disruptions at this time.")
        return

    import pandas as pd
    rows = []
    for d in active:
        rows.append({
            "ID":              d["id"],
            "Type":            d.get("type", ""),
            "Title":           d.get("title", ""),
            "Severity":        d.get("severity", "").upper(),
            "Status":          d.get("status", ""),
            "Est. Delay (d)":  d.get("estimated_delay_days", 0),
            "Add. Cost ($)":   d.get("additional_cost_usd", 0),
            "Affected Routes": len(d.get("affected_routes", [])),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Disruption Detail")
    disr_ids = [d["id"] for d in active]
    sel_disr = st.selectbox("Select a disruption", disr_ids, key="sel_disruption")
    if sel_disr:
        d = next((x for x in active if x["id"] == sel_disr), None)
        if d:
            sev_color = SEV_COLORS.get(d.get("severity","").upper(), "#718096")
            st.markdown(
                _badge(d.get("severity","").upper(), sev_color) + f" **{d['title']}**",
                unsafe_allow_html=True,
            )
            st.write(d.get("description", ""))
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {d.get('type','')}")
                st.write(f"**Status:** {d.get('status','')}")
                st.write(f"**Estimated delay:** {d.get('estimated_delay_days', 0)} days")
                st.write(f"**Additional cost:** ${d.get('additional_cost_usd', 0):,}")
            with col2:
                st.write(f"**Affected ports:** {', '.join(d.get('affected_ports', []))}")
                st.write(f"**Affected routes:** {', '.join(d.get('affected_routes', []))}")
                st.write(f"**Affected carriers:** {', '.join(d.get('affected_carriers', []))}")
                st.write(f"**Affected vessels:** {', '.join(d.get('affected_vessel_ids', []))}")


def page_fleet():
    st.title("Fleet Management")
    fleet = cached_fleet_summary()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vehicles",    fleet["total"])
    c2.metric("Available",         fleet["available"])
    c3.metric("Assigned",          fleet["assigned"])
    c4.metric("Idle",              fleet["idle"])
    c5.metric("Utilisation",       f"{fleet['utilisation_pct']}%")

    r1, r2, r3 = st.columns(3)
    r1.metric("Reefer-Capable",    fleet["reefer_capable_count"])
    r2.metric("Available TEU",     fleet["available_total_teu"])
    r3.metric("Avail. Weight (kg)", f"{fleet['available_total_weight_kg']:,}")

    st.divider()
    st.subheader("Per-Vehicle Utilisation")
    util = cached_vehicle_utilisation()

    import pandas as pd
    rows = []
    for v in util:
        rows.append({
            "Vehicle ID":    v["vehicle_id"],
            "Name":          v["name"],
            "Carrier":       v["carrier"],
            "Status":        v["status"],
            "Assigned":      "Yes" if v["assigned"] else "No",
            "Idle":          "Yes" if v["is_idle"] else "No",
            "Capacity (TEU)":v["capacity_teu"],
            "Used (TEU)":    v["used_teu"],
            "Available (TEU)":v["available_teu"],
            "Load %":        v["load_pct"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Vehicle Recommendation Picker")
    shipments = cached_shipments()
    shp_ids = [s["id"] for s in shipments]
    sel_shp = st.selectbox("Select a shipment to find the best vehicle", shp_ids, key="fleet_shp")
    if sel_shp:
        rec = recommend_vehicle_for_shipment(sel_shp)
        best = rec.get("recommended_vehicle")
        if best:
            st.success(rec["reason"])
            alts = rec.get("alternatives", [])
            if alts:
                st.markdown("**Alternatives:**")
                for a in alts:
                    st.write(
                        f"- {a['name']} ({a['carrier']}) — "
                        f"{a['available_teu']} TEU, "
                        f"departs {a.get('next_departure','TBD')} from {a['current_location']}"
                    )
        else:
            st.warning(rec.get("reason", "No vehicle found."))


def page_cold_chain():
    st.title("Cold-Chain Monitor")
    summary = cached_cold_chain_summary()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tracked Shipments",    summary["total_tracked"])
    c2.metric("Normal",               summary["normal_count"])
    c3.metric("Warning",              summary["warning_count"])
    c4.metric("Critical Excursions",  summary["critical_count"])

    st.divider()
    st.subheader("Temperature Alerts")
    alerts = cached_temperature_alerts()
    if not alerts:
        st.success("No temperature excursions detected.")
    else:
        import pandas as pd
        rows = []
        for a in alerts:
            rows.append({
                "Shipment ID":    a["shipment_id"],
                "Cargo Type":     a["cargo_type"],
                "Severity":       a["excursion_severity"],
                "Excursions":     a["excursion_count"],
                "Risk Score":     a["cold_chain_risk_score"],
                "Latest Temp (C)":a.get("latest_temp_c"),
                "Min (C)":        a.get("required_temp_min_c"),
                "Max (C)":        a.get("required_temp_max_c"),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Shipment Temperature History")

    # Show all cold-chain shipments in the picker, not just those with alerts
    from core.cold_chain_monitor import load_temperature_data
    temp_entries = load_temperature_data()
    cold_shp_ids = [e["shipment_id"] for e in temp_entries]

    if not cold_shp_ids:
        st.info("No temperature data available.")
        return

    sel_cold = st.selectbox("Select a cold-chain shipment", cold_shp_ids, key="sel_cold")
    if not sel_cold:
        return

    status = get_shipment_temperature_status(sel_cold)
    sev_color = SEV_COLORS.get(status["excursion_severity"], "#718096")
    st.markdown(
        _badge(status["excursion_severity"], sev_color) + f" {status['explanation']}",
        unsafe_allow_html=True,
    )
    st.write(
        f"Safe range: [{status['required_temp_min_c']} °C, "
        f"{status['required_temp_max_c']} °C] | "
        f"Cold-chain risk score: {status['cold_chain_risk_score']}/100"
    )

    readings = status["readings"]
    if not readings:
        st.info("No readings recorded for this shipment.")
        return

    # Build chart data
    import pandas as pd
    chart_rows = []
    for i, r in enumerate(readings):
        ts = r.get("timestamp") or r.get("recorded_at") or str(i)
        chart_rows.append({
            "Reading #": i + 1,
            "Timestamp": ts,
            "Temp (°C)": r.get("temperature_c"),
            "Status":    r.get("status", "normal"),
        })
    df_chart = pd.DataFrame(chart_rows)

    st.line_chart(df_chart.set_index("Reading #")[["Temp (°C)"]])

    # Add threshold reference lines as a note
    t_min = status["required_temp_min_c"]
    t_max = status["required_temp_max_c"]
    st.caption(
        f"Safe temperature range: {t_min} °C — {t_max} °C | "
        f"Readings: {status['reading_count']} | "
        f"Excursions: {status['excursion_count']}"
    )

    # Raw readings table
    with st.expander("Raw readings table"):
        st.dataframe(df_chart, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="SmartRoute AI",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    pages = {
        "Dashboard":   page_dashboard,
        "Shipments":   page_shipments,
        "Disruptions": page_disruptions,
        "Fleet":       page_fleet,
        "Cold Chain":  page_cold_chain,
    }

    st.sidebar.title("SmartRoute AI")
    st.sidebar.markdown("*IBM Bob AI Innovation Hackathon 2026*")
    st.sidebar.divider()
    page = st.sidebar.radio("Navigate", list(pages.keys()), key="nav")

    # Render selected page
    pages[page]()

    # Footer
    st.sidebar.divider()
    ai_status = "watsonx.ai connected" if is_watsonx_configured() else "Demo Mode (Mock AI)"
    st.sidebar.caption(f"AI: {ai_status}")
    st.sidebar.caption("Team PI-NANT | Track: AI")


main()
