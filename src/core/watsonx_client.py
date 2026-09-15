"""
watsonx_client.py
=================
Thin wrapper around IBM watsonx.ai.

Reads credentials from environment variables only — never hard-coded.
Falls back to a clearly labelled mock response when credentials are absent,
so the whole application still runs without an IBM account.

Environment variables
---------------------
    WATSONX_API_KEY      IBM Cloud API key          (required for real AI)
    WATSONX_PROJECT_ID   watsonx.ai project ID      (required for real AI)
    WATSONX_URL          Inference endpoint          (optional, has default)
    WATSONX_MODEL_ID     Model to use                (optional, has default)

Public API
----------
    generate_ai_explanation(prompt: str) -> dict
        Returns {"text": str, "source": "watsonx"|"mock", "model_id": str, "error": str|None}

    is_watsonx_configured() -> bool
        True when both WATSONX_API_KEY and WATSONX_PROJECT_ID are set.
"""

import logging
import os

logger = logging.getLogger(__name__)

_DEFAULT_URL = "https://us-south.ml.cloud.ibm.com"
_DEFAULT_MODEL = "ibm/granite-13b-instruct-v2"
_MOCK_TAG = "[MOCK - set WATSONX_API_KEY and WATSONX_PROJECT_ID to enable real AI] "


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    _dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()
except Exception:
    pass

def _credentials():
    """Return credentials dict or None if not configured."""
    key = (os.environ.get("WATSONX_API_KEY") or os.environ.get("WATSONX_APIKEY") or "").strip()
    pid = os.environ.get("WATSONX_PROJECT_ID", "").strip()
    if not key or not pid or key == "your_api_key_here" or pid == "your_project_id_here":
        return None
    return {
        "api_key": key,
        "project_id": pid,
        "url": os.environ.get("WATSONX_URL", _DEFAULT_URL).strip(),
        "model_id": os.environ.get("WATSONX_MODEL_ID", _DEFAULT_MODEL).strip(),
    }


def _call_watsonx(prompt, creds):
    """Send prompt to watsonx.ai and return result dict."""
    try:
        from ibm_watsonx_ai import APIClient, Credentials          # type: ignore
        from ibm_watsonx_ai.foundation_models import ModelInference # type: ignore
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames # type: ignore

        client = APIClient(Credentials(url=creds["url"], api_key=creds["api_key"]))
        params = {
            GenTextParamsMetaNames.MAX_NEW_TOKENS: 400,
            GenTextParamsMetaNames.TEMPERATURE: 0.5,
            GenTextParamsMetaNames.DECODING_METHOD: "sample",
        }
        model = ModelInference(
            model_id=creds["model_id"],
            api_client=client,
            project_id=creds["project_id"],
            params=params,
        )
        text = model.generate_text(prompt=prompt)
        return {"text": text.strip(), "source": "watsonx",
                "model_id": creds["model_id"], "error": None}

    except ImportError:
        logger.warning("ibm-watsonx-ai SDK not installed; using mock.")
        return _mock(prompt, "SDK not installed")
    except Exception as exc:                          # noqa: BLE001
        logger.error("watsonx call failed: %s", exc)
        return _mock(prompt, str(exc))


def _mock(prompt, error=None):
    """Return a canned mock response."""
    text = (
        _MOCK_TAG
        + "Based on the available supply chain data, this shipment is experiencing "
        + "disruptions that may impact delivery timelines and cargo integrity. "
        + "Key risk factors include port congestion, weather conditions, and carrier "
        + "availability. Recommended actions: monitor closely, consider alternative "
        + "routing through unaffected ports, and notify the consignee of potential "
        + "delays. For cold-chain cargo verify temperature compliance at each waypoint."
    )
    return {"text": text, "source": "mock", "model_id": "mock", "error": error}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ai_explanation(prompt):
    """
    Generate an AI explanation for the given prompt.

    Parameters
    ----------
    prompt : str

    Returns
    -------
    dict
        text      (str)        The generated text.
        source    (str)        "watsonx" or "mock".
        model_id  (str)        Model used, or "mock".
        error     (str|None)   Error message if call failed.
    """
    if not prompt or not str(prompt).strip():
        return {"text": "No prompt provided.", "source": "mock",
                "model_id": "mock", "error": "empty prompt"}

    creds = _credentials()
    if creds is None:
        logger.info("watsonx credentials not set — using mock response.")
        return _mock(prompt)
    return _call_watsonx(prompt, creds)


def is_watsonx_configured():
    """
    Return True when WATSONX_API_KEY and WATSONX_PROJECT_ID are both set.

    Useful for UI code to show 'AI Powered' vs 'Demo Mode' badges.
    """
    return _credentials() is not None
