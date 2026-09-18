"""
test_report_exporter.py — Tests for Executive Report Generator
"""

import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_TESTS_DIR, "..", "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import pytest
from core.report_exporter import (
    generate_executive_report_markdown,
    generate_executive_report_html,
)

def test_markdown_report_valid_shipment():
    report = generate_executive_report_markdown("SHP-001")
    assert isinstance(report, str)
    assert len(report) > 100
    assert "SmartRoute AI" in report
    assert "SHP-001" in report
    assert "Risk Score" in report
    assert "Recommended Operational Action" in report

def test_markdown_report_cold_chain_shipment():
    report = generate_executive_report_markdown("SHP-002")
    assert "Cold-Chain Sensor" in report
    assert "SHP-002" in report

def test_markdown_report_unknown_shipment():
    report = generate_executive_report_markdown("SHP-UNKNOWN")
    assert isinstance(report, str)
    assert "SHP-UNKNOWN" in report

def test_html_report_valid_shipment():
    html = generate_executive_report_html("SHP-001")
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html
    assert "SHP-001" in html
    assert "SmartRoute AI" in html
    assert "Recommended Operational Action" in html
    assert "</body>" in html

def test_html_report_cold_chain_shipment():
    html = generate_executive_report_html("SHP-002")
    assert "Cold-Chain Status" in html
    assert "SHP-002" in html
