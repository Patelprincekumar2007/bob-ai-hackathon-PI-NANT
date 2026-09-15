"""
app.py — SmartRoute AI  ·  Supply Chain Control Tower
======================================================
Premium SaaS Streamlit dashboard.

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

# ── Color contract ───────────────────────────────────────────────────────────
RISK_COLORS = {"CRITICAL":"#F87171","HIGH":"#FB923C","MEDIUM":"#FBBF24","LOW":"#34D399"}
SEV_COLORS  = {
    "critical":"#F87171","high":"#FB923C","medium":"#FBBF24","low":"#34D399",
    "CRITICAL":"#F87171","HIGH":"#FB923C","MEDIUM":"#FBBF24","LOW":"#34D399",
    "WARNING":"#FB923C","NORMAL":"#34D399",
}

# ── Design tokens ────────────────────────────────────────────────────────────
BG       = "#070B14"
CARD     = "#0D1424"
ELEVATED = "#111827"
BORDER   = "rgba(255,255,255,0.07)"
ACCENT   = "#38BDF8"
ACCENT2  = "#818CF8"
ACCENT3  = "#34D399"
TXT      = "#F1F5F9"
TXT2     = "#94A3B8"
TXT3     = "#475569"

# ════════════════════════════════════════════════════════════════════════════
# CSS — Premium SaaS Design System
# ════════════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── CSS Variables ── */
:root {
  --bg:        #070B14;
  --card:      #0D1424;
  --elevated:  #111827;
  --border:    rgba(255,255,255,0.07);
  --accent:    #38BDF8;
  --accent2:   #818CF8;
  --accent3:   #34D399;
  --txt:       #F1F5F9;
  --txt2:      #94A3B8;
  --txt3:      #475569;
  --radius:    14px;
  --radius-sm: 8px;
  --shadow:    0 4px 24px rgba(0,0,0,0.4);
  --glow:      0 0 20px rgba(56,189,248,0.15);
}

/* ── Base reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--bg) !important;
  color: var(--txt) !important;
  font-family: 'Inter', system-ui, sans-serif !important;
}

/* ── Main content padding ── */
[data-testid="stMain"] > div {
  padding-top: 1.5rem !important;
}

section[data-testid="stMainBlockContainer"] {
  padding: 0 2rem 2rem 2rem !important;
  max-width: 1400px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #080C17 !important;
  border-right: 1px solid rgba(56,189,248,0.08) !important;
}
[data-testid="stSidebar"] > div {
  padding: 0 !important;
}
[data-testid="stSidebarContent"] {
  padding: 0 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"] {
  visibility: hidden !important;
  height: 0 !important;
}

/* ── Headings ── */
h1, h2, h3 {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  color: var(--txt) !important;
  letter-spacing: -0.02em !important;
}
h1 { font-size: 1.7rem !important; font-weight: 800 !important; margin-bottom: 4px !important; }
h2 { font-size: 1.2rem !important; font-weight: 700 !important; }
h3 { font-size: 1rem !important;   font-weight: 600 !important; }

hr {
  border: none !important;
  border-top: 1px solid rgba(255,255,255,0.06) !important;
  margin: 20px 0 !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important;
  color: #070B14 !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 700 !important;
  font-size: 0.875rem !important;
  padding: 10px 24px !important;
  letter-spacing: 0.01em !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 15px rgba(56,189,248,0.25) !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(56,189,248,0.35) !important;
  opacity: 0.92 !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
  background: var(--elevated) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--txt) !important;
  transition: border-color 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(56,189,248,0.1) !important;
}

/* ── Text input ── */
[data-testid="stTextInput"] > div > div > input {
  background: var(--elevated) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--txt) !important;
  font-size: 0.9rem !important;
  padding: 10px 14px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(56,189,248,0.1) !important;
}
[data-testid="stTextInput"] > div > div > input::placeholder {
  color: var(--txt3) !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
  border-radius: var(--radius) !important;
  overflow: hidden !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="stDataFrame"] iframe { border-radius: var(--radius) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden !important;
  transition: border-color 0.2s !important;
}
[data-testid="stExpander"]:hover {
  border-color: rgba(56,189,248,0.2) !important;
}
[data-testid="stExpander"] summary {
  color: var(--txt2) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 12px 16px !important;
}
details[data-testid="stExpander"] > div {
  padding: 0 16px 14px !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] {
  color: var(--txt3) !important;
  font-size: 0.78rem !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 16px 20px !important;
  transition: border-color 0.2s, transform 0.2s !important;
}
[data-testid="stMetric"]:hover {
  border-color: rgba(56,189,248,0.2) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--txt3) !important;
  font-size: 0.7rem !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
  color: var(--txt) !important;
  font-size: 1.7rem !important;
  font-weight: 800 !important;
  font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* ══════════════════════════════════════════════════
   SIDEBAR DESIGN
══════════════════════════════════════════════════ */
.sr-sidebar-logo {
  padding: 24px 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 8px;
}
.sr-sidebar-logo-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #38BDF8, #818CF8);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(56,189,248,0.3);
}
.sr-sidebar-brand {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 800;
  color: #F1F5F9;
  letter-spacing: -0.01em;
  line-height: 1.2;
}
.sr-sidebar-tagline {
  font-size: 0.65rem;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 2px;
  font-weight: 600;
}

.sr-nav-label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #334155;
  font-weight: 700;
  padding: 14px 20px 6px;
}

.sr-ai-status {
  margin: 12px 16px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(56,189,248,0.06);
  border: 1px solid rgba(56,189,248,0.12);
}
.sr-ai-status-live {
  background: rgba(52,211,153,0.06);
  border-color: rgba(52,211,153,0.15);
}
.sr-ai-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #34D399;
  box-shadow: 0 0 6px #34D399;
  margin-right: 7px;
  animation: pulse-dot 2s infinite;
}
.sr-ai-dot-demo {
  background: #FBBF24;
  box-shadow: 0 0 6px #FBBF24;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}
.sr-ai-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #34D399;
  letter-spacing: 0.02em;
}
.sr-ai-label-demo { color: #FBBF24; }
.sr-ai-sub {
  font-size: 0.67rem;
  color: #475569;
  margin-top: 3px;
  padding-left: 14px;
}

.sr-sidebar-footer {
  padding: 14px 20px;
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: 8px;
}
.sr-sidebar-footer-txt {
  font-size: 0.67rem;
  color: #334155;
  font-weight: 500;
}

/* ── Sidebar radio overrides ── */
[data-testid="stSidebar"] .stRadio {
  padding: 0 12px !important;
}
[data-testid="stSidebar"] .stRadio > label {
  display: none !important;
}
[data-testid="stSidebar"] .stRadio > div {
  gap: 2px !important;
  flex-direction: column !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
  display: flex !important;
  align-items: center !important;
  padding: 9px 12px !important;
  border-radius: 9px !important;
  color: #64748B !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
  background: rgba(255,255,255,0.04) !important;
  color: #94A3B8 !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {
  background: rgba(56,189,248,0.1) !important;
  color: #38BDF8 !important;
  border-color: rgba(56,189,248,0.2) !important;
  font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════
   PAGE HEADER
══════════════════════════════════════════════════ */
.sr-page-header {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sr-page-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.65rem;
  font-weight: 800;
  color: #F1F5F9;
  letter-spacing: -0.03em;
  line-height: 1.2;
  margin: 0 0 4px 0;
}
.sr-page-sub {
  color: #475569;
  font-size: 0.875rem;
  font-weight: 400;
  margin: 0;
  line-height: 1.5;
}

/* ══════════════════════════════════════════════════
   KPI / METRIC CARDS
══════════════════════════════════════════════════ */
.sr-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 10px;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}
.sr-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(56,189,248,0.15), transparent);
}
.sr-card:hover {
  border-color: rgba(56,189,248,0.18);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(56,189,248,0.08);
}

.sr-card-accent {
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 0 var(--radius) var(--radius) 0;
  padding: 16px 20px;
  margin-bottom: 8px;
  transition: border-color 0.2s;
}
.sr-card-accent:hover {
  border-color: rgba(56,189,248,0.25);
  border-left-color: var(--accent);
}

.sr-kpi-icon {
  font-size: 1.25rem;
  margin-bottom: 10px;
  line-height: 1;
  display: block;
}
.sr-kpi-val {
  font-size: 2rem;
  font-weight: 800;
  color: #F1F5F9;
  font-family: 'Space Grotesk', sans-serif;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.sr-kpi-label {
  font-size: 0.67rem;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: #475569;
  margin-top: 6px;
  font-weight: 700;
}
.sr-kpi-sub {
  font-size: 0.78rem;
  color: #38BDF8;
  margin-top: 4px;
  font-weight: 500;
}

/* ══════════════════════════════════════════════════
   SECTION DIVIDER
══════════════════════════════════════════════════ */
.sr-section {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #334155;
  font-weight: 700;
  margin: 24px 0 12px 0;
}
.sr-section::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255,255,255,0.05);
}

/* ══════════════════════════════════════════════════
   TYPOGRAPHY HELPERS
══════════════════════════════════════════════════ */
.sr-label { color: #475569; font-size: 0.82rem; margin-right: 4px; }
.sr-val   { color: #F1F5F9; font-weight: 600; font-size: 0.9rem; }
.sr-row   { margin-bottom: 8px; display: flex; align-items: flex-start; gap: 6px; }
.sr-mono  { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #38BDF8; }

/* ══════════════════════════════════════════════════
   BADGES & CHIPS
══════════════════════════════════════════════════ */
.sr-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #070B14;
}

.sr-chip {
  display: inline-block;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.76rem;
  color: #94A3B8;
  margin: 2px 3px 2px 0;
  font-weight: 500;
}

.sr-pill-wx {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(52,211,153,0.1);
  color: #34D399;
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid rgba(52,211,153,0.2);
}
.sr-pill-demo {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(251,191,36,0.1);
  color: #FBBF24;
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid rgba(251,191,36,0.2);
}

/* ══════════════════════════════════════════════════
   FACTOR BARS
══════════════════════════════════════════════════ */
.sr-factor-wrap   { margin-bottom: 12px; }
.sr-factor-hdr    { display: flex; justify-content: space-between; margin-bottom: 5px; align-items: center; }
.sr-factor-name   { font-size: 0.82rem; color: #94A3B8; font-weight: 500; }
.sr-factor-pts    { font-size: 0.8rem; font-weight: 700; color: #38BDF8; font-family: 'JetBrains Mono', monospace; }
.sr-factor-bg     { background: rgba(255,255,255,0.05); border-radius: 999px; height: 5px; overflow: hidden; }
.sr-factor-fill   { height: 5px; border-radius: 999px; background: linear-gradient(90deg, #38BDF8, #818CF8); }

/* ══════════════════════════════════════════════════
   SCORE BAR
══════════════════════════════════════════════════ */
.sr-score-bar-bg   { background: rgba(255,255,255,0.06); border-radius: 999px; height: 4px; overflow: hidden; margin-top: 4px; }
.sr-score-bar-fill { height: 4px; border-radius: 999px; }

/* ══════════════════════════════════════════════════
   EMPTY STATE
══════════════════════════════════════════════════ */
.sr-empty {
  text-align: center;
  padding: 40px 20px;
  color: #334155;
  font-size: 0.9rem;
  border: 1px dashed rgba(255,255,255,0.07);
  border-radius: var(--radius);
  background: rgba(255,255,255,0.01);
}
.sr-empty-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.5;
}
.sr-empty-text { color: #475569; font-size: 0.85rem; }

/* ══════════════════════════════════════════════════
   DISRUPTION / RISK CARDS
══════════════════════════════════════════════════ */
.sr-disruption-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
  margin-bottom: 10px;
  transition: border-color 0.2s, transform 0.2s;
}
.sr-disruption-card:hover {
  transform: translateY(-1px);
  border-color: rgba(255,255,255,0.12);
}

/* ══════════════════════════════════════════════════
   RISK LEVEL CARD
══════════════════════════════════════════════════ */
.sr-risk-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px;
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}
.sr-risk-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
.sr-risk-card-glow {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: var(--radius) var(--radius) 0 0;
}

/* ══════════════════════════════════════════════════
   AI SECTION
══════════════════════════════════════════════════ */
.sr-ai-section {
  background: linear-gradient(135deg, rgba(56,189,248,0.04), rgba(129,140,248,0.04));
  border: 1px solid rgba(56,189,248,0.1);
  border-radius: var(--radius);
  padding: 20px;
  margin-top: 8px;
}
.sr-ai-response {
  background: var(--card);
  border: 1px solid rgba(56,189,248,0.15);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-top: 12px;
}
.sr-ai-response-text {
  color: #94A3B8;
  line-height: 1.7;
  font-size: 0.9rem;
}

/* ══════════════════════════════════════════════════
   STAT GRID (Dashboard hero)
══════════════════════════════════════════════════ */
.sr-stat-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
  margin-bottom: 4px;
}

/* ══════════════════════════════════════════════════
   TABLE TWEAKS
══════════════════════════════════════════════════ */
[data-testid="stDataFrame"] table {
  background: transparent !important;
}
[data-testid="stDataFrame"] th {
  background: rgba(255,255,255,0.03) !important;
  color: #475569 !important;
  font-size: 0.72rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  font-weight: 700 !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 10px 12px !important;
}
[data-testid="stDataFrame"] td {
  font-size: 0.875rem !important;
  padding: 9px 12px !important;
  border-bottom: 1px solid rgba(255,255,255,0.04) !important;
  color: var(--txt2) !important;
}
[data-testid="stDataFrame"] tr:hover td {
  background: rgba(255,255,255,0.02) !important;
}

/* ══════════════════════════════════════════════════
   PROGRESS / LOADING
══════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, #38BDF8, #818CF8) !important;
  border-radius: 999px !important;
}
[data-testid="stProgress"] > div {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 999px !important;
}

/* ══════════════════════════════════════════════════
   MISC SCROLLBAR
══════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }

/* column gap fix */
[data-testid="column"] { padding: 0 6px !important; }
[data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="column"]:last-child  { padding-right: 0 !important; }
</style>
"""

