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
from core.decision_engine import analyse_shipment, build_watsonx_prompt, is_valid_analysis
from core.report_exporter import generate_executive_report_html, generate_executive_report_markdown

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

/* ── Hide sidebar entirely ── */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarContent"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
  display: none !important;
  width: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stHeader"],
header[data-testid="stHeader"] {
  visibility: hidden !important;
  display: none !important;
  height: 0 !important;
  pointer-events: none !important;
}

/* ── Main content: no top gap since our nav is inline ── */
[data-testid="stMain"] > div {
  padding-top: 0 !important;
}
section[data-testid="stMainBlockContainer"] {
  padding: 0.5rem 2.2rem 2rem 2.2rem !important;
  max-width: 1440px !important;
}

/* ═══════════════════════════════════════════════════
   TOP NAV BAR
═══════════════════════════════════════════════════ */
.sr-topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(13,20,36,0.97);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding: 0 28px;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 9999;
  margin-bottom: 0;
  gap: 20px;
}
.sr-topnav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  min-width: 190px;
}
.sr-topnav-logo {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 14px rgba(56,189,248,0.35);
  flex-shrink: 0;
}
.sr-topnav-name {
  display: flex; flex-direction: column; line-height: 1;
}
.sr-topnav-title {
  font-family: 'Space Grotesk', system-ui, sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: #F1F5F9;
  letter-spacing: -0.01em;
}
.sr-topnav-sub {
  font-size: 0.6rem;
  color: #475569;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin-top: 2px;
}
.sr-topnav-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  justify-content: center;
}
.sr-topnav-tab {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 18px;
  border-radius: 9px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748B;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.18s ease;
  text-decoration: none !important;
  white-space: nowrap;
  background: transparent;
}
.sr-topnav-tab:hover {
  color: #94A3B8;
  background: rgba(255,255,255,0.04);
  border-color: rgba(255,255,255,0.06);
}
.sr-topnav-tab.active {
  color: #38BDF8;
  background: rgba(56,189,248,0.1);
  border-color: rgba(56,189,248,0.25);
  box-shadow: 0 0 12px rgba(56,189,248,0.15);
}
.sr-topnav-tab-icon {
  font-size: 0.95rem;
  opacity: 0.85;
}
.sr-topnav-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  min-width: 190px;
  justify-content: flex-end;
}
.sr-demo-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(251,191,36,0.12);
  border: 1px solid rgba(251,191,36,0.3);
  border-radius: 99px;
  padding: 4px 12px;
  font-size: 0.72rem;
  font-weight: 700;
  color: #FBBF24;
  letter-spacing: 0.02em;
}
.sr-demo-pill-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #FBBF24;
  box-shadow: 0 0 6px #FBBF24;
  animation: pulse-dot 2s infinite;
}
.sr-team-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
  letter-spacing: 0.02em;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
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

/* ── Buttons (general) ── */
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

