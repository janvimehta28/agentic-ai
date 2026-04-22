"""Run the AutonomousDev Writer Agent pipeline end-to-end."""

from __future__ import annotations

import ast
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any

from crewai import Crew, Process

from agents.writer import writer
from tasks.write_code_task import write_code_task
from tools.sandbox_tool import sandbox_tool

LOGGER = logging.getLogger(__name__)
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_FILE_NAME = "generated_code.py"
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE_NAME)
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"


@dataclass
class PipelineResult:
    """Structured result returned by the Writer Agent pipeline."""

    code: str
    sandbox_status: str
    execution_error: str
    file_path: str


writer_crew = Crew(
    agents=[writer],
    tasks=[write_code_task],
    process=Process.sequential,
    verbose=True,
)

# Placeholder: Tester Agent will be added here later.
# Placeholder: Red Team Agent will be added here later.


def _extract_generated_code(result: Any) -> str:
    """Extract generated code text from CrewAI kickoff output."""
    if isinstance(result, str):
        return result
    if hasattr(result, "raw") and isinstance(result.raw, str):
        return result.raw
    if hasattr(result, "output") and isinstance(result.output, str):
        return result.output
    return str(result)


def _save_generated_code(code: str) -> str:
    """Persist generated code to the configured output file path."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as output_file:
        output_file.write(code)
    return OUTPUT_FILE_PATH


def run_pipeline(ticket: str) -> PipelineResult:
    """Execute the Writer Agent pipeline for a single ticket."""
    try:
        crew_result = writer_crew.kickoff(inputs={"ticket": ticket})
    except Exception as error:  # pylint: disable=broad-except
        LOGGER.exception("Crew kickoff failed.")
        raise RuntimeError(f"Writer crew execution failed: {error}") from error

    code = _extract_generated_code(crew_result)
    try:
        ast.parse(code)
    except SyntaxError as error:
        return PipelineResult(
            code=code,
            sandbox_status=STATUS_ERROR,
            execution_error=f"Syntax validation failed: {error}",
            file_path="",
        )

    sandbox_result = sandbox_tool(code)
    saved_path = _save_generated_code(code)
    return PipelineResult(
        code=code,
        sandbox_status=sandbox_result.get("status", STATUS_ERROR),
        execution_error=sandbox_result.get("error", ""),
        file_path=saved_path,
    )


def main() -> None:
    """Run a local smoke test for the Writer Agent pipeline."""
    ticket = (
        "Python program to add two numbers."
    )
    try:
        result = run_pipeline(ticket)
        print(asdict(result))
    except Exception as error:  # pylint: disable=broad-except
        print(f"Pipeline failed cleanly: {error}")


if __name__ == "__main__":
    main()


def test_full_pipeline() -> None:
    """Run the full Writer + Tester pipeline with a realistic login ticket."""
    from pipeline.crew import run_pipeline as run_full_pipeline

    ticket = (
        "Build a login endpoint that validates username and password against a "
        "SQLite database."
    )
    result = run_full_pipeline(ticket)
    print(result)