# ════════════════════════════════════════════════════════════════════════════
# HTML Helpers
# ════════════════════════════════════════════════════════════════════════════

def _badge(label: str, color: str) -> str:
    # Determine if color is dark enough for dark text
    return f'<span class="sr-badge" style="background:{color};color:#070B14;">{label}</span>'

def _risk_badge(level: str) -> str:
    return _badge(level, RISK_COLORS.get(level.upper(), "#718096"))

def _sev_badge(sev: str) -> str:
    return _badge(sev.upper(), SEV_COLORS.get(sev.upper(), "#718096"))

def _mono(text: str) -> str:
    return f'<span class="sr-mono">{text}</span>'

def _kpi(icon, value, label, sub=""):
    sub_html = f'<div class="sr-kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="sr-card">'
        f'<span class="sr-kpi-icon">{icon}</span>'
        f'<div class="sr-kpi-val">{value}</div>'
        f'<div class="sr-kpi-label">{label}</div>'
        f'{sub_html}'
        f'</div>'
    )

def _section(title: str):
    st.markdown(f'<div class="sr-section">{title}</div>', unsafe_allow_html=True)

def _empty(msg: str, icon="📭"):
    st.markdown(
        f'<div class="sr-empty">'
        f'<span class="sr-empty-icon">{icon}</span>'
        f'<div class="sr-empty-text">{msg}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def _row(label, value):
    return (
        f'<div class="sr-row">'
        f'<span class="sr-label">{label}</span>'
        f'<span class="sr-val">{value}</span>'
        f'</div>'
    )

def _factor_bar(label, val, max_val):
    pct = min(100, int(val / max_val * 100)) if max_val else 0
    return (
        f'<div class="sr-factor-wrap">'
        f'<div class="sr-factor-hdr">'
        f'<span class="sr-factor-name">{label}</span>'
        f'<span class="sr-factor-pts">{val}/{int(max_val)}</span>'
        f'</div>'
        f'<div class="sr-factor-bg">'
        f'<div class="sr-factor-fill" style="width:{pct}%"></div>'
        f'</div></div>'
    )

def _score_color(score: int) -> str:
    if score >= 75: return RISK_COLORS["CRITICAL"]
    if score >= 50: return RISK_COLORS["HIGH"]
    if score >= 25: return RISK_COLORS["MEDIUM"]
    return RISK_COLORS["LOW"]

def _score_bar(score: int) -> str:
    c = _score_color(score)
    return (
        f'<div class="sr-score-bar-bg">'
        f'<div class="sr-score-bar-fill" style="width:{score}%;background:{c}"></div>'
        f'</div>'
    )

def _chips(items):
    return " ".join(f'<span class="sr-chip">{i}</span>' for i in items) if items else "—"

def _page_header(title: str, subtitle: str):
    st.markdown(
        f'<div class="sr-page-header">'
        f'<div class="sr-page-title">{title}</div>'
        f'<div class="sr-page-sub">{subtitle}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── DataFrame styling ────────────────────────────────────────────────────────
def _style_df(df: pd.DataFrame):
    def _cr(val):
        c = RISK_COLORS.get(str(val).upper(), "")
        return f"color:{c};font-weight:700;" if c else ""
    s = df.style
    for col in ("Risk Level", "Severity", "excursion_severity"):
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
    risk   = calculate_risk_by_id(sid)
    disrs  = get_shipment_disruptions(sid)
    routes = recommend_alternative_routes(sid)
    veh    = recommend_vehicle_for_shipment(sid)
    raw    = next((s for s in load_shipments() if s["id"] == sid), None)
    cold   = get_shipment_temperature_status(sid) if raw and raw.get("requires_cold_chain") else None
    return dict(risk=risk, disruptions=disrs, routes=routes, vehicle=veh, cold=cold, raw=raw)

def filter_scored(scored, rf, sf, pf, search=""):
    out = scored
    if rf and rf != "All":  out = [s for s in out if s["classification"] == rf]
    if sf and sf != "All":  out = [s for s in out if s.get("status","").lower() == sf.lower()]
    if pf and pf != "All":  out = [s for s in out if s.get("priority","").lower() == pf.lower()]
    if search:
        q = search.lower()
        out = [s for s in out if q in s["shipment_id"].lower() or q in s.get("description","").lower()]
    return out

def build_ai_prompt(sid, risk, disrs):
    rc  = (risk or {}).get("classification","UNKNOWN")
    rs  = (risk or {}).get("score",0)
    dt  = "; ".join(d["title"] for d in disrs) if disrs else "None"
    return (
        f"You are a supply chain risk analyst. Shipment {sid} has a risk score of "
        f"{rs}/100 ({rc}). Active disruptions: {dt}. Provide a brief, actionable "
        f"explanation for a logistics coordinator: what is happening, why it matters, "
        f"and what they should do next."
    )

# ════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    _page_header(
        "⚓ SmartRoute AI",
        "Supply Chain Control Tower — real-time risk, disruption & fleet intelligence"
    )

    risk  = cached_risk_summary()
    disr  = cached_disruption_summary()
    fleet = cached_fleet_summary()
    cold  = cached_cold_chain_summary()

    # ── Primary KPI row ──────────────────────────────────────────────────────
    _section("Overview")
    cols = st.columns(7)
    cards = [
        ("📦", risk["total_shipments"],           "Total Shipments",    ""),
        ("⚠️",  disr["total_affected_shipments"],  "At-Risk Shipments",  ""),
        ("🔴",  risk["critical_count"],            "Critical Risk",      "Needs action"),
        ("🌩️", disr["total_active_disruptions"],  "Disruptions",        "Active events"),
        ("🚢",  fleet["available"],                "Available Vessels",  ""),
        ("📊",  f'{fleet["utilisation_pct"]}%',    "Fleet Utilisation",  ""),
        ("🌡️", cold["shipments_with_excursions"], "Cold-Chain Alerts",  ""),
    ]
    for col, (icon, val, label, sub) in zip(cols, cards):
        col.markdown(_kpi(icon, val, label, sub), unsafe_allow_html=True)

    st.divider()

    # ── Risk breakdown ───────────────────────────────────────────────────────
    _section("Risk Breakdown")
    rc = st.columns(4)
    risk_cards = [
        ("🔴", risk["critical_count"], "Critical", "Score 75–100", RISK_COLORS["CRITICAL"], "rgba(248,113,113,0.15)"),
        ("🟠", risk["high_count"],     "High",     "Score 50–74",  RISK_COLORS["HIGH"],     "rgba(251,146,60,0.15)"),
        ("🟡", risk["medium_count"],   "Medium",   "Score 25–49",  RISK_COLORS["MEDIUM"],   "rgba(251,191,36,0.15)"),
        ("🟢", risk["low_count"],      "Low",      "Score 0–24",   RISK_COLORS["LOW"],      "rgba(52,211,153,0.15)"),
    ]
    total = risk["total_shipments"] or 1
    for col, (icon, cnt, label, rng, clr, bg) in zip(rc, risk_cards):
        pct = round(cnt / total * 100)
        bar_w = min(100, pct)
        col.markdown(
            f'<div class="sr-risk-card">'
            f'<div class="sr-risk-card-glow" style="background:{clr};opacity:0.7;"></div>'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f'<span style="font-size:1.4rem;">{icon}</span>'
            f'<span style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.08em;color:{clr};background:{bg};padding:3px 8px;border-radius:6px;">'
            f'{label}</span></div>'
            f'<div style="font-size:2rem;font-weight:800;color:{clr};font-family:Space Grotesk,sans-serif;'
            f'letter-spacing:-0.03em;margin:8px 0 2px;">{cnt}</div>'
            f'<div style="font-size:0.7rem;color:#475569;font-weight:600;margin-bottom:10px;">'
            f'{rng} &nbsp;·&nbsp; {pct}%</div>'
            f'<div style="background:rgba(255,255,255,0.05);border-radius:999px;height:4px;overflow:hidden;">'
            f'<div style="width:{bar_w}%;height:4px;border-radius:999px;background:{clr};opacity:0.85;"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Top at-risk shipments table ──────────────────────────────────────────
    _section("Top At-Risk Shipments")
    scored = cached_scored_shipments()
    top = [s for s in scored if s["classification"] in ("CRITICAL","HIGH")][:5]
    if not top:
        _empty("No CRITICAL or HIGH risk shipments at this time.", "✅")
    else:
        rows = []
        for s in top:
            rows.append({
                "ID":           s["shipment_id"],
                "Description":  s["description"],
                "Score":        s["score"],
                "Risk Level":   s["classification"],
                "Status":       s.get("status",""),
                "Delay (days)": s.get("delay_days",0),
                "Disruptions":  len(s.get("disruptions",[])),
            })
        df = pd.DataFrame(rows)
        st.dataframe(
            _style_df(df),
            use_container_width=True,
            hide_index=True,
            column_config={"Score": st.column_config.NumberColumn("Score", format="%d")},
        )

    st.divider()

    # ── Second row: disruptions + fleet ─────────────────────────────────────
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        _section("Disruption Summary")
        disrs = cached_disruptions()
        active_disrs = [d for d in disrs if d.get("status") in ("active","monitoring")][:4]
        if not active_disrs:
            _empty("No active disruptions.", "✅")
        else:
            for d in active_disrs:
                sc = SEV_COLORS.get(d.get("severity","").upper(),"#718096")
                st.markdown(
                    f'<div class="sr-disruption-card">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                    f'{_badge(d.get("severity","").upper(), sc)}'
                    f'<span style="color:#F1F5F9;font-weight:600;font-size:0.875rem;">{d["title"]}</span>'
                    f'</div>'
                    f'<div style="color:#475569;font-size:0.78rem;">'
                    f'{d.get("type","—")} · +{d.get("estimated_delay_days",0)}d · '
                    f'+${d.get("additional_cost_usd",0):,}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_r:
        _section("Fleet Health")
        r1, r2 = st.columns(2)
        r1.markdown(_kpi("❄️", fleet["reefer_capable_count"], "Reefer-Capable"), unsafe_allow_html=True)
        r2.markdown(_kpi("📐", fleet["available_total_teu"], "Available TEU"), unsafe_allow_html=True)

        util = cached_vehicle_utilisation()
        busy = [v for v in util if v["load_pct"] >= 85]
        idle = [v for v in util if v["is_idle"]]
        st.markdown(
            f'<div class="sr-card" style="margin-top:0;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="color:#94A3B8;font-size:0.85rem;">Fleet Utilisation</span>'
            f'<span style="font-size:1.1rem;font-weight:800;color:#F1F5F9;font-family:Space Grotesk,sans-serif;">'
            f'{fleet["utilisation_pct"]}%</span></div>'
            f'<div style="background:rgba(255,255,255,0.05);border-radius:999px;height:8px;overflow:hidden;margin:10px 0 8px;">'
            f'<div style="width:{fleet["utilisation_pct"]}%;height:8px;border-radius:999px;'
            f'background:linear-gradient(90deg,#38BDF8,#818CF8);"></div></div>'
            f'<div style="display:flex;gap:16px;">'
            f'<span style="font-size:0.76rem;color:#475569;">🔴 {len(busy)} overloaded</span>'
            f'<span style="font-size:0.76rem;color:#475569;">💤 {len(idle)} idle</span>'
            f'<span style="font-size:0.76rem;color:#475569;">✅ {fleet["available"]} available</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: Shipments
# ════════════════════════════════════════════════════════════════════════════
def page_shipments():
    _page_header(
        "📋 Shipments",
        "Risk-scored shipment register with disruption, route and AI analysis"
    )

    scored = cached_scored_shipments()

    # ── Sidebar filters ──────────────────────────────────────────────────────
    st.sidebar.markdown('<div class="sr-nav-label">Filters</div>', unsafe_allow_html=True)
    risk_levels     = ["All","CRITICAL","HIGH","MEDIUM","LOW"]
    statuses        = ["All"] + sorted({s.get("status","") for s in scored if s.get("status")})
    priorities      = ["All"] + sorted({s.get("priority","") for s in scored if s.get("priority")})
    risk_filter     = st.sidebar.selectbox("Risk Level", risk_levels, key="filter_risk")
    status_filter   = st.sidebar.selectbox("Status",     statuses,    key="filter_status")
    priority_filter = st.sidebar.selectbox("Priority",   priorities,  key="filter_priority")

    search = st.text_input(
        "Search",
        key="_shp_search",
        placeholder="🔍  Search by shipment ID or description…",
        label_visibility="collapsed",
    )
    filtered = filter_scored(scored, risk_filter, status_filter, priority_filter, search)

    _section(f"Shipment Register — {len(filtered)} results")
    if not filtered:
        _empty("No shipments match the selected filters.", "🔍")
        return

    rows = []
    for s in filtered:
        rows.append({
            "ID":           s["shipment_id"],
            "Description":  s["description"],
            "Score":        s["score"],
            "Risk Level":   s["classification"],
            "Status":       s.get("status",""),
            "Priority":     s.get("priority",""),
            "Delay (d)":    s.get("delay_days",0),
            "Disruptions":  len(s.get("disruptions",[])),
            "Cold Chain":   "❄️" if s.get("requires_cold_chain") else "—",
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        _style_df(df),
        use_container_width=True,
        hide_index=True,
        column_config={"Score": st.column_config.NumberColumn("Score", format="%d")},
    )

    # ── Detail view ──────────────────────────────────────────────────────────
    st.divider()
    _section("Shipment Detail")
    ids         = [s["shipment_id"] for s in filtered]
    selected_id = st.selectbox("Select a shipment", ids, key="sel_shipment")
    if not selected_id:
        return

    detail = get_shipment_detail(selected_id)
    risk   = detail["risk"]
    raw    = detail["raw"]

    if risk is None:
        st.error(f"Could not load risk data for {selected_id}.")
        return

    col1, col2 = st.columns(2, gap="large")

    with col1:
        _section("Shipment Info")
        orig = (raw or {}).get("origin",{})
        dest = (raw or {}).get("destination",{})
        info = "".join([
            _row("Shipment ID:",  f'<span class="sr-mono">{selected_id}</span>'),
            _row("Description:",  (raw or {}).get("description","N/A")),
            _row("Carrier:",      (raw or {}).get("carrier","N/A")),
            _row("Origin:",       f"{orig.get('city','')} · {orig.get('country','')}"),
            _row("Destination:",  f"{dest.get('city','')} · {dest.get('country','')}"),
            _row("Status:",       (raw or {}).get("status","N/A")),
            _row("Priority:",     (raw or {}).get("priority","N/A")),
            _row("Cargo Type:",   (raw or {}).get("cargo_type","N/A")),
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
            f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">'
            f'<div style="text-align:center;">'
            f'<div style="font-size:2.4rem;font-weight:800;color:{clr};'
            f'font-family:Space Grotesk,sans-serif;letter-spacing:-0.04em;line-height:1;">{sc}</div>'
            f'<div style="font-size:0.68rem;color:#475569;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.06em;">/ 100</div></div>'
            f'<div>{_badge(cls, clr)}'
            f'<div style="font-size:0.78rem;color:#475569;margin-top:5px;">Risk Score</div>'
            f'</div></div>'
            f'{bars}</div>',
            unsafe_allow_html=True,
        )

    # Active disruptions
    _section("Active Disruptions")
    disrs = detail["disruptions"]
    if not disrs:
        _empty("No active disruptions affecting this shipment.", "✅")
    else:
        for d in disrs:
            sc2 = SEV_COLORS.get(d["severity"].upper(),"#718096")
            st.markdown(
                f'<div class="sr-disruption-card" style="border-left:3px solid {sc2};border-radius:0 {14}px {14}px 0;">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                f'{_badge(d["severity"].upper(), sc2)}'
                f'<strong style="color:#F1F5F9;">{d["title"]}</strong>'
                f'<span style="color:#475569;font-size:.8rem;margin-left:4px;">'
                f'{d["type"]} · +{d["estimated_delay_days"]}d · +${d["additional_cost_usd"]:,}</span>'
                f'</div>'
                f'<div style="color:#64748B;font-size:.86rem;line-height:1.55;">{d["description"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Route alternatives
    _section("Route Alternatives")
    routes = detail["routes"]
    alts   = routes.get("alternatives",[])
    if not alts:
        if routes.get("action_required"):
            _empty("No pre-defined alternatives — contact carrier directly.", "📞")
        else:
            _empty("No rerouting required — shipment is on schedule.", "✅")
    else:
        for i, alt in enumerate(alts, 1):
            ed    = alt["extra_delay_days"]
            d_str = f"+{ed}d" if ed >= 0 else f"{abs(ed)}d faster"
            d_clr = RISK_COLORS["HIGH"] if ed > 0 else RISK_COLORS["LOW"]
            cost_str = "+${:,}".format(alt["extra_cost_usd"])
            with st.expander(f"Option {i}: {alt['description']}  ·  {d_str}  ·  {cost_str}"):
                st.markdown(
                    f'{_badge(d_str, d_clr)}&nbsp;{_badge(cost_str,"#1E3A5F")}'
                    f'<div style="color:#64748B;margin-top:10px;line-height:1.6;font-size:.875rem;">'
                    f'{alt["reason"]}</div>',
                    unsafe_allow_html=True,
                )
                veh_list = alt.get("available_vehicles",[])
                if veh_list:
                    v_html = " ".join(f'<span class="sr-chip">🚢 {v["name"]}</span>' for v in veh_list)
                    st.markdown(f'<div style="margin-top:8px;">Vessels: {v_html}</div>', unsafe_allow_html=True)
                else:
                    carriers = _chips(alt.get("suggested_carriers",[]))
                    st.markdown(f'<div style="margin-top:8px;color:#64748B;font-size:.85rem;">Carriers: {carriers}</div>', unsafe_allow_html=True)
                if alt.get("via"):
                    st.markdown(f'<div style="color:#475569;font-size:.82rem;margin-top:4px;">Via: <strong style="color:#94A3B8">{alt["via"]}</strong></div>', unsafe_allow_html=True)

    # Vehicle recommendation
    _section("Vehicle Recommendation")
    vr   = detail["vehicle"]
    best = vr.get("recommended_vehicle")
    if best:
        alts_v   = vr.get("alternatives",[])
        alt_html = ""
        for a in alts_v:
            alt_html += (
                f'<div style="color:#64748B;font-size:.84rem;padding:8px 0;'
                f'border-top:1px solid rgba(255,255,255,.05);margin-top:4px;">'
                f'🚢 <strong style="color:#94A3B8">{a["name"]}</strong> ({a["carrier"]}) · '
                f'{a["available_teu"]} TEU · '
                f'Departs {a.get("next_departure","TBD")} from {a["current_location"]}'
                f'</div>'
            )
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid #38BDF8;border-radius:0 14px 14px 0;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'<span style="color:#38BDF8;font-size:.7rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.08em;">✔ Recommended</span></div>'
            f'<div style="color:#F1F5F9;font-size:.9rem;line-height:1.6;">{vr["reason"]}</div>'
            f'{alt_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        _empty(vr.get("reason","No vehicle recommendation available."), "🔍")

    # Cold chain
    cold = detail["cold"]
    if cold:
        _section("Cold-Chain Status")
        sc3 = SEV_COLORS.get(cold["excursion_severity"],"#718096")
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid {sc3};border-radius:0 14px 14px 0;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'{_badge(cold["excursion_severity"], sc3)}'
            f'</div>'
            f'<div style="color:#94A3B8;font-size:.88rem;line-height:1.6;">{cold["explanation"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # AI explanation
    st.divider()
    ai_configured = is_watsonx_configured()
    pill = (
        '<span class="sr-pill-wx">● watsonx.ai</span>'
        if ai_configured else
        '<span class="sr-pill-demo">○ Demo Mode</span>'
    )
    st.markdown(
        f'<div class="sr-ai-section">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<span style="font-weight:700;color:#F1F5F9;font-size:.98rem;font-family:Space Grotesk,sans-serif;">'
        f'AI Risk Explanation</span>'
        f'{pill}</div>',
        unsafe_allow_html=True,
    )
    ai_label = "watsonx.ai" if ai_configured else "Demo AI"
    if st.button(f"Generate Explanation via {ai_label}", key=f"ai_{selected_id}"):
        prompt = build_ai_prompt(selected_id, risk, disrs)
        with st.spinner("Analysing with AI…"):
            result = generate_ai_explanation(prompt)
        src_pill = (
            '<span class="sr-pill-wx">● watsonx.ai</span>'
            if result["source"] == "watsonx" else
            '<span class="sr-pill-demo">○ Demo Mode</span>'
        )
        st.markdown(
            f'<div class="sr-ai-response">'
            f'<div style="margin-bottom:10px;">{src_pill}</div>'
            f'<div class="sr-ai-response-text">{result["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if result.get("error"):
            st.caption(f"Note: {result['error']}")
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: Disruptions
# ════════════════════════════════════════════════════════════════════════════
def page_disruptions():
    _page_header(
        "🌩️ Active Disruptions",
        "Real-time port, weather, strike and vessel disruption tracking"
    )

    disruptions = cached_disruptions()
    active      = [d for d in disruptions if d.get("status") in ("active","monitoring")]
    summary     = cached_disruption_summary()

    cols = st.columns(4)
    kpis = [
        ("🌩️", summary["total_active_disruptions"], "Active Disruptions", ""),
        ("📦",  summary["total_affected_shipments"], "Affected Shipments",  ""),
        ("🔴",  summary["critical_count"],           "Critical",            ""),
        ("🟠",  summary["high_count"],               "High",                ""),
    ]
    for col, (icon, val, label, sub) in zip(cols, kpis):
        col.markdown(_kpi(icon, val, label, sub), unsafe_allow_html=True)

    st.divider()
    if not active:
        _empty("No active disruptions at this time.", "✅")
        return

    _section("Disruption Register")
    rows = []
    for d in active:
        rows.append({
            "ID":               d["id"],
            "Type":             d.get("type",""),
            "Title":            d.get("title",""),
            "Severity":         d.get("severity","").upper(),
            "Status":           d.get("status",""),
            "Est. Delay (d)":   d.get("estimated_delay_days",0),
            "Add. Cost ($)":    d.get("additional_cost_usd",0),
            "Affected Routes":  len(d.get("affected_routes",[])),
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        _style_df(df),
        use_container_width=True,
        hide_index=True,
        column_config={"Add. Cost ($)": st.column_config.NumberColumn(format="$%d")},
    )

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
        f'<div class="sr-disruption-card" style="border-left:3px solid {sc};border-radius:0 14px 14px 0;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
        f'{_badge(d.get("severity","").upper(), sc)}'
        f'<strong style="color:#F1F5F9;font-size:1rem;">{d["title"]}</strong>'
        f'&nbsp;<span class="sr-mono">{d["id"]}</span>'
        f'</div>'
        f'<div style="color:#64748B;line-height:1.6;font-size:.875rem;">{d.get("description","")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")
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
            + _row("Affected Ports:",    _chips(d.get("affected_ports",[])))
            + _row("Affected Routes:",   _chips(d.get("affected_routes",[])))
            + _row("Affected Carriers:", _chips(d.get("affected_carriers",[])))
            + _row("Affected Vessels:",  _chips(d.get("affected_vessel_ids",[])))
            + f'</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: Fleet
# ════════════════════════════════════════════════════════════════════════════
def page_fleet():
    _page_header(
        "🚢 Fleet Management",
        "Vehicle utilisation, availability and assignment tracking"
    )

    fleet = cached_fleet_summary()
    cols  = st.columns(5)
    for col, (icon, val, label) in zip(cols, [
        ("🚢", fleet["total"],                "Total Vehicles"),
        ("✅", fleet["available"],            "Available"),
        ("📦", fleet["assigned"],             "Assigned"),
        ("💤", fleet["idle"],                 "Idle"),
        ("📊", f'{fleet["utilisation_pct"]}%',"Utilisation"),
    ]):
        col.markdown(_kpi(icon, val, label), unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    r1.markdown(_kpi("❄️", fleet["reefer_capable_count"],             "Reefer-Capable"),    unsafe_allow_html=True)
    r2.markdown(_kpi("📐", fleet["available_total_teu"],              "Available TEU"),     unsafe_allow_html=True)
    r3.markdown(_kpi("⚖️", f'{fleet["available_total_weight_kg"]:,}', "Avail. Weight (kg)"), unsafe_allow_html=True)

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
    st.dataframe(
        styler,
        use_container_width=True,
        hide_index=True,
        column_config={"Load %": st.column_config.ProgressColumn("Load %", min_value=0, max_value=100, format="%.1f%%")},
    )

    st.divider()
    _section("Vehicle Recommendation Picker")
    shp_ids = [s["id"] for s in cached_shipments()]
    sel_shp = st.selectbox("Select a shipment to find the best vehicle", shp_ids, key="fleet_shp")
    if not sel_shp:
        return

    rec  = recommend_vehicle_for_shipment(sel_shp)
    best = rec.get("recommended_vehicle")
    if best:
        alts     = rec.get("alternatives",[])
        alt_html = ""
        for a in alts:
            alt_html += (
                f'<div style="color:#64748B;font-size:.84rem;padding:8px 0;'
                f'border-top:1px solid rgba(255,255,255,.05);margin-top:4px;">'
                f'🚢 <strong style="color:#94A3B8;">{a["name"]}</strong> ({a["carrier"]}) · '
                f'{a["available_teu"]} TEU · '
                f'departs {a.get("next_departure","TBD")} from {a["current_location"]}'
                f'</div>'
            )
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid #38BDF8;border-radius:0 14px 14px 0;">'
            f'<div style="color:#38BDF8;font-size:.7rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.08em;margin-bottom:8px;">✔ Recommended</div>'
            f'<div style="color:#F1F5F9;font-size:.9rem;line-height:1.6;">{rec["reason"]}</div>'
            f'{alt_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        _empty(rec.get("reason","No vehicle found."), "🔍")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: Cold Chain
# ════════════════════════════════════════════════════════════════════════════
def page_cold_chain():
    _page_header(
        "🌡️ Cold-Chain Monitor",
        "Temperature excursion alerts and shipment cold-chain history"
    )

    summary = cached_cold_chain_summary()
    cols    = st.columns(4)
    for col, (icon, val, label) in zip(cols, [
        ("📦", summary["total_tracked"],          "Tracked Shipments"),
        ("🟢", summary["normal_count"],           "Normal"),
        ("🟡", summary["warning_count"],          "Warning"),
        ("🔴", summary["critical_count"],         "Critical Excursions"),
    ]):
        col.markdown(_kpi(icon, val, label), unsafe_allow_html=True)

    st.divider()
    _section("Temperature Alerts")
    alerts = cached_temperature_alerts()
    if not alerts:
        _empty("No temperature excursions — all cold-chain shipments within safe range.", "✅")
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

    st.markdown(
        f'<div class="sr-card" style="border-left:3px solid {sev_clr};border-radius:0 14px 14px 0;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
        f'{_badge(status["excursion_severity"], sev_clr)}'
        f'<span style="color:#94A3B8;font-size:.875rem;">{status["explanation"]}</span>'
        f'</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:16px;color:#475569;font-size:.8rem;">'
        f'<span>Safe range: <strong style="color:#94A3B8">{t_min} °C – {t_max} °C</strong></span>'
        f'<span>Risk: <strong style="color:#38BDF8">{status["cold_chain_risk_score"]}/100</strong></span>'
        f'<span>Latest: <strong style="color:#F1F5F9">{status.get("latest_temp_c","—")} °C</strong></span>'
        f'<span>Min observed: {status.get("min_observed_c","—")} °C</span>'
        f'<span>Max observed: {status.get("max_observed_c","—")} °C</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    readings = status["readings"]
    if not readings:
        _empty("No readings recorded for this shipment.", "📭")
        return

    chart_rows = []
    for i, r in enumerate(readings):
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
        RISK_COLORS["CRITICAL"] if str(s).lower() == "critical"
        else RISK_COLORS["HIGH"] if str(s).lower() in ("warning","excursion","high")
        else RISK_COLORS["LOW"]
        for s in statuses
    ]

    fig = go.Figure()

    if t_min is not None and t_max is not None:
        fig.add_trace(go.Scatter(
            x=labels+labels[::-1], y=[t_max]*len(labels)+[t_min]*len(labels),
            fill="toself", fillcolor="rgba(52,211,153,0.07)",
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

    fig.add_trace(go.Scatter(
        x=labels, y=temps, mode="lines+markers",
        line=dict(color="#38BDF8", width=2.5),
        marker=dict(color=pt_colors, size=7, line=dict(color="#070B14", width=1.5)),
        name="Temperature (°C)",
        hovertext=tooltips, hoverinfo="text",
    ))

    fig.update_layout(
        plot_bgcolor="#0D1424",
        paper_bgcolor="#0D1424",
        font=dict(color="#475569", family="Inter,sans-serif", size=12),
        xaxis=dict(
            title="Reading #",
            gridcolor="rgba(255,255,255,0.04)",
            showline=True, linecolor="rgba(255,255,255,0.07)",
            tickfont=dict(color="#475569"),
            title_font=dict(color="#475569"),
        ),
        yaxis=dict(
            title="Temperature (°C)",
            gridcolor="rgba(255,255,255,0.04)",
            showline=True, linecolor="rgba(255,255,255,0.07)",
            tickfont=dict(color="#475569"),
            title_font=dict(color="#475569"),
        ),
        legend=dict(
            bgcolor="rgba(13,20,36,0.8)",
            bordercolor="rgba(255,255,255,.07)",
            borderwidth=1,
            font=dict(size=11, color="#64748B"),
        ),
        margin=dict(l=10, r=10, t=16, b=10),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Safe range: {t_min} °C – {t_max} °C  ·  "
        f"Readings: {status['reading_count']}  ·  "
        f"Excursions: {status['excursion_count']}"
    )

    with st.expander("Raw readings table"):
        st.dataframe(df_chart, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# Sidebar
# ════════════════════════════════════════════════════════════════════════════
NAV_ICONS = {
    "Dashboard":   "◈",
    "Shipments":   "◻",
    "Disruptions": "◬",
    "Fleet":       "◉",
    "Cold Chain":  "◎",
}

def render_sidebar(pages, ai_on):
    with st.sidebar:
        # Logo area
        pill_class = "sr-ai-status sr-ai-status-live" if ai_on else "sr-ai-status"
        dot_class  = "sr-ai-dot" if ai_on else "sr-ai-dot sr-ai-dot-demo"
        ai_lbl_class = "sr-ai-label" if ai_on else "sr-ai-label sr-ai-label-demo"
        ai_text    = "watsonx.ai Connected" if ai_on else "Demo Mode · Mock AI"
        ai_sub     = "IBM watsonx.ai  ·  Live" if ai_on else "Simulation data active"

        st.markdown(
            f'<div class="sr-sidebar-logo">'
            f'<div class="sr-sidebar-logo-icon">⚓</div>'
            f'<div class="sr-sidebar-brand">SmartRoute AI</div>'
            f'<div class="sr-sidebar-tagline">Supply Chain Control Tower</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sr-nav-label">Navigation</div>', unsafe_allow_html=True)
        page = st.radio(
            "Navigate",
            list(pages.keys()),
            key="nav",
            label_visibility="collapsed",
        )

        st.markdown(
            f'<div class="{pill_class}">'
            f'<div><span class="{dot_class}"></span>'
            f'<span class="{ai_lbl_class}">{ai_text}</span></div>'
            f'<div class="sr-ai-sub">{ai_sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="sr-sidebar-footer">'
            f'<div class="sr-sidebar-footer-txt">Team PI-NANT · IBM Hackathon · AI Track</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    return page


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

    ai_on = is_watsonx_configured()
    page  = render_sidebar(pages, ai_on)
    pages[page]()


main()
