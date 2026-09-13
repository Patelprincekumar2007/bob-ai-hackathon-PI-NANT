"""
mcp_server.py
=============
IBM Bob MCP Server for SmartRoute AI.

Exposes SmartRoute AI capabilities as tools that IBM Bob can call via the
Model Context Protocol (MCP).  Each tool calls the real project functions —
no hardcoded or fake responses.

Tools exposed
-------------
  1. get_shipment_risk        (shipment_id)          -> risk score + explanation
  2. get_shipment_disruptions (shipment_id)          -> active disruptions
  3. recommend_route          (shipment_id)          -> alternative routes
  4. recommend_vehicle        (shipment_id)          -> best available vehicle
  5. get_fleet_status         ()                     -> fleet utilisation summary
  6. get_temperature_alerts   (shipment_id=optional) -> cold-chain alerts
  7. explain_shipment         (shipment_id)          -> AI explanation via watsonx

How to run
----------
    cd bob-ai-hackathon-PI-NANT/src
    pip install -r requirements.txt
    python mcp_server.py

IBM Bob connects to this server via stdio MCP transport.
See src/mcp/README.md for full setup instructions.

Environment variables (for tool 7 — watsonx AI explanations)
-------------------------------------------------------------
    WATSONX_API_KEY      IBM Cloud API key
    WATSONX_PROJECT_ID   watsonx.ai project ID
    WATSONX_URL          (optional) Inference endpoint
    WATSONX_MODEL_ID     (optional) Model ID
"""

import json
import logging
import sys
import os

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup — allow running as: python src/mcp_server.py
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# ---------------------------------------------------------------------------
# Import core project functions
# ---------------------------------------------------------------------------
from core.risk_engine import calculate_risk_by_id
from core.disruption_detector import get_shipment_disruptions as _get_disruptions
from core.route_advisor import recommend_alternative_routes
from core.fleet_optimizer import (
    recommend_vehicle_for_shipment,
    get_fleet_summary,
)
from core.cold_chain_monitor import get_temperature_alerts as _get_temp_alerts
from core.watsonx_client import generate_ai_explanation, is_watsonx_configured

# ---------------------------------------------------------------------------
# MCP SDK import with graceful fallback
# ---------------------------------------------------------------------------
try:
    from mcp.server import Server                          # type: ignore
    from mcp.server.stdio import stdio_server              # type: ignore
    from mcp import types as mcp_types                     # type: ignore
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    logger.warning(
        "mcp package not installed. Run: pip install mcp  "
        "The tool functions are still importable and testable without it."
    )


# ---------------------------------------------------------------------------
# Tool implementation functions
# All functions return plain Python dicts for easy testing and JSON serialisation.
# ---------------------------------------------------------------------------

def tool_get_shipment_risk(shipment_id: str) -> dict:
    """
    Return the risk score, classification, and explanation for a shipment.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict  { shipment_id, score, classification, explanation, factor_breakdown }
    """
    result = calculate_risk_by_id(shipment_id)
    if result is None:
        return {
            "shipment_id": shipment_id,
            "error": "Shipment '%s' not found." % shipment_id,
            "score": None,
            "classification": None,
            "explanation": None,
        }
    return {
        "shipment_id": result["shipment_id"],
        "score": result["score"],
        "classification": result["classification"],
        "explanation": result["explanation"],
        "factor_breakdown": result["factor_breakdown"],
    }


def tool_get_shipment_disruptions(shipment_id: str) -> dict:
    """
    Return all active disruptions affecting a shipment.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict  { shipment_id, disruption_count, disruptions: list }
    """
    disruptions = _get_disruptions(shipment_id)
    return {
        "shipment_id": shipment_id,
        "disruption_count": len(disruptions),
        "disruptions": disruptions,
    }


def tool_recommend_route(shipment_id: str) -> dict:
    """
    Recommend alternative routes and carriers for a disrupted shipment.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict  { shipment_id, action_required, recommendation, alternatives }
    """
    result = recommend_alternative_routes(shipment_id)
    return {
        "shipment_id": result["shipment_id"],
        "action_required": result["action_required"],
        "recommendation": result["recommendation"],
        "risk_score": result["risk_score"],
        "risk_classification": result["risk_classification"],
        "alternatives": result["alternatives"],
    }


def tool_recommend_vehicle(shipment_id: str) -> dict:
    """
    Recommend the best available vehicle for a shipment.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict  { shipment_id, recommended_vehicle, reason, alternatives }
    """
    return recommend_vehicle_for_shipment(shipment_id)


def tool_get_fleet_status() -> dict:
    """
    Return fleet utilisation summary (no input required).

    Returns
    -------
    dict  { total, available, unavailable, assigned, idle,
            utilisation_pct, reefer_capable_count,
            available_total_teu, available_total_weight_kg }
    """
    return get_fleet_summary()


def tool_get_temperature_alerts(shipment_id: str = None) -> dict:
    """
    Return cold-chain temperature alerts.

    Parameters
    ----------
    shipment_id : str | None
        If provided, return alerts for that shipment only.
        If None or empty, return alerts for all tracked shipments.

    Returns
    -------
    dict  { alert_count, alerts: list }
    """
    sid = shipment_id if shipment_id and shipment_id.strip() else None
    alerts = _get_temp_alerts(shipment_id=sid)
    return {
        "alert_count": len(alerts),
        "alerts": alerts,
    }


