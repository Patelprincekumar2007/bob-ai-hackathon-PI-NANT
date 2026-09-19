"""
report_exporter.py — SmartRoute AI  ·  Executive Report Generator
===================================================================
Generates polished Executive Incident Briefings in HTML and Markdown
formats for logistics managers, executive leadership, and auditors.
"""

from datetime import datetime
from core.decision_engine import analyse_shipment, build_watsonx_prompt
from core.watsonx_client import generate_ai_explanation


def generate_executive_report_markdown(shipment_id: str) -> str:
    """Generate a clean Markdown Executive Briefing for a shipment."""
    analysis = analyse_shipment(shipment_id)
    if analysis.get("error"):
        return f"# Executive Incident Briefing — {shipment_id}\n\n**Error:** {analysis['error']}\n"

    shp   = analysis.get("shipment", {}) or {}
    disr  = analysis.get("disruptions", []) or []
    rres  = analysis.get("route_result", {}) or {}
    alts  = rres.get("alternatives", []) or []
    vres  = analysis.get("vehicle_result", {}) or {}
    veh   = vres.get("recommended_vehicle") or {}
    cold  = analysis.get("cold_chain")
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    risk_score = analysis.get("risk_score", 0)
    risk_level = analysis.get("risk_level", "LOW")
    risk_factors = analysis.get("risk_factors", {})

    # Generate or fetch AI explanation summary
    ai_prompt = build_watsonx_prompt(analysis)
    ai_res = generate_ai_explanation(ai_prompt)
    ai_text = ai_res.get("text", "No AI explanation generated.")

    lines = [
        f"# ⚓ SmartRoute AI — Executive Incident Briefing",
        f"**Shipment ID:** `{shipment_id}` | **Generated:** `{gen_time}` | **System Status:** `Active Control Tower`",
        f"---",
        f"",
        f"## 1. Executive Summary & Cargo Overview",
        f"- **Description:** {shp.get('description', 'N/A')}",
        f"- **Route:** {shp.get('origin', {}).get('city', 'N/A')} ({shp.get('origin', {}).get('country', '')}) → {shp.get('destination', {}).get('city', 'N/A')} ({shp.get('destination', {}).get('country', '')})",
        f"- **Carrier:** {shp.get('carrier', 'N/A')}",
        f"- **Priority:** {str(shp.get('priority', 'N/A')).upper()}",
        f"- **Status:** {str(shp.get('status', 'N/A')).title()}",
        f"- **Cold-Chain Required:** {'Yes (❄️)' if shp.get('requires_cold_chain') else 'No'}",
        f"",
        f"## 2. Risk & Impact Assessment",
        f"- **Risk Score:** `{risk_score} / 100` ({risk_level})",
        f"- **Estimated Delay:** {shp.get('delay_days', 0)} day(s)",
        f"- **Active Disruptions Count:** {len(disr)}",
        f"",
        f"### Contributing Risk Factors",
        f"- Disruption Severity: {risk_factors.get('disruption_severity', 0)} / 35",
        f"- Delay Impact: {risk_factors.get('delay', 0)} / 25",
        f"- Deadline Pressure: {risk_factors.get('deadline_pressure', 0)} / 20",
        f"- Cargo Priority: {risk_factors.get('priority', 0)} / 15",
        f"- Cold Chain Factor: {risk_factors.get('cold_chain', 0)} / 5",
        f"",
        f"## 3. Recommended Operational Action",
        f"🎯 **Primary Action:** {analysis.get('recommended_action', 'Continue Monitoring')}",
        f"- **Priority Level:** `{analysis.get('action_priority', 'MEDIUM')}`",
        f"- **Action Rationale:** {analysis.get('action_reason', 'N/A')}",
        f"- **Escalation Required:** {'🚨 YES — Immediate Leadership Review Required' if analysis.get('escalation_required') else 'NO'}",
    ]

    if analysis.get('escalation_reasons'):
        lines.append("### Escalation Drivers:")
        for r in analysis['escalation_reasons']:
            lines.append(f"- ⚠️ {r}")

    lines.extend([
        f"",
        f"## 4. Reroute & Fleet Contingency Options",
    ])

    if alts:
        for i, alt in enumerate(alts, 1):
            ed = alt.get("extra_delay_days", 0)
            delay_str = f"+{ed} day(s)" if ed >= 0 else f"{abs(ed)} day(s) faster"
            lines.append(f"### Option {i}: {alt.get('description')}")
            lines.append(f"- **Impact:** Delay {delay_str} | Additional Cost: +${alt.get('extra_cost_usd', 0):,}")
            lines.append(f"- **Avoided Disruptions:** {', '.join(alt.get('avoids_disruptions', [])) or 'None'}")
            lines.append(f"- **Rationale:** {alt.get('reason', 'N/A')}")
    else:
        lines.append("_No pre-defined alternative routes required or available._")

    if veh and veh.get("name"):
        lines.extend([
            f"",
            f"### Recommended Vehicle Allocation",
            f"- **Vessel/Vehicle:** {veh.get('name')} ({veh.get('carrier', 'N/A')})",
            f"- **Available Capacity:** {veh.get('available_teu', 0)} TEU | Reefer Slots: {veh.get('available_reefer_slots', 0)}",
            f"- **Location / Next Departure:** {veh.get('current_location', 'N/A')} (Departs: {veh.get('next_departure', 'TBD')})",
        ])

    if cold:
        lines.extend([
            f"",
            f"## 5. Cold-Chain Sensor & Cargo Integrity Status",
            f"- **Safe Temp Range:** {cold.get('required_temp_min_c')} °C to {cold.get('required_temp_max_c')} °C",
            f"- **Latest Reading:** {cold.get('latest_temp_c')} °C",
            f"- **Excursion Severity:** `{cold.get('excursion_severity', 'NORMAL')}` ({cold.get('excursion_count', 0)} excursions detected)",
            f"- **Cold Chain Risk Score:** {cold.get('cold_chain_risk_score', 0)} / 100",
        ])

    lines.extend([
        f"",
        f"## 6. AI Strategic Briefing — IBM watsonx.ai",
        f"> {ai_text.replace(chr(10), chr(10) + '> ')}",
        f"",
        f"---",
        f"*Report generated automatically by SmartRoute AI Control Tower. Internal Use Only.*",
    ])

    return "\n".join(lines)


