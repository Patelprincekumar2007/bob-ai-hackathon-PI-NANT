"""
app.py — SmartRoute AI  ·  Supply Chain Control Tower
======================================================
Premium hackathon-ready Streamlit dashboard.

Run:  streamlit run src/app.py
"""

import os, sys, time
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.disruption_detector import (
    load_disruptions, load_shipments,
    get_disruption_summary, get_shipment_disruptions,
)
from core.risk_engine import get_risk_summary, score_all_shipments, calculate_risk_by_id
from core.route_advisor import recommend_alternative_routes
from core.fleet_optimizer import (
    get_fleet_summary, get_vehicle_utilisation, recommend_vehicle_for_shipment,
)
from core.cold_chain_monitor import (
    get_cold_chain_summary, get_temperature_alerts,
    get_shipment_temperature_status, load_temperature_data,
)
from core.watsonx_client import generate_ai_explanation, is_watsonx_configured

# ── Exact color contract (never change meaning) ─────────────────────────────
RISK_COLORS = {"CRITICAL":"#E53E3E","HIGH":"#DD6B20","MEDIUM":"#D69E2E","LOW":"#38A169"}
SEV_COLORS  = {
    "critical":"#E53E3E","high":"#DD6B20","medium":"#D69E2E","low":"#38A169",
    "CRITICAL":"#E53E3E","HIGH":"#DD6B20","MEDIUM":"#D69E2E","LOW":"#38A169",
    "WARNING":"#DD6B20","NORMAL":"#38A169",
}

# ── Design tokens ────────────────────────────────────────────────────────────
BG       = "#0A0E17"
CARD     = "#10151F"
ELEVATED = "#1A2130"
BORDER   = "rgba(255,255,255,0.08)"
ACCENT   = "#22D3EE"
ACCENT2  = "#5B8DEF"
TXT      = "#F5F7FA"
TXT2     = "#94A3B8"
TXT3     = "#64748B"

# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── reset / base ── */
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
  background:#0A0E17!important; color:#F5F7FA!important;
  font-family:'Inter',system-ui,sans-serif!important;
}
[data-testid="stSidebar"]{
  background:#0D1220!important;
  border-right:1px solid rgba(255,255,255,0.06)!important;
}
/* hide default Streamlit hamburger / footer */
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden!important;}