def tool_explain_shipment(shipment_id: str) -> dict:
    """
    Generate an AI-powered natural-language explanation for a shipment's situation.

    Uses IBM watsonx.ai if credentials are configured; returns a clearly-labelled
    mock response otherwise.

    Parameters
    ----------
    shipment_id : str   e.g. "SHP-001"

    Returns
    -------
    dict  { shipment_id, explanation, source, ai_powered }
    """
    # Build a rich prompt using real data
    risk = calculate_risk_by_id(shipment_id)
    if risk is None:
        prompt = "Shipment %s was not found in the system." % shipment_id
    else:
        disruptions = risk.get("disruptions", [])
        disr_summary = (
            ", ".join(d["title"] for d in disruptions) if disruptions else "none"
        )
        prompt = (
            "You are a supply chain risk advisor. "
            "Explain in plain English the current situation for shipment %s. "
            "Risk score: %d/100 (%s). "
            "Active disruptions: %s. "
            "Risk explanation: %s "
            "Provide a brief (3-4 sentence) advisory for the logistics coordinator."
            % (
                shipment_id,
                risk["score"],
                risk["classification"],
                disr_summary,
                risk["explanation"],
            )
        )

    ai_result = generate_ai_explanation(prompt)
    return {
        "shipment_id": shipment_id,
        "explanation": ai_result["text"],
        "source": ai_result["source"],
        "ai_powered": ai_result["source"] == "watsonx",
        "model_id": ai_result["model_id"],
    }


# ---------------------------------------------------------------------------
# MCP tool registry — used both by the MCP server and by tests
# ---------------------------------------------------------------------------

TOOLS = {
    "get_shipment_risk": {
        "fn": tool_get_shipment_risk,
        "description": "Get risk score, classification, and explanation for a shipment.",
        "required_params": ["shipment_id"],
    },
    "get_shipment_disruptions": {
        "fn": tool_get_shipment_disruptions,
        "description": "Get all active disruptions affecting a specific shipment.",
        "required_params": ["shipment_id"],
    },
    "recommend_route": {
        "fn": tool_recommend_route,
        "description": "Recommend alternative routes and carriers for a disrupted shipment.",
        "required_params": ["shipment_id"],
    },
    "recommend_vehicle": {
        "fn": tool_recommend_vehicle,
        "description": "Recommend the best available vehicle for a shipment.",
        "required_params": ["shipment_id"],
    },
    "get_fleet_status": {
        "fn": tool_get_fleet_status,
        "description": "Get fleet utilisation summary including idle and assigned vehicles.",
        "required_params": [],
    },
    "get_temperature_alerts": {
        "fn": tool_get_temperature_alerts,
        "description": "Get cold-chain temperature excursion alerts. Optional: shipment_id.",
        "required_params": [],
    },
    "explain_shipment": {
        "fn": tool_explain_shipment,
        "description": "Generate an AI explanation for a shipment's risk situation.",
        "required_params": ["shipment_id"],
    },
}


def call_tool(tool_name: str, params: dict) -> dict:
    """
    Call a registered tool by name with the given parameters dict.

    This is the main entry point used by both the MCP server and tests.

    Parameters
    ----------
    tool_name : str   Name of the tool (key in TOOLS).
    params    : dict  Tool arguments.

    Returns
    -------
    dict  Tool result, or error dict if tool not found / call fails.
    """
    if tool_name not in TOOLS:
        return {"error": "Unknown tool: '%s'" % tool_name,
                "available_tools": list(TOOLS.keys())}
    tool = TOOLS[tool_name]
    try:
        return tool["fn"](**params)
    except TypeError as exc:
        return {"error": "Invalid parameters for tool '%s': %s" % (tool_name, exc)}
    except Exception as exc:  # noqa: BLE001
        logger.error("Tool '%s' raised: %s", tool_name, exc)
        return {"error": "Tool execution error: %s" % str(exc)}


# ---------------------------------------------------------------------------
# MCP server entry point (only runs when SDK is available)
# ---------------------------------------------------------------------------

def _build_mcp_server():
    """Construct and return the MCP Server object with all tools registered."""
    if not _MCP_AVAILABLE:
        raise RuntimeError("mcp package is not installed. Run: pip install mcp")

    server = Server("smartroute-ai")

    @server.list_tools()
    async def list_tools():
        tool_list = []
        for name, meta in TOOLS.items():
            # Build input schema
            props = {}
            required = meta["required_params"]
            for p in required:
                props[p] = {"type": "string", "description": p}
            # get_temperature_alerts has optional shipment_id
            if name == "get_temperature_alerts":
                props["shipment_id"] = {
                    "type": "string",
                    "description": "Optional shipment ID to filter alerts.",
                }
            tool_list.append(
                mcp_types.Tool(
                    name=name,
                    description=meta["description"],
                    inputSchema={
                        "type": "object",
                        "properties": props,
                        "required": required,
                    },
                )
            )
        return tool_list

    @server.call_tool()
    async def call_tool_handler(name: str, arguments: dict):
        result = call_tool(name, arguments)
        return [mcp_types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str),
        )]

    return server


async def _run_stdio_server():
    server = _build_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    if not _MCP_AVAILABLE:
        print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)
    asyncio.run(_run_stdio_server())
