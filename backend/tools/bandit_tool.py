"""
Bandit static security analysis tool for the Red Team Agent. Runs Bandit CLI on a Python file
and returns structured JSON findings.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Dict

from crewai.tools import tool

CODE_FILE_PATH = "output/generated_code.py"
BANDIT_TIMEOUT = 30

STATUS_SUCCESS = "success"
STATUS_ERROR = "error"


def _error_result(error_message: str, raw_output: str = "") -> Dict[str, Any]:
    """Create a consistent error payload for Bandit tool failures."""
    return {
        "status": STATUS_ERROR,
        "error": error_message,
        "raw_output": raw_output,
        "findings": [],
        "metrics": {},
    }


@tool("bandit_tool")
def bandit_tool(file_path: str) -> Dict[str, Any]:
    """Run Bandit static analysis against a Python file and return JSON findings."""
    if not os.path.exists(file_path):
        return {
            "status": STATUS_ERROR,
            "error": f"File not found: {file_path}",
            "findings": [],
            "metrics": {},
        }

    command = [
        "python",
        "-m",
        "bandit",
        "-r",
        file_path,
        "-f",
        "json",
        "-ll",
        "--exit-zero",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=BANDIT_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _error_result(f"Bandit timed out after {BANDIT_TIMEOUT} seconds")
    except Exception as error:  # pylint: disable=broad-except
        return _error_result(f"Bandit execution failed: {error}")

    stdout_text = result.stdout or ""
    stderr_text = result.stderr or ""
    combined_text = f"{stdout_text}\n{stderr_text}".strip()

    if "No module named bandit" in combined_text or "ModuleNotFoundError" in combined_text:
        return _error_result(
            "Bandit is not installed. Install it with: pip install bandit",
            raw_output=combined_text,
        )

    try:
        parsed = json.loads(stdout_text)
    except json.JSONDecodeError:
        return _error_result("Bandit output could not be parsed", raw_output=combined_text)

    results = parsed.get("results", []) if isinstance(parsed, dict) else []
    metrics = parsed.get("metrics", {}) if isinstance(parsed, dict) else {}

    return {
        "status": STATUS_SUCCESS,
        "total_findings": len(results),
        "findings": results,
        "metrics": metrics,
        "raw_output": stdout_text,
    }