def generate_executive_report_html(shipment_id: str) -> str:
    """Generate a print-ready, beautifully styled HTML Executive Briefing."""
    analysis = analyse_shipment(shipment_id)
    if analysis.get("error"):
        return f"<html><body><h1>Error</h1><p>{analysis['error']}</p></body></html>"

    shp   = analysis.get("shipment", {}) or {}
    disr  = analysis.get("disruptions", []) or []
    rres  = analysis.get("route_result", {}) or {}
    alts  = rres.get("alternatives", []) or []
    vres  = analysis.get("vehicle_result", {}) or {}
    veh   = vres.get("recommended_vehicle") or {}
    cold  = analysis.get("cold_chain")
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    risk_score = analysis.get("risk_score", 0)
    risk_level = analysis.get("risk_level", "LOW")

    ai_prompt = build_watsonx_prompt(analysis)
    ai_res = generate_ai_explanation(ai_prompt)
    ai_text = ai_res.get("text", "No AI explanation generated.")

    cls = risk_level
    risk_colors = {"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MEDIUM": "#D97706", "LOW": "#059669"}
    cls_color = risk_colors.get(cls, "#059669")

    disr_rows = ""
    for d in disr:
        disr_rows += f"""
        <tr>
            <td><strong>{d.get('id')}</strong></td>
            <td>{d.get('title')}</td>
            <td><span class="badge" style="background:#FEE2E2;color:#991B1B;">{d.get('severity','').upper()}</span></td>
            <td>+{d.get('estimated_delay_days',0)} days</td>
            <td>+${d.get('additional_cost_usd',0):,}</td>
        </tr>
        """
    if not disr_rows:
        disr_rows = "<tr><td colspan='5' style='text-align:center;color:#6B7280;'>No active disruptions affecting this shipment.</td></tr>"

    alt_rows = ""
    for i, a in enumerate(alts, 1):
        ed = a.get('extra_delay_days', 0)
        d_str = f"+{ed}d" if ed >= 0 else f"{abs(ed)}d faster"
        alt_rows += f"""
        <tr>
            <td><strong>Alt {i}</strong></td>
            <td>{a.get('description')}</td>
            <td>{d_str}</td>
            <td>+${a.get('extra_cost_usd',0):,}</td>
            <td>{a.get('reason')}</td>
        </tr>
        """
    if not alt_rows:
        alt_rows = "<tr><td colspan='5' style='text-align:center;color:#6B7280;'>No rerouting required — shipment on schedule.</td></tr>"

    ai_html = ai_text.replace('\n', '<br>')
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Executive Incident Briefing — {shipment_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0F172A;
            color: #F8FAFC;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #1E293B;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid #334155;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #334155;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .title {{ font-size: 24px; font-weight: 800; color: #38BDF8; margin: 0; }}
        .subtitle {{ font-size: 13px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; }}
        .meta-bar {{ font-size: 13px; color: #CBD5E1; margin-bottom: 20px; }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #F1F5F9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-left: 4px solid #38BDF8;
            padding-left: 10px;
            margin-top: 28px;
            margin-bottom: 14px;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px; }}
        .card {{
            background: #0F172A;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px;
        }}
        .score-box {{
            text-align: center;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid {cls_color};
            border-radius: 10px;
            padding: 20px;
        }}
        .score-num {{ font-size: 42px; font-weight: 900; color: {cls_color}; line-height: 1; }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-risk {{ background: {cls_color}; color: #FFFFFF; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 14px;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        th {{ background: #0F172A; color: #94A3B8; font-size: 12px; text-transform: uppercase; }}
        .ai-box {{
            background: linear-gradient(135deg, rgba(56,189,248,0.1), rgba(129,140,248,0.1));
            border: 1px solid rgba(56,189,248,0.3);
            border-radius: 8px;
            padding: 18px;
            margin-top: 14px;
            color: #E2E8F0;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #64748B;
            border-top: 1px solid #334155;
            padding-top: 16px;
        }}
        @media print {{
            body {{ background: #FFFFFF; color: #000000; padding: 0; }}
            .container {{ background: #FFFFFF; border: none; box-shadow: none; color: #000000; }}
            .card, .score-box {{ background: #F8FAFC; border-color: #CBD5E1; color: #000000; }}
            .ai-box {{ background: #F1F5F9; border-color: #CBD5E1; color: #000000; }}
            th {{ background: #E2E8F0; color: #1E293B; }}
            td {{ border-bottom-color: #E2E8F0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">SmartRoute AI</h1>
                <div class="subtitle">Executive Incident Briefing & Mitigation Plan</div>
            </div>
            <div>
                <span class="badge badge-risk">{cls} RISK</span>
            </div>
        </div>

        <div class="meta-bar">
            <strong>Shipment ID:</strong> {shipment_id} &nbsp;|&nbsp; 
            <strong>Generated:</strong> {gen_time} &nbsp;|&nbsp; 
            <strong>Priority:</strong> {str(shp.get('priority','N/A')).upper()}
        </div>

        <div class="grid">
            <div class="score-box">
                <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase;">Overall Risk Score</div>
                <div class="score-num">{risk_score}</div>
                <div style="font-size: 13px; color: {cls_color}; font-weight: 700;">{cls} SEVERITY</div>
            </div>
            <div class="card">
                <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; margin-bottom: 6px;">Overview</div>
                <div><strong>Description:</strong> {shp.get('description', 'N/A')}</div>
                <div><strong>Route:</strong> {shp.get('origin', {}).get('city', '')} → {shp.get('destination', {}).get('city', '')}</div>
                <div><strong>Carrier:</strong> {shp.get('carrier', 'N/A')}</div>
                <div><strong>Cold-Chain:</strong> {'Required ❄️' if shp.get('requires_cold_chain') else 'Not Required'}</div>
            </div>
        </div>

        <div class="section-title">Recommended Operational Action</div>
        <div class="card" style="border-left: 4px solid #38BDF8;">
            <div style="font-size: 18px; font-weight: 700; color: #38BDF8;">🎯 {analysis.get('recommended_action', 'Continue Monitoring')}</div>
            <div style="margin-top: 6px; color: #CBD5E1;">{analysis.get('action_reason', 'N/A')}</div>
            <div style="margin-top: 10px; font-size: 13px; color: #94A3B8;">
                <strong>Action Priority:</strong> {analysis.get('action_priority', 'MEDIUM')} &nbsp;|&nbsp; 
                <strong>Escalation Required:</strong> {'🚨 YES' if analysis.get('escalation_required') else 'NO'}
            </div>
        </div>

        <div class="section-title">Active Disruptions</div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Severity</th>
                    <th>Delay</th>
                    <th>Add. Cost</th>
                </tr>
            </thead>
            <tbody>
                {disr_rows}
            </tbody>
        </table>

        <div class="section-title">Route Alternatives</div>
        <table>
            <thead>
                <tr>
                    <th>Option</th>
                    <th>Description</th>
                    <th>Delay Delta</th>
                    <th>Cost Delta</th>
                    <th>Rationale</th>
                </tr>
            </thead>
            <tbody>
                {alt_rows}
            </tbody>
        </table>

        {"<div class='section-title'>Cold-Chain Status</div><div class='card'>Safe Range: " + str(cold.get('required_temp_min_c','?')) + " °C – " + str(cold.get('required_temp_max_c','?')) + " °C | Latest: " + str(cold.get('latest_temp_c','?')) + " °C | Excursion Severity: <strong>" + str(cold.get('excursion_severity','NORMAL')) + "</strong></div>" if cold else ""}

        <div class="section-title">IBM watsonx.ai Strategic Narrative</div>
        <div class="ai-box">
            {ai_html}
        </div>

        <div class="footer">
            SmartRoute AI Control Tower — Official Operational Decision Support Briefing
        </div>
    </div>
</body>
</html>
"""
    return html