/* ── Top-nav tab buttons ── */
/* secondary = inactive tab */
[data-testid="stBaseButton-secondary"] > button,
button[data-testid="stBaseButton-secondary"] {
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 9px !important;
  color: #64748B !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  padding: 8px 14px !important;
  box-shadow: none !important;
  transition: all 0.18s ease !important;
  letter-spacing: 0 !important;
}
[data-testid="stBaseButton-secondary"] > button:hover,
button[data-testid="stBaseButton-secondary"]:hover {
  background: rgba(255,255,255,0.05) !important;
  color: #CBD5E1 !important;
  border-color: rgba(255,255,255,0.1) !important;
  transform: none !important;
  box-shadow: none !important;
}
/* primary = active tab */
[data-testid="stBaseButton-primary"] > button,
button[data-testid="stBaseButton-primary"] {
  background: rgba(56,189,248,0.12) !important;
  border: 1px solid rgba(56,189,248,0.35) !important;
  border-radius: 9px !important;
  color: #38BDF8 !important;
  font-size: 0.875rem !important;
  font-weight: 700 !important;
  padding: 8px 14px !important;
  box-shadow: 0 0 12px rgba(56,189,248,0.15) !important;
  transition: all 0.18s ease !important;
  letter-spacing: 0 !important;
}
[data-testid="stBaseButton-primary"] > button:hover,
button[data-testid="stBaseButton-primary"]:hover {
  background: rgba(56,189,248,0.2) !important;
  box-shadow: 0 0 18px rgba(56,189,248,0.25) !important;
  transform: none !important;
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

/* ══════════════════════════════════════════════════
   PAGE HEADER
══════════════════════════════════════════════════ */
.sr-page-header {
  margin-top: 0;
  margin-bottom: 24px;
  padding-top: 4px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  overflow: visible !important;
}
.sr-page-title {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  font-size: 1.85rem !important;
  font-weight: 800 !important;
  color: #F1F5F9 !important;
  letter-spacing: -0.02em !important;
  line-height: 1.35 !important;
  margin: 0 0 6px 0 !important;
  padding: 0 !important;
  overflow: visible !important;
}
.sr-page-sub {
  color: #94A3B8 !important;
  font-size: 0.88rem !important;
  font-weight: 400 !important;
  margin: 0 !important;
  line-height: 1.5 !important;
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

/* ══════════════════════════════════════════════════
   ACTION CARD
══════════════════════════════════════════════════ */
.sr-action-card {
  background: var(--card);
  border: 1px solid rgba(56,189,248,0.18);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 10px;
  position: relative;
  overflow: hidden;
}
.sr-action-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, #38BDF8, #818CF8);
}
.sr-action-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #F1F5F9;
  margin-bottom: 6px;
}
.sr-action-reason {
  color: #94A3B8;
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 10px;
}
.sr-action-factors {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

/* ══════════════════════════════════════════════════
   ESCALATION BANNER
══════════════════════════════════════════════════ */
.sr-escalation-banner {
  background: rgba(248,113,113,0.1);
  border: 1px solid rgba(248,113,113,0.3);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.sr-escalation-icon { font-size: 1.4rem; flex-shrink: 0; }
.sr-escalation-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  color: #F87171;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.sr-escalation-reasons {
  color: #94A3B8;
  font-size: 0.82rem;
  line-height: 1.6;
}

/* ══════════════════════════════════════════════════
   DATA STATUS BADGE
══════════════════════════════════════════════════ */
.sr-data-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(251,191,36,0.08);
  border: 1px solid rgba(251,191,36,0.2);
  border-radius: 6px;
  padding: 3px 9px;
  font-size: 0.68rem;
  font-weight: 700;
  color: #FBBF24;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ══════════════════════════════════════════════════
   RISK NARRATIVE
══════════════════════════════════════════════════ */
.sr-risk-narrative {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 14px 16px;
  margin-top: 12px;
  color: #94A3B8;
  font-size: 0.855rem;
  line-height: 1.7;
  font-style: italic;
}

/* ══════════════════════════════════════════════════
   VEHICLE DETAIL
══════════════════════════════════════════════════ */
.sr-vehicle-attr {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 10px;
}
.sr-vehicle-attr-item {
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  padding: 8px 12px;
}
.sr-vehicle-attr-label {
  font-size: 0.68rem;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  font-weight: 600;
  margin-bottom: 3px;
}
.sr-vehicle-attr-val {
  font-size: 0.875rem;
  font-weight: 600;
  color: #F1F5F9;
}

/* ══════════════════════════════════════════════════
   MCP TOOL LIST
══════════════════════════════════════════════════ */
.sr-mcp-tool {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.sr-mcp-tool:last-child { border-bottom: none; }
.sr-mcp-check {
  color: #34D399;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 1px;
}
.sr-mcp-name {
  font-weight: 600;
  color: #94A3B8;
  font-size: 0.82rem;
  font-family: 'JetBrains Mono', monospace;
}
.sr-mcp-desc {
  color: #475569;
  font-size: 0.78rem;
  margin-top: 2px;
}
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
    """Aggregate full shipment analysis using the decision engine."""
    analysis = analyse_shipment(sid)
    # Keep backward-compatible keys for existing Dashboard/other code paths
    return dict(
        risk=calculate_risk_by_id(sid),
        disruptions=get_shipment_disruptions(sid),
        routes=recommend_alternative_routes(sid),
        vehicle=recommend_vehicle_for_shipment(sid),
        cold=analysis.get("cold_chain"),
        raw=analysis.get("shipment"),
        analysis=analysis,   # full structured result
    )

def filter_scored(scored, rf, sf, pf, search=""):
    out = scored
    if rf and rf != "All":  out = [s for s in out if s["classification"] == rf]
    if sf and sf != "All":  out = [s for s in out if s.get("status","").lower() == sf.lower()]
    if pf and pf != "All":  out = [s for s in out if s.get("priority","").lower() == pf.lower()]
    if search:
        q = search.lower()
        out = [s for s in out if q in s["shipment_id"].lower() or q in s.get("description","").lower()]
    return out

def build_ai_prompt(sid, risk, disrs, analysis=None):
    """Build a rich AI prompt. Uses the decision engine analysis when available."""
    if analysis and is_valid_analysis(analysis):
        return build_watsonx_prompt(analysis)
    # Fallback to the original simple prompt for backward compatibility
    rc  = (risk or {}).get("classification","UNKNOWN")
    rs  = (risk or {}).get("score",0)
    dt  = "; ".join(d["title"] for d in disrs) if disrs else "None"
    return (
        f"You are a supply chain risk analyst. Shipment {sid} has a risk score of "
        f"{rs}/100 ({rc}). Active disruptions: {dt}. Provide a brief, actionable "
        f"explanation for a logistics coordinator: what is happening, why it matters, "
        f"and what they should do next."
    )

# ── City coordinates for the map ─────────────────────────────────────────────
_CITY_COORDS = {
    "Shanghai":    (31.23,  121.47),
    "Los Angeles": (34.05, -118.24),
    "Hamburg":     (53.55,    9.99),
    "Mumbai":      (19.08,   72.88),
    "Detroit":     (42.33,  -83.05),
    "Frankfurt":   (50.11,    8.68),
    "Santos":      (-23.96, -46.33),
    "Rotterdam":   (51.92,    4.48),
    "Osaka":       (34.69,  135.50),
    "Sydney":      (-33.87, 151.21),
    "Dhaka":       (23.72,   90.41),
    "New York":    (40.71,  -74.01),
    "Lima":        (-12.05, -77.04),
    "Tianjin":     (39.09,  117.20),
}

def _render_global_map(scored: list) -> None:
    """Render the dark Plotly Scattergeo world map with shipment hotspot pins."""
    shipments = load_shipments()
    risk_map = {s["shipment_id"]: s for s in scored}

    # Build node data (one per unique city that appears as origin or destination)
    seen: dict[str, dict] = {}
    for shp in shipments:
        sid   = shp["id"]
        score = risk_map.get(sid, {}).get("score", 0)
        clsf  = risk_map.get(sid, {}).get("classification", "LOW")
        color = RISK_COLORS.get(clsf, "#34D399")

        for role in ("origin", "destination"):
            city = shp[role]["city"]
            coords = _CITY_COORDS.get(city)
            if not coords:
                continue
            key = city
            if key not in seen:
                seen[key] = {
                    "city": city, "lat": coords[0], "lon": coords[1],
                    "max_score": score, "color": color, "shipments": [sid],
                }
            else:
                if score > seen[key]["max_score"]:
                    seen[key]["max_score"] = score
                    seen[key]["color"]     = color
                seen[key]["shipments"].append(sid)

    nodes = list(seen.values())

    # Route lines
    line_lats, line_lons = [], []
    for shp in shipments:
        o_city = shp["origin"]["city"]
        d_city = shp["destination"]["city"]
        o_c = _CITY_COORDS.get(o_city)
        d_c = _CITY_COORDS.get(d_city)
        if o_c and d_c:
            line_lats += [o_c[0], d_c[0], None]
            line_lons += [o_c[1], d_c[1], None]

    fig = go.Figure()

    # Route lines
    if line_lats:
        fig.add_trace(go.Scattergeo(
            lat=line_lats, lon=line_lons,
            mode="lines",
            line=dict(width=1.2, color="rgba(56,189,248,0.22)"),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Hotspot pins — sized by risk score
    if nodes:
        pin_sizes  = [max(10, min(26, 8 + n["max_score"] // 8)) for n in nodes]
        pin_colors = [n["color"] for n in nodes]
        pin_text   = [
            f"<b>{n['city']}</b><br>Score: {n['max_score']}<br>Shipments: {', '.join(n['shipments'])}"
            for n in nodes
        ]
        fig.add_trace(go.Scattergeo(
            lat=[n["lat"] for n in nodes],
            lon=[n["lon"] for n in nodes],
            mode="markers",
            marker=dict(
                size=pin_sizes,
                color=pin_colors,
                opacity=0.92,
                line=dict(width=1.5, color="rgba(0,0,0,0.5)"),
            ),
            text=pin_text,
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
        paper_bgcolor="#070B14",
        plot_bgcolor="#070B14",
        geo=dict(
            projection_type="natural earth",
            showland=True,    landcolor="#0D1424",
            showocean=True,   oceancolor="#070B14",
            showcountries=True, countrycolor="rgba(255,255,255,0.07)",
            showcoastlines=True, coastlinecolor="rgba(255,255,255,0.1)",
            showframe=True,   framecolor="rgba(255,255,255,0.1)",
            bgcolor="#070B14",
            lataxis=dict(range=[-60, 80]),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


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

    # ── Global Control Tower Map ──────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.12em;color:#334155;margin-bottom:8px;">'
        'GLOBAL CONTROL TOWER MAP — ACTIVE ROUTES &amp; HOTSPOTS</div>',
        unsafe_allow_html=True,
    )
    scored = cached_scored_shipments()
    _render_global_map(scored)

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
        "Shipments Register",
        "Risk-scored register — disruptions, routes & AI explanations"
    )

    scored = cached_scored_shipments()

    # ── Inline filter expander (matching screenshot) ──────────────────────────
    with st.expander("🔍  Filter Shipments Register", expanded=False):
        risk_levels     = ["All","CRITICAL","HIGH","MEDIUM","LOW"]
        statuses        = ["All"] + sorted({s.get("status","") for s in scored if s.get("status")})
        priorities      = ["All"] + sorted({s.get("priority","") for s in scored if s.get("priority")})
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            risk_filter = st.selectbox("Risk Level", risk_levels, key="filter_risk")
        with fc2:
            status_filter = st.selectbox("Status", statuses, key="filter_status")
        with fc3:
            priority_filter = st.selectbox("Priority", priorities, key="filter_priority")

    st.markdown('<div style="font-size:0.8rem;color:#475569;margin-bottom:4px;">Search shipment ID or description</div>', unsafe_allow_html=True)
    search = st.text_input(
        "Search shipment ID or description",
        key="_shp_search",
        placeholder="e.g. SHP-001 or pharma…",
        label_visibility="collapsed",
    )
    filtered = filter_scored(scored, risk_filter, status_filter, priority_filter, search)

    # ── Toolbar ──────────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:0.75rem;color:#334155;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-top:12px;margin-bottom:6px;font-weight:700;">'
        f'ALL SHIPMENTS — {len(filtered)} SHOWN</div>',
        unsafe_allow_html=True,
    )
    tb_left, tb_right = st.columns([1, 1])
    with tb_left:
        if st.button("🔄 Refresh Data", key="btn_refresh"):
            st.cache_data.clear()
            st.rerun()
    with tb_right:
        csv_data = pd.DataFrame([{
            "ID": s["shipment_id"], "Description": s["description"],
            "Score": s["score"], "Risk Level": s["classification"],
            "Status": s.get("status",""), "Priority": s.get("priority",""),
            "Delay (d)": s.get("delay_days",0), "Disruptions": len(s.get("disruptions",[])),
        } for s in filtered]).to_csv(index=False).encode()
        st.download_button("📥 Export CSV", csv_data, "shipments.csv", "text/csv", key="btn_export_csv")

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

    if "sel_shipment" in st.session_state and st.session_state["sel_shipment"] not in ids:
        del st.session_state["sel_shipment"]

    # Pre-select a high-risk shipment for demo convenience (SHP-006 or SHP-004)
    _demo_default = next(
        (s["shipment_id"] for s in filtered
         if s["classification"] in ("CRITICAL", "HIGH")), ids[0] if ids else None
    )
    default_idx = ids.index(_demo_default) if _demo_default in ids else 0
    selected_id = st.selectbox("Select a shipment", ids, index=default_idx, key="sel_shipment")
    if not selected_id:
        return

    detail   = get_shipment_detail(selected_id)
    risk     = detail["risk"]
    raw      = detail["raw"]
    analysis = detail.get("analysis", {})

    if risk is None:
        st.error(f"Could not load risk data for {selected_id}.")
        return

    # ── 1. SHIPMENT HEADER ────────────────────────────────────────────────────
    _section("Shipment Overview")
    orig = (raw or {}).get("origin",{})
    dest = (raw or {}).get("destination",{})
    orig_str = f"{orig.get('city','')} → {dest.get('city','')}"
    desc     = (raw or {}).get("description","")
    carrier  = (raw or {}).get("carrier","")
    cargo    = (raw or {}).get("cargo_type","")
    priority = (raw or {}).get("priority","")
    status   = (raw or {}).get("status","")
    delay    = int((raw or {}).get("delay_days",0))
    cold_req = bool((raw or {}).get("requires_cold_chain",False))

    col_hdr1, col_hdr2 = st.columns([2, 1], gap="large")
    with col_hdr1:
        info_html = "".join([
            _row("Shipment ID:",  f'<span class="sr-mono">{selected_id}</span>'),
            _row("Description:",  desc or "N/A"),
            _row("Route:",        orig_str + f" ({orig.get('country','')}/{dest.get('country','')})"),
            _row("Carrier:",      carrier or "N/A"),
            _row("Status:",       status.replace("_"," ").title() if status else "N/A"),
            _row("Priority:",     priority.upper() if priority else "N/A"),
            _row("Cargo Type:",   cargo or "N/A"),
            _row("Cold Chain:",   "❄️ Required" if cold_req else "Not required"),
            _row("Delay:",        f"{delay} day(s)" if delay else "On schedule"),
        ])
        st.markdown(
            f'<div class="sr-card">{info_html}'
            f'<div style="margin-top:8px;"><span class="sr-data-status">📁 DEMO DATA — Local JSON</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_hdr2:
        # ── 2. RISK SCORE ────────────────────────────────────────────────────
        _section("Risk Assessment")
        fb  = risk.get("factor_breakdown",{})
        sc  = risk["score"]
        cls = risk["classification"]
        clr = RISK_COLORS.get(cls,"#718096")
        bars = "".join([
            _factor_bar("Disruption Severity", fb.get("disruption_severity",0), 35),
            _factor_bar("Delay Impact",         fb.get("delay",0),              25),
            _factor_bar("Deadline Pressure",    fb.get("deadline_pressure",0),  20),
            _factor_bar("Priority",             fb.get("priority",0),           15),
            _factor_bar("Cold Chain",           fb.get("cold_chain",0),          5),
        ])
        st.markdown(
            f'<div class="sr-card">'
            f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
            f'<div style="text-align:center;">'
            f'<div style="font-size:2.6rem;font-weight:800;color:{clr};'
            f'font-family:Space Grotesk,sans-serif;letter-spacing:-0.04em;line-height:1;">{sc}</div>'
            f'<div style="font-size:0.65rem;color:#475569;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.06em;">/ 100</div></div>'
            f'<div>{_badge(cls, clr)}'
            f'<div style="font-size:0.75rem;color:#475569;margin-top:4px;">Risk Score</div>'
            f'</div></div>'
            f'{bars}'
            f'{_score_bar(sc)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── "Why is this shipment at risk?" ──────────────────────────────────────
    if analysis.get("risk_explanation"):
        # Extract just the contributing factor lines — skip the header line
        full_expl = analysis["risk_explanation"]
        # Build a readable summary of the top driving factors
        dominant_factors = [
            f for f, v in [
                ("Disruption severity", fb.get("disruption_severity",0)),
                ("Current delay",       fb.get("delay",0)),
                ("Deadline pressure",   fb.get("deadline_pressure",0)),
                ("Cargo priority",      fb.get("priority",0)),
                ("Cold-chain status",   fb.get("cold_chain",0)),
            ] if v > 0
        ]
        sf = analysis.get("supporting_factors",[])
        narrative = " · ".join(sf) if sf else "Refer to factor breakdown above."
        _section("Why Is This Shipment At Risk?")
        st.markdown(
            f'<div class="sr-risk-narrative">'
            f'<strong style="color:#F1F5F9;font-style:normal;">'
            f'Top contributing factors:</strong> '
            + (" | ".join(dominant_factors) if dominant_factors else "None identified") +
            f'<br><br>{narrative}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── 3. ACTIVE DISRUPTIONS ────────────────────────────────────────────────
    _section("Active Disruptions")
    disrs = detail["disruptions"]
    if not disrs:
        _empty("No active disruptions affecting this shipment.", "✅")
    else:
        for d in disrs:
            sc2 = SEV_COLORS.get(d["severity"].upper(),"#718096")
            st.markdown(
                f'<div class="sr-disruption-card" style="border-left:3px solid {sc2};border-radius:0 14px 14px 0;">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                f'{_badge(d["severity"].upper(), sc2)}'
                f'<strong style="color:#F1F5F9;">{d["title"]}</strong>'
                f'<span style="color:#475569;font-size:.8rem;margin-left:4px;">'
                f'{d["type"]} · +{d["estimated_delay_days"]}d · +${d["additional_cost_usd"]:,}</span>'
                f'</div>'
                f'<div style="color:#64748B;font-size:.86rem;line-height:1.55;">{d["description"]}</div>'
                f'<div style="color:#475569;font-size:.78rem;margin-top:6px;">'
                f'<em>Match reason: {d.get("match_reason","—")}</em></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── 4. RECOMMENDED ACTION + ESCALATION ──────────────────────────────────
    _section("Recommended Action")
    rec_action   = analysis.get("recommended_action", "Continue Monitoring")
    action_pri   = analysis.get("action_priority", "MEDIUM")
    action_reason = analysis.get("action_reason", "")
    esc_required = analysis.get("escalation_required", False)
    esc_reasons  = analysis.get("escalation_reasons", [])
    supp_factors = analysis.get("supporting_factors", [])

    # Priority color
    _PRI_CLR = {"IMMEDIATE":"#F87171","HIGH":"#FB923C","MEDIUM":"#FBBF24","LOW":"#34D399"}
    pri_clr  = _PRI_CLR.get(action_pri, "#38BDF8")

    # Escalation banner (shown first when required)
    if esc_required:
        reasons_html = "<br>".join(f"⚠ {r}" for r in esc_reasons) if esc_reasons else ""
        st.markdown(
            f'<div class="sr-escalation-banner">'
            f'<span class="sr-escalation-icon">🚨</span>'
            f'<div>'
            f'<div class="sr-escalation-title">Escalation Required — Immediate Attention</div>'
            f'<div class="sr-escalation-reasons">{reasons_html}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    factors_chips = "".join(
        f'<span class="sr-chip">{f}</span>' for f in supp_factors
    )
    st.markdown(
        f'<div class="sr-action-card">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        f'<div class="sr-action-title">🎯 {rec_action}</div>'
        f'<span style="background:{pri_clr};color:#070B14;font-size:.72rem;font-weight:700;'
        f'padding:3px 10px;border-radius:6px;text-transform:uppercase;letter-spacing:.04em;">'
        f'{action_pri}</span>'
        f'</div>'
        f'<div class="sr-action-reason">{action_reason}</div>'
        f'<div class="sr-action-factors">{factors_chips}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── 5. ROUTE ALTERNATIVES ────────────────────────────────────────────────
    _section("Route Alternatives")
    routes = detail["routes"]
    alts   = routes.get("alternatives",[])
    if not alts:
        if routes.get("action_required"):
            _empty("No pre-defined alternatives for this route — contact carrier directly.", "📞")
        else:
            _empty("No rerouting required — shipment is on schedule.", "✅")
    else:
        # Show current route header
        current_route = f"{orig.get('city','?')} → {dest.get('city','?')} via {carrier}"
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);'
            f'border-radius:10px;padding:12px 16px;margin-bottom:12px;">'
            f'<div style="font-size:.68rem;font-weight:700;color:#475569;text-transform:uppercase;'
            f'letter-spacing:.09em;margin-bottom:4px;">CURRENT ROUTE</div>'
            f'<div style="color:#94A3B8;font-size:.9rem;font-weight:500;">{current_route}</div>'
            f'<div style="color:#F87171;font-size:.78rem;margin-top:3px;">'
            f'⚠ {len(disrs)} active disruption(s) on this route</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for i, alt in enumerate(alts, 1):
            ed    = alt["extra_delay_days"]
            d_str = f"+{ed} day(s)" if ed >= 0 else f"{abs(ed)} day(s) faster"
            d_clr = RISK_COLORS["HIGH"] if ed > 0 else RISK_COLORS["LOW"]
            cost_str = "+${:,}".format(alt["extra_cost_usd"])
            avoids = ", ".join(alt.get("avoids_disruptions",[]))
            with st.expander(
                f"Alternative {i}: {alt['description']}  ·  {d_str}  ·  {cost_str}",
                expanded=(i == 1)
            ):
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown(
                        _row("Delay Impact:",   f'<span style="color:{d_clr};font-weight:700;">{d_str}</span>') +
                        _row("Cost Impact:",     f'<span style="color:#FBBF24;font-weight:700;">{cost_str}</span>') +
                        _row("Avoids:",          avoids or "—") +
                        _row("Via Port/Hub:",    alt.get("via","—")),
                        unsafe_allow_html=True,
                    )
                with c_b:
                    veh_list = alt.get("available_vehicles",[])
                    if veh_list:
                        v_html = " ".join(f'<span class="sr-chip">🚢 {v["name"]}</span>' for v in veh_list)
                        st.markdown(f'<div style="margin-bottom:6px;"><span style="color:#475569;font-size:.78rem;">Available vessels:</span><br>{v_html}</div>', unsafe_allow_html=True)
                    else:
                        carriers = _chips(alt.get("suggested_carriers",[]))
                        st.markdown(f'<div style="margin-bottom:6px;"><span style="color:#475569;font-size:.78rem;">Suggested carriers:</span><br>{carriers}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.02);border-radius:8px;padding:10px 12px;'
                    f'color:#64748B;font-size:.85rem;line-height:1.6;margin-top:6px;">'
                    f'<strong style="color:#94A3B8;">Rationale:</strong> {alt["reason"]}</div>',
                    unsafe_allow_html=True,
                )

    # ── 6. VEHICLE RECOMMENDATION ────────────────────────────────────────────
    _section("Vehicle Recommendation")
    vr   = detail["vehicle"]
    best = vr.get("recommended_vehicle")
    if best:
        needs_reefer = bool((raw or {}).get("requires_cold_chain",False))
        reefer_ok    = (best.get("available_reefer_slots",0) > 0) if needs_reefer else None
        reefer_txt   = ""
        if needs_reefer:
            reefer_txt = (
                '<div style="display:flex;align-items:center;gap:8px;margin-top:10px;">'
                + ('<span style="color:#34D399;font-weight:700;">❄️ Reefer: Required ✓ Available</span>'
                   if reefer_ok else
                   '<span style="color:#F87171;font-weight:700;">❄️ Reefer: Required — check availability</span>')
                + '</div>'
            )
        attrs = (
            f'<div class="sr-vehicle-attr">'
            f'<div class="sr-vehicle-attr-item"><div class="sr-vehicle-attr-label">Vehicle</div>'
            f'<div class="sr-vehicle-attr-val">{best.get("name","—")}</div></div>'
            f'<div class="sr-vehicle-attr-item"><div class="sr-vehicle-attr-label">Carrier</div>'
            f'<div class="sr-vehicle-attr-val">{best.get("carrier","—")}</div></div>'
            f'<div class="sr-vehicle-attr-item"><div class="sr-vehicle-attr-label">Available TEU</div>'
            f'<div class="sr-vehicle-attr-val">{best.get("available_teu","—")}</div></div>'
            f'<div class="sr-vehicle-attr-item"><div class="sr-vehicle-attr-label">Reefer Slots</div>'
            f'<div class="sr-vehicle-attr-val">{best.get("available_reefer_slots",0)}</div></div>'
            f'<div class="sr-vehicle-attr-item"><div class="sr-vehicle-attr-label">Location</div>'
            f'<div class="sr-vehicle-attr-val">{best.get("current_location","—")}</div></div>'
            f'<div class="sr-vehicle-attr-item"><div class="sr-vehicle-attr-label">Next Departure</div>'
            f'<div class="sr-vehicle-attr-val">{best.get("next_departure","TBD")}</div></div>'
            f'</div>'
        )
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
            f'<div style="color:#38BDF8;font-size:.7rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.08em;margin-bottom:8px;">✔ Recommended Vehicle</div>'
            f'{attrs}{reefer_txt}'
            f'<div style="color:#94A3B8;font-size:.82rem;margin-top:10px;line-height:1.6;">'
            f'{vr.get("reason","")}'
            f'</div>'
            f'{alt_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        _empty(vr.get("reason","No suitable vehicle found for this shipment."), "🔍")

    # ── 7. COLD-CHAIN STATUS ─────────────────────────────────────────────────
    cold = detail["cold"]
    if cold:
        _section("Cold-Chain Status")
        sc3     = SEV_COLORS.get(cold["excursion_severity"],"#718096")
        t_min   = cold.get("required_temp_min_c","?")
        t_max   = cold.get("required_temp_max_c","?")
        latest  = cold.get("latest_temp_c","?")
        exc_cnt = cold.get("excursion_count",0)
        exc_sev = cold.get("excursion_severity","NORMAL")
        max_dev = cold.get("max_deviation_c", None)  # may not always exist
        cc_risk = cold.get("cold_chain_risk_score",0)
        cc_detail = "".join([
            _row("Safe Range:",     f'{t_min} °C – {t_max} °C'),
            _row("Latest Reading:", f'{latest} °C'),
            _row("Min Observed:",   f'{cold.get("min_observed_c","?")!s} °C'),
            _row("Max Observed:",   f'{cold.get("max_observed_c","?")!s} °C'),
            _row("Readings:",       str(cold.get("reading_count",0))),
            _row("Excursions:",     str(exc_cnt)),
            _row("Severity:",       f'<span style="color:{sc3};font-weight:700;">{exc_sev}</span>'),
            _row("Cold-Chain Risk:",f'<span style="color:#38BDF8;font-weight:700;">{cc_risk}/100</span>'),
        ])
        st.markdown(
            f'<div class="sr-card" style="border-left:3px solid {sc3};border-radius:0 14px 14px 0;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
            f'{_badge(exc_sev, sc3)}'
            f'<span style="color:#94A3B8;font-size:.82rem;">Cold-Chain Monitor — DEMO DATA</span>'
            f'</div>'
            f'{cc_detail}'
            f'<div style="margin-top:12px;background:rgba(255,255,255,0.02);border-radius:8px;'
            f'padding:10px 14px;color:#64748B;font-size:.83rem;line-height:1.6;">'
            f'<strong style="color:#94A3B8;">Why does this matter?</strong><br>'
            + (
                f'Temperature excursions (readings outside {t_min}–{t_max} °C) indicate '
                f'that cargo integrity may be compromised. '
                f'{exc_cnt} excursion(s) detected. '
                + ("Severity is CRITICAL — immediate corrective action required to prevent spoilage or regulatory non-compliance."
                   if exc_sev == "CRITICAL" else
                   "Severity is WARNING — close monitoring required to prevent escalation."
                   if exc_sev == "WARNING" else
                   "All readings are within the safe range.")
            ) +
            f'</div></div>',
            unsafe_allow_html=True,
        )

    # ── 8. AI EXPLANATION ────────────────────────────────────────────────────
    st.divider()
    ai_configured = is_watsonx_configured()
    pill = (
        '<span class="sr-pill-wx">● watsonx.ai Live</span>'
        if ai_configured else
        '<span class="sr-pill-demo">○ Demo Mode — Mock AI</span>'
    )
    st.markdown(
        f'<div class="sr-ai-section">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<span style="font-weight:700;color:#F1F5F9;font-size:.98rem;font-family:Space Grotesk,sans-serif;">'
        f'🤖 AI Risk Explanation — IBM watsonx.ai</span>'
        f'{pill}</div>'
        f'<div style="color:#475569;font-size:.8rem;margin-bottom:8px;">'
        f'The deterministic SmartRoute engine has already calculated the risk, action, and route options. '
        f'IBM watsonx.ai (Granite LLM) explains the result in plain English.</div>',
        unsafe_allow_html=True,
    )
    ai_label = "watsonx.ai (Granite LLM)" if ai_configured else "Demo AI (Mock)"
    if st.button(f"Generate Explanation via {ai_label}", key=f"ai_{selected_id}"):
        prompt = build_ai_prompt(selected_id, risk, disrs, analysis)
        with st.spinner("Generating AI explanation…"):
            result = generate_ai_explanation(prompt)
        src_pill = (
            '<span class="sr-pill-wx">● watsonx.ai</span>'
            if result["source"] == "watsonx" else
            '<span class="sr-pill-demo">○ Demo Mode — Mock AI</span>'
        )
        st.markdown(
            f'<div class="sr-ai-response">'
            f'<div style="margin-bottom:10px;">{src_pill}'
            + (f'<span style="color:#475569;font-size:.75rem;margin-left:8px;">Model: {result.get("model_id","mock")}</span>' if result.get("model_id") else '') +
            f'</div>'
            f'<div class="sr-ai-response-text">{result["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if result.get("error"):
            st.caption(f"Note: {result['error']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Executive Report Exporter ───────────────────────────────────────────
    _section("Executive Incident Command Report")
    st.markdown(
        f'<div class="sr-card">'
        f'<div style="color:#94A3B8;font-size:0.86rem;margin-bottom:12px;line-height:1.5;">'
        f'Generate an official <strong>Executive Incident Briefing & Mitigation Plan</strong> for logistics leadership, '
        f'clients, or compliance auditors. Includes risk factors, recommended actions, route options, and IBM watsonx.ai narrative.'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            "📥 Download Executive Briefing (HTML)",
            data=generate_executive_report_html(selected_id),
            file_name=f"Executive_Incident_Briefing_{selected_id}.html",
            mime="text/html",
            key=f"dl_html_{selected_id}",
            use_container_width=True,
        )
    with col_exp2:
        st.download_button(
            "📄 Download Briefing (Markdown)",
            data=generate_executive_report_markdown(selected_id),
            file_name=f"Executive_Incident_Briefing_{selected_id}.md",
            mime="text/markdown",
            key=f"dl_md_{selected_id}",
            use_container_width=True,
        )

    # ── 9. TECHNICAL DETAILS + MCP TOOLS ─────────────────────────────────────
    st.divider()
    with st.expander("🔧 Technical Details & MCP Tool Integration"):
        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            _section("Factor Breakdown")
            fb = risk.get("factor_breakdown",{})
            st.markdown(
                f'<div class="sr-card">'
                + _row("Disruption Severity:", f'{fb.get("disruption_severity",0)}/35') +
                _row("Delay Impact:",           f'{fb.get("delay",0)}/25') +
                _row("Deadline Pressure:",      f'{fb.get("deadline_pressure",0)}/20') +
                _row("Priority:",               f'{fb.get("priority",0)}/15') +
                _row("Cold-Chain:",             f'{fb.get("cold_chain",0)}/5') +
                _row("Total Score:",            f'<strong style="color:{RISK_COLORS.get(cls,"#718096")};">{sc}/100 ({cls})</strong>') +
                f'</div>',
                unsafe_allow_html=True,
            )
            _section("Data Sources")
            ds = analysis.get("data_sources", {})
            ds_html = "".join([
                _row("Shipment Data:",    "✓ Loaded" if ds.get("shipment_data") == "loaded" else "Not found"),
                _row("Disruption Data:", "✓ Loaded" if ds.get("disruption_data") == "loaded" else "Unavailable"),
                _row("Route Data:",      "✓ Loaded" if ds.get("route_data") == "loaded" else "Unavailable"),
                _row("Vehicle Data:",    "✓ Loaded" if ds.get("vehicle_data") == "loaded" else "Unavailable"),
                _row("Temperature:",     "✓ Loaded" if ds.get("temperature_data") == "loaded" else ("N/A" if ds.get("temperature_data") == "not_applicable" else "Not found")),
                _row("Environment:",     f'<span class="sr-data-status">{ds.get("source","DEMO")}</span>'),
            ])
            st.markdown(f'<div class="sr-card">{ds_html}</div>', unsafe_allow_html=True)

        with c_right:
            _section("MCP Tool Integration")
            _MCP_TOOLS = [
                ("get_shipment_risk",        "Returns risk score, classification, and factor breakdown for a shipment."),
                ("get_shipment_disruptions", "Returns all active disruptions affecting a shipment."),
                ("recommend_route",          "Recommends alternative routes for a disrupted shipment."),
                ("recommend_vehicle",        "Recommends the best available vehicle for a shipment."),
                ("get_fleet_status",         "Returns fleet utilisation summary across all vessels."),
                ("get_temperature_alerts",   "Returns cold-chain temperature excursion alerts."),
                ("explain_shipment",         "Generates an AI explanation via IBM watsonx.ai."),
            ]
            tools_html = ""
            for tname, tdesc in _MCP_TOOLS:
                tools_html += (
                    f'<div class="sr-mcp-tool">'
                    f'<span class="sr-mcp-check">✓</span>'
                    f'<div>'
                    f'<div class="sr-mcp-name">{tname}</div>'
                    f'<div class="sr-mcp-desc">{tdesc}</div>'
                    f'</div></div>'
                )
            st.markdown(
                f'<div class="sr-card" style="padding:14px 16px;">'
                f'<div style="font-size:.68rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;'
                f'font-weight:700;margin-bottom:8px;">IBM BOB MCP SERVER — 7 TOOLS</div>'
                f'{tools_html}</div>',
                unsafe_allow_html=True,
            )


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
    if "sel_disruption" in st.session_state and st.session_state["sel_disruption"] not in disr_ids:
        del st.session_state["sel_disruption"]
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
    if "fleet_shp" in st.session_state and st.session_state["fleet_shp"] not in shp_ids:
        del st.session_state["fleet_shp"]
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

    if "sel_cold" in st.session_state and st.session_state["sel_cold"] not in cold_shp_ids:
        del st.session_state["sel_cold"]
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
# Top Navigation Bar
# ════════════════════════════════════════════════════════════════════════════
NAV_TABS = [
    ("Dashboard",   "🏠"),
    ("Shipments",   "📦"),
    ("Disruptions", "⚠️"),
    ("Fleet",       "🚢"),
    ("Cold Chain",  "🌡️"),
]

# Robust CSS injected once to style the nav buttons specifically
_TOPNAV_BTN_CSS = """
<style>
/* ── Top-nav Streamlit button overrides ── */
button[key^="topnav_btn_"],
div[data-testid="stColumn"] button[aria-label*="Dashboard"],
div[data-testid="stColumn"] button[aria-label*="Shipments"],
div[data-testid="stColumn"] button[aria-label*="Disruptions"],
div[data-testid="stColumn"] button[aria-label*="Fleet"],
div[data-testid="stColumn"] button[aria-label*="Cold Chain"] {
  background: transparent !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 9px !important;
  color: #94A3B8 !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  padding: 6px 10px !important;
  box-shadow: none !important;
  transition: all 0.18s ease !important;
  letter-spacing: 0 !important;
  width: 100% !important;
  white-space: nowrap !important;
}

/* Inactive nav button hover */
div[data-testid="stBaseButton-secondary"] button[aria-label*="Dashboard"]:hover,
div[data-testid="stBaseButton-secondary"] button[aria-label*="Shipments"]:hover,
div[data-testid="stBaseButton-secondary"] button[aria-label*="Disruptions"]:hover,
div[data-testid="stBaseButton-secondary"] button[aria-label*="Fleet"]:hover,
div[data-testid="stBaseButton-secondary"] button[aria-label*="Cold Chain"]:hover {
  background: rgba(255,255,255,0.08) !important;
  color: #F1F5F9 !important;
  border-color: rgba(255,255,255,0.18) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Active tab button styling (Primary button) */
div[data-testid="stBaseButton-primary"] button[aria-label*="Dashboard"],
div[data-testid="stBaseButton-primary"] button[aria-label*="Shipments"],
div[data-testid="stBaseButton-primary"] button[aria-label*="Disruptions"],
div[data-testid="stBaseButton-primary"] button[aria-label*="Fleet"],
div[data-testid="stBaseButton-primary"] button[aria-label*="Cold Chain"] {
  color: #38BDF8 !important;
  background: rgba(56,189,248,0.14) !important;
  border: 1px solid rgba(56,189,248,0.4) !important;
  font-weight: 700 !important;
  box-shadow: 0 0 12px rgba(56,189,248,0.2) !important;
}

div[data-testid="stBaseButton-primary"] button[aria-label*="Dashboard"]:hover,
div[data-testid="stBaseButton-primary"] button[aria-label*="Shipments"]:hover,
div[data-testid="stBaseButton-primary"] button[aria-label*="Disruptions"]:hover,
div[data-testid="stBaseButton-primary"] button[aria-label*="Fleet"]:hover,
div[data-testid="stBaseButton-primary"] button[aria-label*="Cold Chain"]:hover {
  background: rgba(56,189,248,0.22) !important;
  border-color: rgba(56,189,248,0.5) !important;
  transform: none !important;
}
</style>
"""


def _render_topnav(ai_on: bool, current_page: str) -> str | None:
    """Render the glassmorphic top nav bar. Returns new page if user clicked a tab."""

    demo_pill = (
        '<span class="sr-demo-pill">'
        '<span class="sr-demo-pill-dot"></span>● Demo Mode</span>'
        if not ai_on else
        '<span class="sr-demo-pill" style="background:rgba(52,211,153,0.12);'
        'border-color:rgba(52,211,153,0.3);color:#34D399;">'
        '<span class="sr-demo-pill-dot" style="background:#34D399;box-shadow:0 0 6px #34D399;"></span>'
        '● watsonx.ai Live</span>'
    )

    st.markdown(f"""
<div class="sr-topnav">
  <div class="sr-topnav-brand">
    <div class="sr-topnav-logo">⚓</div>
    <div class="sr-topnav-name">
      <span class="sr-topnav-title">SmartRoute AI</span>
      <span class="sr-topnav-sub">Supply Chain Control Tower</span>
    </div>
  </div>
  <div class="sr-topnav-right" style="margin-left:auto;">
    {demo_pill}
    <span class="sr-team-badge">Team PI-NANT</span>
  </div>
</div>
{_TOPNAV_BTN_CSS}
""", unsafe_allow_html=True)

    # ── Navigation buttons (real Streamlit widgets) ─────────────────────────
    clicked_page = None
    btn_cols = st.columns(len(NAV_TABS))
    for col, (name, icon) in zip(btn_cols, NAV_TABS):
        is_active = (name == current_page)
        btn_type = "primary" if is_active else "secondary"
        with col:
            if st.button(
                f"{icon}  {name}",
                key=f"topnav_btn_{name}",
                use_container_width=True,
                type=btn_type,
            ):
                clicked_page = name

    # Draw bottom border under nav buttons
    st.markdown(
        '<div style="border-bottom:1px solid rgba(255,255,255,0.07);'
        'margin: -6px -2.2rem 16px -2.2rem;"></div>',
        unsafe_allow_html=True,
    )
    return clicked_page


# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="SmartRoute AI",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    pages = {
        "Dashboard":   page_dashboard,
        "Shipments":   page_shipments,
        "Disruptions": page_disruptions,
        "Fleet":       page_fleet,
        "Cold Chain":  page_cold_chain,
    }

    # Initialise navigation state
    if "nav" not in st.session_state:
        st.session_state["nav"] = "Dashboard"

    # Render top nav — if any tab button was clicked, update state and rerun
    ai_on = is_watsonx_configured()
    clicked = _render_topnav(ai_on, st.session_state["nav"])
    if clicked:
        st.session_state["nav"] = clicked
        st.rerun()

    # Render active page safely
    active_page = st.session_state.get("nav", "Dashboard")
    if active_page in pages:
        pages[active_page]()
    else:
        st.session_state["nav"] = "Dashboard"
        pages["Dashboard"]()


main()

