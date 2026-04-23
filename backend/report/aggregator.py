"""Render and persist the final AutonomousDev markdown report."""

from __future__ import annotations

import os
from typing import Any

from jinja2 import Environment, FileSystemLoader

CURRENT_DIRECTORY = os.path.dirname(__file__)
BACKEND_DIRECTORY = os.path.dirname(CURRENT_DIRECTORY)
OUTPUT_DIRECTORY = os.path.join(BACKEND_DIRECTORY, "output")
REPORT_DIRECTORY = CURRENT_DIRECTORY
TEMPLATE_FILE_NAME = "template.md.j2"
REPORT_OUTPUT_FILE = os.path.join(OUTPUT_DIRECTORY, "report.md")


def _load_template_environment() -> Environment:
    """Create a Jinja2 environment for the report template directory."""
    return Environment(loader=FileSystemLoader(REPORT_DIRECTORY), autoescape=False)


def _write_report_file(report_content: str) -> None:
    """Write the rendered markdown report to the backend output folder."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    with open(REPORT_OUTPUT_FILE, "w", encoding="utf-8") as file_handle:
        file_handle.write(report_content)


def _normalize_test_results(test_results: Any) -> dict[str, Any]:
    """Return a safe test results payload for template rendering."""
    if not isinstance(test_results, dict):
        return {"passed": False, "output": "No test output provided.", "coverage": "N/A"}
    return {
        "passed": bool(test_results.get("passed", False)),
        "output": str(test_results.get("output", "No test output provided.")),
        "coverage": str(test_results.get("coverage", "N/A")),
    }


def _normalize_vulnerabilities(vulnerabilities: Any) -> list[dict[str, str]]:
    """Return vulnerability findings in a template-safe list format."""
    if not isinstance(vulnerabilities, list):
        return []

    normalized_findings: list[dict[str, str]] = []
    for finding in vulnerabilities:
        if not isinstance(finding, dict):
            continue
        normalized_findings.append(
            {
                "title": str(finding.get("title", "Untitled finding")),
                "severity": str(finding.get("severity", "unknown")),
                "description": str(finding.get("description", "No description provided.")),
                "suggested_fix": str(finding.get("suggested_fix", "No suggested fix provided.")),
            }
        )
    return normalized_findings


def generate_report(pipeline_result: dict[str, Any]) -> str:
    """Generate the markdown report from pipeline output and save it to disk."""
    generated_code = pipeline_result.get("code", "")
    test_results = pipeline_result.get("test_results", {"passed": False, "output": "", "coverage": ""})
    vulnerabilities = pipeline_result.get("vulnerabilities", [])
    try:
        environment = _load_template_environment()
        template = environment.get_template(TEMPLATE_FILE_NAME)
        safe_generated_code = str(pipeline_result.get("code", "No generated code provided."))
        safe_test_results = _normalize_test_results(pipeline_result.get("test_results"))
        safe_vulnerabilities = _normalize_vulnerabilities(pipeline_result.get("vulnerabilities"))
        rendered_report = template.render(
            generated_code=safe_generated_code,
            test_results=safe_test_results,
            vulnerabilities=safe_vulnerabilities,
        )
        _write_report_file(rendered_report)
        return rendered_report
    except Exception as exc:  # pragma: no cover - defensive error boundary
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Failed to generate report: {exc}") from exc