/* ── headings ── */
h1,h2,h3{font-family:'Space Grotesk',system-ui,sans-serif!important;color:#F5F7FA!important;}
h1{font-size:1.55rem!important;font-weight:700!important;margin-bottom:2px!important;}
h2{font-size:1.15rem!important;font-weight:600!important;}
h3{font-size:1rem!important;font-weight:600!important;}
hr{border-color:rgba(255,255,255,0.07)!important;margin:18px 0!important;}

/* ── sidebar nav radio ── */
[data-testid="stSidebar"] .stRadio label{
  color:#94A3B8!important;font-size:0.9rem!important;padding:5px 0!important;
}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div span{
  color:#22D3EE!important;font-weight:600!important;
}

/* ── buttons ── */
.stButton>button{
  background:linear-gradient(135deg,#22D3EE,#5B8DEF)!important;
  color:#0A0E17!important;border:none!important;border-radius:8px!important;
  font-weight:700!important;font-size:0.88rem!important;
  padding:9px 22px!important;transition:opacity .2s!important;
}
.stButton>button:hover{opacity:.85!important;}

/* ── selectbox ── */
[data-testid="stSelectbox"]>div>div{
  background:#1A2130!important;border:1px solid rgba(255,255,255,0.1)!important;
  border-radius:8px!important;color:#F5F7FA!important;
}

/* ── text input ── */
[data-testid="stTextInput"]>div>div>input{
  background:#1A2130!important;border:1px solid rgba(255,255,255,0.1)!important;
  border-radius:8px!important;color:#F5F7FA!important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"]{border-radius:10px!important;overflow:hidden!important;}
[data-testid="stDataFrame"] iframe{border-radius:10px!important;}

/* ── expander ── */
[data-testid="stExpander"]{
  background:#10151F!important;
  border:1px solid rgba(255,255,255,0.08)!important;border-radius:10px!important;
}
[data-testid="stExpander"] summary{
  color:#94A3B8!important;font-weight:600!important;font-size:0.9rem!important;
}

/* ── alert / info / success / warning ── */
[data-testid="stAlert"]{border-radius:10px!important;}

/* ── caption ── */
[data-testid="stCaptionContainer"]{color:#64748B!important;font-size:0.78rem!important;}

/* ── metric ── */
[data-testid="stMetric"]{
  background:#10151F!important;border:1px solid rgba(255,255,255,0.07)!important;
  border-radius:12px!important;padding:14px 18px!important;
}
[data-testid="stMetricLabel"]{color:#64748B!important;font-size:0.72rem!important;text-transform:uppercase;letter-spacing:.06em;}
[data-testid="stMetricValue"]{color:#F5F7FA!important;font-size:1.6rem!important;font-weight:700!important;}

/* ── custom component classes ── */
.sr-card{
  background:#10151F;border:1px solid rgba(255,255,255,0.08);
  border-radius:12px;padding:18px 20px;margin-bottom:10px;
}
.sr-card-accent{
  background:#10151F;border:1px solid rgba(255,255,255,0.08);
  border-left:3px solid #22D3EE;border-radius:0 12px 12px 0;
  padding:16px 20px;margin-bottom:8px;
}
.sr-kpi-icon{font-size:1.3rem;margin-bottom:6px;line-height:1;}
.sr-kpi-val{font-size:1.95rem;font-weight:800;color:#F5F7FA;font-family:'Space Grotesk',sans-serif;line-height:1.1;}
.sr-kpi-label{font-size:0.7rem;text-transform:uppercase;letter-spacing:.08em;color:#64748B;margin-top:5px;}
.sr-kpi-sub{font-size:0.8rem;color:#22D3EE;margin-top:3px;}

.sr-section{
  font-size:0.72rem;text-transform:uppercase;letter-spacing:.1em;
  color:#64748B;font-weight:700;
  margin:22px 0 10px 0;padding-bottom:5px;
  border-bottom:1px solid rgba(255,255,255,0.06);
}
.sr-label{color:#64748B;font-size:0.82rem;margin-right:4px;}
.sr-val  {color:#F5F7FA;font-weight:600;font-size:0.9rem;}
.sr-row  {margin-bottom:7px;}
.sr-mono {font-family:'JetBrains Mono',monospace;font-size:0.88rem;color:#22D3EE;}

.sr-badge{
  display:inline-block;padding:2px 11px;border-radius:20px;
  font-size:0.76rem;font-weight:700;letter-spacing:.04em;color:#fff;
}

.sr-factor-wrap{margin-bottom:10px;}
.sr-factor-hdr{display:flex;justify-content:space-between;margin-bottom:3px;}
.sr-factor-name{font-size:0.83rem;color:#94A3B8;}
.sr-factor-pts {font-size:0.83rem;font-weight:700;color:#22D3EE;}
.sr-factor-bg  {background:rgba(255,255,255,0.07);border-radius:4px;height:6px;overflow:hidden;}
.sr-factor-fill{height:6px;border-radius:4px;background:linear-gradient(90deg,#22D3EE,#5B8DEF);}

.sr-pill-wx  {background:rgba(34,211,238,.15);color:#22D3EE;padding:3px 11px;border-radius:20px;font-size:0.74rem;font-weight:700;}
.sr-pill-demo{background:rgba(251,191,36,.12);color:#FBBF24;padding:3px 11px;border-radius:20px;font-size:0.74rem;font-weight:700;}

.sr-empty{text-align:center;padding:28px 0;color:#64748B;font-size:0.92rem;}
.sr-page-sub{color:#64748B;font-size:0.9rem;margin-top:-2px;margin-bottom:18px;}

.sr-chip{
  display:inline-block;background:rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.1);border-radius:20px;
  padding:2px 10px;font-size:0.78rem;color:#94A3B8;margin:2px 3px 2px 0;
}

.sr-score-bar-bg  {background:rgba(255,255,255,0.07);border-radius:4px;height:5px;overflow:hidden;margin-top:3px;}
.sr-score-bar-fill{height:5px;border-radius:4px;}
</style>
"""

# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def _badge(label: str, color: str) -> str:
    return (f'<span class="sr-badge" style="background:{color}">{label}</span>')

def _risk_badge(level: str) -> str:
    return _badge(level, RISK_COLORS.get(level.upper(), "#718096"))

def _sev_badge(sev: str) -> str:
    return _badge(sev.upper(), SEV_COLORS.get(sev.upper(), "#718096"))

def _mono(text: str) -> str:
    return f'<span class="sr-mono">{text}</span>'

def _kpi(icon, value, label, sub=""):
    sub_html = f'<div class="sr-kpi-sub">{sub}</div>' if sub else ""
    return (f'<div class="sr-card">'
            f'<div class="sr-kpi-icon">{icon}</div>'
            f'<div class="sr-kpi-val">{value}</div>'
            f'<div class="sr-kpi-label">{label}</div>{sub_html}</div>')

def _section(title: str):
    st.markdown(f'<div class="sr-section">{title}</div>', unsafe_allow_html=True)

def _empty(msg: str, icon="📭"):
    st.markdown(f'<div class="sr-empty">{icon}<br>{msg}</div>', unsafe_allow_html=True)

def _row(label, value):
    return (f'<div class="sr-row"><span class="sr-label">{label}</span>'
            f'<span class="sr-val">{value}</span></div>')

def _factor_bar(label, val, max_val):
    pct = min(100, int(val / max_val * 100)) if max_val else 0
    return (f'<div class="sr-factor-wrap">'
            f'<div class="sr-factor-hdr">'
            f'<span class="sr-factor-name">{label}</span>'
            f'<span class="sr-factor-pts">{val}/{int(max_val)}</span></div>'
            f'<div class="sr-factor-bg">'
            f'<div class="sr-factor-fill" style="width:{pct}%"></div></div></div>')

def _score_color(score: int) -> str:
    if score >= 75: return RISK_COLORS["CRITICAL"]
    if score >= 50: return RISK_COLORS["HIGH"]
    if score >= 25: return RISK_COLORS["MEDIUM"]
    return RISK_COLORS["LOW"]

def _score_bar(score: int) -> str:
    c = _score_color(score)
    return (f'<div class="sr-score-bar-bg">'
            f'<div class="sr-score-bar-fill" style="width:{score}%;background:{c}"></div></div>')

def _chips(items):
    return " ".join(f'<span class="sr-chip">{i}</span>' for i in items) if items else "—"

# ── DataFrame styling (no matplotlib) ───────────────────────────────────────
def _style_df(df: pd.DataFrame):
    def _cr(val):
        c = RISK_COLORS.get(str(val).upper(), "")
        return f"color:{c};font-weight:700;" if c else ""
    s = df.style
    for col in ("Risk Level","Severity","excursion_severity"):
        if col in df.columns:
            s = s.map(_cr, subset=[col])
    return s

# ════════════════════════════════════════════════════════════════════════════
# Cached backend calls
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=30)
def cached_shipments():           return load_shipments()
@st.cache_data(ttl=30)
def cached_disruptions():         return load_disruptions()
@st.cache_data(ttl=30)
def cached_scored_shipments():    return score_all_shipments()
@st.cache_data(ttl=30)
def cached_risk_summary():        return get_risk_summary()
@st.cache_data(ttl=30)
def cached_disruption_summary():  return get_disruption_summary()
@st.cache_data(ttl=30)
def cached_fleet_summary():       return get_fleet_summary()
@st.cache_data(ttl=30)
def cached_vehicle_utilisation(): return get_vehicle_utilisation()
@st.cache_data(ttl=30)
def cached_cold_chain_summary():  return get_cold_chain_summary()
@st.cache_data(ttl=30)
def cached_temperature_alerts():  return get_temperature_alerts()

def get_shipment_detail(sid):
    risk  = calculate_risk_by_id(sid)
    disrs = get_shipment_disruptions(sid)
    routes= recommend_alternative_routes(sid)
    veh   = recommend_vehicle_for_shipment(sid)
    raw   = next((s for s in load_shipments() if s["id"] == sid), None)
    cold  = get_shipment_temperature_status(sid) if raw and raw.get("requires_cold_chain") else None
    return dict(risk=risk, disruptions=disrs, routes=routes, vehicle=veh, cold=cold, raw=raw)

def filter_scored(scored, rf, sf, pf, search=""):
    out = scored
    if rf and rf != "All":   out = [s for s in out if s["classification"] == rf]
    if sf and sf != "All":   out = [s for s in out if s.get("status","").lower() == sf.lower()]
    if pf and pf != "All":   out = [s for s in out if s.get("priority","").lower() == pf.lower()]
    if search:
        q = search.lower()
        out = [s for s in out if q in s["shipment_id"].lower() or q in s.get("description","").lower()]
    return out

def build_ai_prompt(sid, risk, disrs):
    rc  = (risk or {}).get("classification","UNKNOWN")
    rs  = (risk or {}).get("score",0)
    dt  = "; ".join(d["title"] for d in disrs) if disrs else "None"
    return (f"You are a supply chain risk analyst. Shipment {sid} has a risk score of "
            f"{rs}/100 ({rc}). Active disruptions: {dt}. Provide a brief, actionable "
            f"explanation for a logistics coordinator: what is happening, why it matters, "
            f"and what they should do next.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown('<h1>⚓ SmartRoute AI</h1>'
                '<div class="sr-page-sub">Supply Chain Control Tower — real-time risk, disruption & fleet intelligence</div>',
                unsafe_allow_html=True)

    risk  = cached_risk_summary()
    disr  = cached_disruption_summary()
    fleet = cached_fleet_summary()
    cold  = cached_cold_chain_summary()

    _section("Fleet Overview")
    cols = st.columns(7)
    cards = [
        ("📦", risk["total_shipments"],              "Total Shipments",    ""),
        ("⚠️",  disr["total_affected_shipments"],     "At-Risk Shipments",  ""),
        ("🔴",  risk["critical_count"],               "Critical Risk",      f'{risk["critical_count"]} CRITICAL'),
        ("🌩️", disr["total_active_disruptions"],     "Active Disruptions", ""),
        ("🚢",  fleet["available"],                   "Available Vehicles", ""),
        ("📊",  f'{fleet["utilisation_pct"]}%',       "Fleet Utilisation",  ""),
        ("🌡️", cold["shipments_with_excursions"],    "Cold-Chain Alerts",  ""),
    ]
    for col, (icon, val, label, sub) in zip(cols, cards):
        col.markdown(_kpi(icon, val, label, sub), unsafe_allow_html=True)

    st.divider()
    _section("Risk Breakdown")
    rc = st.columns(4)
    risk_cards = [
        ("🔴", risk["critical_count"], "Critical", "Score 75–100", RISK_COLORS["CRITICAL"]),
        ("🟠", risk["high_count"],     "High",     "Score 50–74",  RISK_COLORS["HIGH"]),
        ("🟡", risk["medium_count"],   "Medium",   "Score 25–49",  RISK_COLORS["MEDIUM"]),
        ("🟢", risk["low_count"],      "Low",      "Score 0–24",   RISK_COLORS["LOW"]),
    ]
    total = risk["total_shipments"] or 1
    for col, (icon, cnt, label, rng, clr) in zip(rc, risk_cards):
        pct = round(cnt / total * 100)
        col.markdown(
            f'<div class="sr-card" style="border-left:3px solid {clr};border-radius:0 12px 12px 0;">'
            f'<div class="sr-kpi-icon">{icon}</div>'
            f'<div class="sr-kpi-val" style="color:{clr}">{cnt}</div>'
            f'<div class="sr-kpi-label">{label}</div>'
            f'<div class="sr-kpi-sub">{rng} · {pct}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    _section("Top At-Risk Shipments")
    scored = cached_scored_shipments()
    top = [s for s in scored if s["classification"] in ("CRITICAL","HIGH")][:5]
    if not top:
        _empty("No CRITICAL or HIGH risk shipments at this time.", "✅")
    else:
        rows = []
        for s in top:
            rows.append({
                "ID": s["shipment_id"],
                "Description": s["description"],
                "Score": s["score"],
                "Risk Level": s["classification"],
                "Status": s.get("status",""),
                "Delay (days)": s.get("delay_days",0),
                "Disruptions": len(s.get("disruptions",[])),
            })
        df = pd.DataFrame(rows)
        st.dataframe(_style_df(df), use_container_width=True, hide_index=True,
                     column_config={"Score": st.column_config.NumberColumn("Score", format="%d")})

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Shipments
# ════════════════════════════════════════════════════════════════════════════
def page_shipments():
    st.markdown('<h1>📋 Shipments</h1>'
                '<div class="sr-page-sub">Risk-scored shipment register with disruption, route and AI detail</div>',
                unsafe_allow_html=True)

    scored = cached_scored_shipments()

    # ── sidebar filters ──────────────────────────────────────────────────────
    st.sidebar.markdown('<div class="sr-section">Filters</div>', unsafe_allow_html=True)
    risk_levels  = ["All","CRITICAL","HIGH","MEDIUM","LOW"]
    statuses     = ["All"] + sorted({s.get("status","") for s in scored if s.get("status")})
    priorities   = ["All"] + sorted({s.get("priority","") for s in scored if s.get("priority")})
    risk_filter     = st.sidebar.selectbox("Risk Level", risk_levels,  key="filter_risk")
    status_filter   = st.sidebar.selectbox("Status",     statuses,     key="filter_status")
    priority_filter = st.sidebar.selectbox("Priority",   priorities,   key="filter_priority")

    search = st.text_input("🔍  Search shipment ID or description", key="_shp_search", placeholder="e.g. SHP-001 or pharma")
    filtered = filter_scored(scored, risk_filter, status_filter, priority_filter, search)

    _section(f"All Shipments — {len(filtered)} shown")
    if not filtered:
        _empty("No shipments match the selected filters.", "🔍")
        return

    rows = []
    for s in filtered:
        rows.append({
            "ID": s["shipment_id"],
            "Description": s["description"],
            "Score": s["score"],
            "Risk Level": s["classification"],
            "Status": s.get("status",""),
            "Priority": s.get("priority",""),
            "Delay (d)": s.get("delay_days",0),
            "Disruptions": len(s.get("disruptions",[])),
            "Cold Chain": "❄️ Yes" if s.get("requires_cold_chain") else "No",
        })
    df = pd.DataFrame(rows)
    st.dataframe(_style_df(df), use_container_width=True, hide_index=True,
                 column_config={"Score": st.column_config.NumberColumn("Score", format="%d")})

    # ── detail view ──────────────────────────────────────────────────────────
    st.divider()
    _section("Shipment Detail")
    ids = [s["shipment_id"] for s in filtered]
    selected_id = st.selectbox("Select shipment for detail view", ids, key="sel_shipment")
    if not selected_id:
        return

    detail = get_shipment_detail(selected_id)
    risk   = detail["risk"]
    raw    = detail["raw"]

    if risk is None:
        st.error(f"Could not load risk data for {selected_id}.")
        return

    # info + risk columns
    col1, col2 = st.columns(2, gap="large")
    with col1:
        _section("Shipment Info")
        orig = (raw or {}).get("origin",{})
        dest = (raw or {}).get("destination",{})
        info = "".join([
            _row("Shipment ID:", f'<span class="sr-mono">{selected_id}</span>'),
            _row("Description:", (raw or {}).get("description","N/A")),
            _row("Carrier:",     (raw or {}).get("carrier","N/A")),
            _row("Origin:",      f"{orig.get('city','')} · {orig.get('country','')}"),
            _row("Destination:", f"{dest.get('city','')} · {dest.get('country','')}"),
            _row("Status:",      (raw or {}).get("status","N/A")),
            _row("Priority:",    (raw or {}).get("priority","N/A")),
            _row("Cargo Type:",  (raw or {}).get("cargo_type","N/A")),
        ])
        st.markdown(f'<div class="sr-card">{info}</div>', unsafe_allow_html=True)

    with col2:
        _section("Risk Assessment")
        fb  = risk.get("factor_breakdown",{})
        sc  = risk["score"]
        cls = risk["classification"]
        clr = RISK_COLORS.get(cls,"#718096")
        bars = "".join([
            _factor_bar("Disruption Severity", fb.get("disruption_severity",0), 35),
            _factor_bar("Delay Factor",         fb.get("delay",0),              25),
            _factor_bar("Deadline Pressure",    fb.get("deadline_pressure",0),  20),
            _factor_bar("Priority Factor",      fb.get("priority",0),           15),
            _factor_bar("Cold-Chain Factor",    fb.get("cold_chain",0),          5),
        ])
        st.markdown(
            f'<div class="sr-card">'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">'
            f'<span style="font-size:2.3rem;font-weight:800;color:{clr};font-family:Space Grotesk,sans-serif">{sc}</span>'
            f'<span style="color:#64748B;font-size:.9rem">/ 100</span>'
            f'&nbsp;{_badge(cls,clr)}</div>{bars}</div>',
            unsafe_allow_html=True,
        )

    # active disruptions
    _section("Active Disruptions")
    disrs = detail["disruptions"]
    if not disrs:
        _empty("No active disruptions affecting this shipment.", "✅")
    else:
        for d in disrs:
            sc2 = SEV_COLORS.get(d["severity"].upper(),"#718096")
            st.markdown(
                f'<div class="sr-card" style="border-left:3px solid {sc2};border-radius:0 12px 12px 0;">'
                f'{_badge(d["severity"].upper(), sc2)}'
                f'&nbsp;<strong style="color:#F5F7FA">{d["title"]}</strong>'
                f'<span style="color:#64748B;font-size:.82rem;margin-left:10px;">'
                f'{d["type"]} · +{d["estimated_delay_days"]}d · +${d["additional_cost_usd"]:,}</span>'
                f'<div style="color:#94A3B8;font-size:.86rem;margin-top:6px;">{d["description"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # route alternatives
    _section("Route Alternatives")
    routes = detail["routes"]
    alts   = routes.get("alternatives",[])
    if not alts:
        if routes.get("action_required"):
            _empty("No pre-defined alternatives. Contact carrier directly.", "📞")
        else:
            _empty("No rerouting required — shipment is on schedule.", "✅")
    else:
        for i, alt in enumerate(alts, 1):
            ed = alt["extra_delay_days"]
            d_str = f"+{ed}d" if ed >= 0 else f"{abs(ed)}d faster"
            d_clr = RISK_COLORS["HIGH"] if ed > 0 else RISK_COLORS["LOW"]
            cost_str = "+${:,}".format(alt["extra_cost_usd"])
            with st.expander(f"Option {i}: {alt['description']}  ({d_str}, {cost_str})"):
                st.markdown(
                    f'{_badge(d_str,d_clr)} {_badge(cost_str,"#1E3A5F")}'
                    f'<div style="color:#94A3B8;margin-top:8px;">{alt["reason"]}</div>',
                    unsafe_allow_html=True,
                )
                veh_list = alt.get("available_vehicles",[])
                if veh_list:
                    v_html = " ".join(f'<span class="sr-chip">🚢 {v["name"]}</span>' for v in veh_list)
                    st.markdown(f'<div style="margin-top:6px;">Vessels: {v_html}</div>', unsafe_allow_html=True)
                else:
                    carriers = _chips(alt.get("suggested_carriers",[]))
                    st.markdown(f'<div style="margin-top:6px;color:#64748B;font-size:.85rem;">Carriers: {carriers}</div>', unsafe_allow_html=True)
                if alt.get("via"):
                    st.markdown(f'<div style="color:#64748B;font-size:.82rem;margin-top:4px;">Via: <strong style="color:#94A3B8">{alt["via"]}</strong></div>', unsafe_allow_html=True)

    # vehicle recommendation
    _section("Vehicle Recommendation")
    vr   = detail["vehicle"]
    best = vr.get("recommended_vehicle")
    if best:
        alts_v = vr.get("alternatives",[])
        alt_html = ""
        for a in alts_v:
            alt_html += (f'<div style="color:#94A3B8;font-size:.85rem;padding:5px 0;'
                         f'border-top:1px solid rgba(255,255,255,.06);">'
                         f'🚢 <strong>{a["name"]}</strong> ({a["carrier"]}) · '
                         f'{a["available_teu"]} TEU · '
                         f'Departs {a.get("next_departure","TBD")} from {a["current_location"]}'
                         f'</div>')
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid #22D3EE;border-radius:0 12px 12px 0;">'
            f'<div style="color:#22D3EE;font-size:.72rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;">✔ Recommended</div>'
            f'<div style="color:#F5F7FA;">{vr["reason"]}</div>{alt_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        _empty(vr.get("reason","No vehicle recommendation available."), "🔍")

    # cold chain
    cold = detail["cold"]
    if cold:
        _section("Cold-Chain Status")
        sc3 = SEV_COLORS.get(cold["excursion_severity"],"#718096")
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid {sc3};border-radius:0 12px 12px 0;">'
            f'{_badge(cold["excursion_severity"], sc3)}'
            f'&nbsp;<span style="color:#94A3B8;">{cold["explanation"]}</span></div>',
            unsafe_allow_html=True,
        )

    # AI explanation
    st.divider()
    ai_configured = is_watsonx_configured()
    ai_label = "[AI - watsonx]" if ai_configured else "[Demo Mode - Mock AI]"
    pill = ('<span class="sr-pill-wx">● AI · watsonx.ai</span>'
            if ai_configured else
            '<span class="sr-pill-demo">○ Demo Mode · Mock AI</span>')
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
        f'<span style="font-weight:700;color:#F5F7FA;font-size:.98rem;">AI Explanation</span>'
        f'{pill}</div>',
        unsafe_allow_html=True,
    )
    if st.button(f"Generate AI Explanation {ai_label}", key=f"ai_{selected_id}"):
        prompt = build_ai_prompt(selected_id, risk, disrs)
        with st.spinner("Calling watsonx.ai…"):
            result = generate_ai_explanation(prompt)
        src_label = "[AI - watsonx]" if result["source"] == "watsonx" else "[Demo Mode - Mock AI]"
        src_pill  = ('<span class="sr-pill-wx">● AI · watsonx.ai</span>'
                     if result["source"] == "watsonx"
                     else '<span class="sr-pill-demo">○ Demo Mode · Mock AI</span>')
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid #22D3EE;border-radius:0 12px 12px 0;">'
            f'<div style="margin-bottom:8px;">{src_pill}</div>'
            f'<div style="color:#94A3B8;line-height:1.65;">{result["text"]}</div></div>',
            unsafe_allow_html=True,
        )
        if result.get("error"):
            st.caption(f"Note: {result['error']}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Disruptions
# ════════════════════════════════════════════════════════════════════════════
def page_disruptions():
    st.markdown('<h1>🌩️ Active Disruptions</h1>'
                '<div class="sr-page-sub">Real-time port, weather, strike and vessel disruption tracking</div>',
                unsafe_allow_html=True)

    disruptions = cached_disruptions()
    active  = [d for d in disruptions if d.get("status") in ("active","monitoring")]
    summary = cached_disruption_summary()

    cols = st.columns(4)
    kpis = [
        ("🌩️", summary["total_active_disruptions"], "Active Disruptions",""),
        ("📦",  summary["total_affected_shipments"], "Affected Shipments",""),
        ("🔴",  summary["critical_count"],           "Critical",""),
        ("🟠",  summary["high_count"],               "High",""),
    ]
    for col,(icon,val,label,sub) in zip(cols,kpis):
        col.markdown(_kpi(icon,val,label,sub), unsafe_allow_html=True)

    st.divider()
    if not active:
        _empty("No active disruptions at this time.", "✅")
        return

    _section("Disruption Register")
    rows = []
    for d in active:
        rows.append({
            "ID": d["id"], "Type": d.get("type",""),
            "Title": d.get("title",""),
            "Severity": d.get("severity","").upper(),
            "Status": d.get("status",""),
            "Est. Delay (d)": d.get("estimated_delay_days",0),
            "Add. Cost ($)": d.get("additional_cost_usd",0),
            "Affected Routes": len(d.get("affected_routes",[])),
        })
    df = pd.DataFrame(rows)
    st.dataframe(_style_df(df), use_container_width=True, hide_index=True,
                 column_config={"Add. Cost ($)": st.column_config.NumberColumn(format="$%d")})

    st.divider()
    _section("Disruption Detail")
    disr_ids = [d["id"] for d in active]
    sel_disr = st.selectbox("Select a disruption", disr_ids, key="sel_disruption")
    if not sel_disr:
        return
    d = next((x for x in active if x["id"] == sel_disr), None)
    if not d:
        return

    sc = SEV_COLORS.get(d.get("severity","").upper(),"#718096")
    st.markdown(
        f'<div class="sr-card" style="border-left:3px solid {sc};border-radius:0 12px 12px 0;">'
        f'{_badge(d.get("severity","").upper(), sc)}'
        f'&nbsp;<strong style="color:#F5F7FA;font-size:1.05rem">{d["title"]}</strong>'
        f'&nbsp;<span class="sr-mono">{d["id"]}</span>'
        f'<div style="color:#94A3B8;margin-top:8px;line-height:1.6;">{d.get("description","")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    c1,c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            f'<div class="sr-card">'
            + _row("Type:",             d.get("type",""))
            + _row("Status:",           d.get("status",""))
            + _row("Est. Delay:",       f'{d.get("estimated_delay_days",0)} days')
            + _row("Additional Cost:",  f'${d.get("additional_cost_usd",0):,}')
            + f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="sr-card">'
            + _row("Affected Ports:",    _chips(d.get("affected_ports",[])) or "—")
            + _row("Affected Routes:",   _chips(d.get("affected_routes",[])) or "—")
            + _row("Affected Carriers:", _chips(d.get("affected_carriers",[])) or "—")
            + _row("Affected Vessels:",  _chips(d.get("affected_vessel_ids",[])) or "—")
            + f'</div>',
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Fleet
# ════════════════════════════════════════════════════════════════════════════
def page_fleet():
    st.markdown('<h1>🚢 Fleet Management</h1>'
                '<div class="sr-page-sub">Vehicle utilisation, availability and assignment tracking</div>',
                unsafe_allow_html=True)

    fleet = cached_fleet_summary()
    cols  = st.columns(5)
    for col,(icon,val,label) in zip(cols,[
        ("🚢", fleet["total"],                  "Total Vehicles"),
        ("✅", fleet["available"],              "Available"),
        ("📦", fleet["assigned"],               "Assigned"),
        ("💤", fleet["idle"],                   "Idle"),
        ("📊", f'{fleet["utilisation_pct"]}%',  "Utilisation"),
    ]):
        col.markdown(_kpi(icon,val,label), unsafe_allow_html=True)

    r1,r2,r3 = st.columns(3)
    r1.markdown(_kpi("❄️",  fleet["reefer_capable_count"],             "Reefer-Capable"), unsafe_allow_html=True)
    r2.markdown(_kpi("📐",  fleet["available_total_teu"],              "Available TEU"),  unsafe_allow_html=True)
    r3.markdown(_kpi("⚖️",  f'{fleet["available_total_weight_kg"]:,}', "Avail. Weight kg"), unsafe_allow_html=True)

    st.divider()
    _section("Per-Vehicle Utilisation")
    util = cached_vehicle_utilisation()
    rows = []
    for v in util:
        rows.append({
            "Vehicle ID":      v["vehicle_id"],
            "Name":            v["name"],
            "Carrier":         v["carrier"],
            "Status":          v["status"],
            "Assigned":        "Yes" if v["assigned"] else "No",
            "Idle":            "Yes" if v["is_idle"] else "No",
            "Capacity (TEU)":  v["capacity_teu"],
            "Used (TEU)":      v["used_teu"],
            "Available (TEU)": v["available_teu"],
            "Load %":          v["load_pct"],
        })
    df = pd.DataFrame(rows)

    def _load_color(val):
        try:
            v = float(val)
            if v >= 85: return f"color:{RISK_COLORS['CRITICAL']};font-weight:700;"
            if v >= 60: return f"color:{RISK_COLORS['MEDIUM']};font-weight:700;"
            return f"color:{RISK_COLORS['LOW']};"
        except Exception:
            return ""

    styler = df.style.map(_load_color, subset=["Load %"])
    st.dataframe(styler, use_container_width=True, hide_index=True,
                 column_config={"Load %": st.column_config.ProgressColumn("Load %", min_value=0, max_value=100, format="%.1f%%")})

    st.divider()
    _section("Vehicle Recommendation Picker")
    shp_ids = [s["id"] for s in cached_shipments()]
    sel_shp = st.selectbox("Select a shipment to find the best vehicle", shp_ids, key="fleet_shp")
    if not sel_shp:
        return
    rec  = recommend_vehicle_for_shipment(sel_shp)
    best = rec.get("recommended_vehicle")
    if best:
        alts = rec.get("alternatives",[])
        alt_html = ""
        for a in alts:
            alt_html += (f'<div style="color:#94A3B8;font-size:.86rem;padding:5px 0;'
                         f'border-top:1px solid rgba(255,255,255,.06);">'
                         f'🚢 <strong>{a["name"]}</strong> ({a["carrier"]}) · '
                         f'{a["available_teu"]} TEU · '
                         f'departs {a.get("next_departure","TBD")} from {a["current_location"]}</div>')
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid #22D3EE;border-radius:0 12px 12px 0;">'
            f'<div style="color:#22D3EE;font-size:.72rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;">✔ Recommended</div>'
            f'<div style="color:#F5F7FA;">{rec["reason"]}</div>{alt_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        _empty(rec.get("reason","No vehicle found."), "🔍")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Cold Chain
# ════════════════════════════════════════════════════════════════════════════
def page_cold_chain():
    st.markdown('<h1>🌡️ Cold-Chain Monitor</h1>'
                '<div class="sr-page-sub">Temperature excursion alerts and shipment cold-chain history</div>',
                unsafe_allow_html=True)

    summary = cached_cold_chain_summary()
    cols    = st.columns(4)
    for col,(icon,val,label) in zip(cols,[
        ("📦", summary["total_tracked"],           "Tracked Shipments"),
        ("🟢", summary["normal_count"],            "Normal"),
        ("🟡", summary["warning_count"],           "Warning"),
        ("🔴", summary["critical_count"],          "Critical Excursions"),
    ]):
        col.markdown(_kpi(icon,val,label), unsafe_allow_html=True)

    st.divider()
    _section("Temperature Alerts")
    alerts = cached_temperature_alerts()
    if not alerts:
        _empty("No temperature excursions detected — all cold-chain shipments within safe range.", "✅")
    else:
        rows = []
        for a in alerts:
            rows.append({
                "Shipment ID":     a["shipment_id"],
                "Cargo Type":      a["cargo_type"],
                "Severity":        a["excursion_severity"],
                "Excursions":      a["excursion_count"],
                "Risk Score":      a["cold_chain_risk_score"],
                "Latest Temp (C)": a.get("latest_temp_c"),
                "Min (C)":         a.get("required_temp_min_c"),
                "Max (C)":         a.get("required_temp_max_c"),
            })
        df = pd.DataFrame(rows)
        st.dataframe(_style_df(df), use_container_width=True, hide_index=True)

    st.divider()
    _section("Shipment Temperature History")
    temp_entries = load_temperature_data()
    cold_shp_ids = [e["shipment_id"] for e in temp_entries]
    if not cold_shp_ids:
        _empty("No temperature data available.", "📭")
        return

    sel_cold = st.selectbox("Select a cold-chain shipment", cold_shp_ids, key="sel_cold")
    if not sel_cold:
        return

    status  = get_shipment_temperature_status(sel_cold)
    sev_clr = SEV_COLORS.get(status["excursion_severity"],"#718096")
    t_min   = status["required_temp_min_c"]
    t_max   = status["required_temp_max_c"]

    # status card
    st.markdown(
        f'<div class="sr-card" style="border-left:3px solid {sev_clr};border-radius:0 12px 12px 0;">'
        f'{_badge(status["excursion_severity"], sev_clr)}'
        f'&nbsp;<span style="color:#94A3B8;">{status["explanation"]}</span>'
        f'<div style="color:#64748B;font-size:.82rem;margin-top:6px;">'
        f'Safe range: {t_min} °C – {t_max} °C &nbsp;|&nbsp; '
        f'Cold-chain risk: <strong style="color:#22D3EE">{status["cold_chain_risk_score"]}/100</strong>'
        f'&nbsp;|&nbsp; Latest: <strong style="color:#F5F7FA">{status.get("latest_temp_c","—")} °C</strong>'
        f'&nbsp;|&nbsp; Min observed: {status.get("min_observed_c","—")} °C'
        f'&nbsp;|&nbsp; Max observed: {status.get("max_observed_c","—")} °C'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    readings = status["readings"]
    if not readings:
        _empty("No readings recorded for this shipment.", "📭")
        return

    # build chart data
    chart_rows = []
    for i,r in enumerate(readings):
        ts = r.get("timestamp") or r.get("recorded_at") or str(i)
        chart_rows.append({
            "Reading #": i+1, "Timestamp": ts,
            "Temp (°C)": r.get("temperature_c"),
            "Status":    r.get("status","normal"),
            "Location":  r.get("location",""),
            "Sensor":    r.get("sensor_id",""),
            "Notes":     r.get("notes",""),
        })
    df_chart = pd.DataFrame(chart_rows)
    temps    = df_chart["Temp (°C)"].tolist()
    labels   = df_chart["Reading #"].tolist()
    statuses = df_chart["Status"].tolist()
    tooltips = [
        f"Reading #{r['Reading #']}<br>Temp: {r['Temp (°C)']} °C<br>"
        f"Status: {r['Status']}<br>Location: {r['Location'] or '—'}<br>"
        f"Sensor: {r['Sensor'] or '—'}<br>Notes: {r['Notes'] or '—'}"
        for _, r in df_chart.iterrows()
    ]

    pt_colors = [
        RISK_COLORS["CRITICAL"] if str(s).lower()=="critical"
        else RISK_COLORS["HIGH"] if str(s).lower() in ("warning","excursion","high")
        else RISK_COLORS["LOW"]
        for s in statuses
    ]

    fig = go.Figure()

    # safe-range band
    if t_min is not None and t_max is not None:
        fig.add_trace(go.Scatter(
            x=labels+labels[::-1], y=[t_max]*len(labels)+[t_min]*len(labels),
            fill="toself", fillcolor="rgba(56,161,105,0.10)",
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip", name="Safe Range", showlegend=True,
        ))
        fig.add_trace(go.Scatter(
            x=labels, y=[t_min]*len(labels), mode="lines",
            line=dict(color=RISK_COLORS["LOW"], width=1, dash="dot"),
            name=f"Min ({t_min}°C)", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=labels, y=[t_max]*len(labels), mode="lines",
            line=dict(color=RISK_COLORS["LOW"], width=1, dash="dot"),
            name=f"Max ({t_max}°C)", hoverinfo="skip",
        ))

    # temperature line
    fig.add_trace(go.Scatter(
        x=labels, y=temps, mode="lines+markers",
        line=dict(color="#22D3EE", width=2.5),
        marker=dict(color=pt_colors, size=7, line=dict(color="#0A0E17", width=1.5)),
        name="Temperature (°C)",
        hovertext=tooltips, hoverinfo="text",
    ))

    fig.update_layout(
        plot_bgcolor="#0D1220", paper_bgcolor="#0D1220",
        font=dict(color="#94A3B8", family="Inter,sans-serif", size=12),
        xaxis=dict(title="Reading #", gridcolor="rgba(255,255,255,0.05)",
                   showline=True, linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title="Temperature (°C)", gridcolor="rgba(255,255,255,0.05)",
                   showline=True, linecolor="rgba(255,255,255,0.1)"),
        legend=dict(bgcolor="#10151F", bordercolor="rgba(255,255,255,.08)",
                    borderwidth=1, font=dict(size=11)),
        margin=dict(l=10,r=10,t=16,b=10), height=340,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Safe range: {t_min} °C – {t_max} °C  |  "
        f"Readings: {status['reading_count']}  |  "
        f"Excursions: {status['excursion_count']}"
    )

    with st.expander("Raw readings table"):
        st.dataframe(df_chart, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="SmartRoute AI",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    pages = {
        "Dashboard":   page_dashboard,
        "Shipments":   page_shipments,
        "Disruptions": page_disruptions,
        "Fleet":       page_fleet,
        "Cold Chain":  page_cold_chain,
    }

    # ── Sidebar ──────────────────────────────────────────────────────────────
    ai_on = is_watsonx_configured()
    pill  = ('<span class="sr-pill-wx">● watsonx.ai Connected</span>'
             if ai_on else
             '<span class="sr-pill-demo">○ Demo Mode · Mock AI</span>')

    with st.sidebar:
        st.markdown(
            f'<div style="padding:18px 4px 10px 4px;">'
            f'<div style="font-size:1.3rem;font-weight:800;color:#22D3EE;'
            f'font-family:Space Grotesk,sans-serif;letter-spacing:.02em;">⚓ SmartRoute AI</div>'
            f'<div style="font-size:0.7rem;color:#64748B;margin-top:2px;letter-spacing:.04em;">'
            f'SUPPLY CHAIN CONTROL TOWER</div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        page = st.radio("Navigate", list(pages.keys()), key="nav")
        st.divider()
        st.markdown(
            f'<div style="padding:4px 0 10px 0;">'
            f'<div style="font-size:.68rem;color:#64748B;text-transform:uppercase;'
            f'letter-spacing:.08em;margin-bottom:5px;">AI Status</div>'
            f'{pill}</div>',
            unsafe_allow_html=True,
        )
        st.caption("Team PI-NANT · Track: AI")

    pages[page]()

main()
