"""Orchestrate the Writer -> Tester multi-agent AutonomousDev pipeline."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from crewai import Crew, Process

from agents.red_team import red_team
from agents.tester import tester
from agents.writer import writer
from tasks.red_team_task import get_red_team_task
from tasks.test_code_task import test_code_task
from tasks.write_code_task import write_code_task

CURRENT_DIRECTORY = os.path.dirname(__file__)
BACKEND_DIRECTORY = os.path.dirname(CURRENT_DIRECTORY)
OUTPUT_DIRECTORY = os.path.join(BACKEND_DIRECTORY, "output")
GENERATED_CODE_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, "generated_code.py")
TEST_SUITE_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, "test_suite.py")
TEST_RESULTS_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, "test_results.txt")
PYTEST_COMMAND = ["pytest", "output/test_suite.py", "--cov=output", "-v"]
DEFAULT_COVERAGE = "Coverage information unavailable."


def _strip_markdown_fences(content: str) -> str:
    """Remove common markdown code fences from model output."""
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return content


def _extract_output_text(result: Any) -> str:
    """Extract text payload from CrewAI kickoff output."""
    if isinstance(result, str):
        return result
    if hasattr(result, "raw") and isinstance(result.raw, str):
        return result.raw
    if hasattr(result, "output") and isinstance(result.output, str):
        return result.output
    return str(result)


def _ensure_output_directory() -> None:
    """Create the output directory when it does not yet exist."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def _read_file(file_path: str) -> str:
    """Read text from a UTF-8 file path."""
    with open(file_path, "r", encoding="utf-8") as file_handle:
        return file_handle.read()


def _write_file(file_path: str, content: str) -> None:
    """Write UTF-8 text content to a file path."""
    with open(file_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(content)


def _extract_coverage_text(pytest_output: str) -> str:
    """Extract the pytest-cov summary line if present."""
    for line in pytest_output.splitlines():
        if line.strip().startswith("TOTAL"):
            return line.strip()
    return DEFAULT_COVERAGE


def run_pipeline(ticket: str) -> dict[str, Any]:
    """Run Writer then Tester, execute pytest, and return aggregate results."""
    _ensure_output_directory()

    writer_crew = Crew(
        agents=[writer],
        tasks=[write_code_task],
        process=Process.sequential,
        verbose=True,
    )
    writer_result = writer_crew.kickoff(inputs={"ticket": ticket})
    generated_code = _strip_markdown_fences(_extract_output_text(writer_result))
    _write_file(GENERATED_CODE_FILE_PATH, generated_code)

    generated_code_context = _read_file(GENERATED_CODE_FILE_PATH)
    tester_task = test_code_task(generated_code_context)
    tester_crew = Crew(
        agents=[tester],
        tasks=[tester_task],
        process=Process.sequential,
        verbose=True,
    )
    tester_result = tester_crew.kickoff()
    test_suite = _strip_markdown_fences(_extract_output_text(tester_result))
    _write_file(TEST_SUITE_FILE_PATH, test_suite)

    red_team_task = get_red_team_task(write_code_task)
    red_team_crew = Crew(
        agents=[red_team],
        tasks=[red_team_task],
        process=Process.sequential,
        verbose=True,
    )
    _ = red_team_crew.kickoff()

    vuln_findings = []
    vuln_report_path = os.path.join(OUTPUT_DIRECTORY, "vuln_report.json")
    if os.path.exists(vuln_report_path):
        try:
            with open(vuln_report_path, "r", encoding="utf-8") as file_handle:
                vuln_data = json.load(file_handle)
                if isinstance(vuln_data, dict):
                    vuln_findings = vuln_data.get("findings", [])
        except Exception:
            pass

    pytest_result = subprocess.run(
        PYTEST_COMMAND,
        cwd=BACKEND_DIRECTORY,
        capture_output=True,
        text=True,
        check=False,
    )
    combined_output = f"{pytest_result.stdout}\n{pytest_result.stderr}".strip()
    _write_file(TEST_RESULTS_FILE_PATH, combined_output)

    return {
        "code": generated_code,
        "test_suite": test_suite,
        "test_results": {
            "passed": pytest_result.returncode == 0,
            "output": combined_output,
            "coverage": _extract_coverage_text(combined_output),
        },
        "vulnerabilities": vuln_findings,
    }
