"""
Entry point for the Agentic AI multi-agent coding crew.

Agents
------
writer  → writes Python code from a task spec
tester  → writes a pytest suite for the writer's code

Run
---
    python main.py
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

from crewai import Crew, Process, Task

from agents.red_team import red_team
from agents.writer import writer
from agents.tester import tester
from tasks.red_team_task import get_red_team_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)

CURRENT_DIRECTORY = os.path.dirname(__file__)
OUTPUT_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "output")
GENERATED_CODE_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, "generated_code.py")
TEST_SUITE_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, "test_suite.py")
VULN_REPORT_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, "vuln_report.json")


DEMO_TICKET = (
    "Build a login endpoint that validates username and password against a database and returns a "
    "JWT token if credentials are valid"
)


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


def _get_write_code_task() -> Task:
    """Create the Writer task fresh each run."""
    return Task(
        description=(
            "You are given a software ticket.\n"
            "Ticket:\n"
            "{ticket}\n\n"
            "Write complete Python code that is executable and test-friendly.\n"
            "Requirements:\n"
            "- Use type hints on all function signatures.\n"
            "- Add docstrings to all functions.\n"
            "- Include inline comments for non-obvious logic.\n"
            "- Handle edge cases explicitly.\n"
            "- Keep functions modular and easy to unit test.\n"
            "- Return only valid Python code."
        ),
        expected_output=(
            "A complete, executable Python file saved to output/generated_code.py with proper type "
            "hints, docstrings, and inline comments. The code must handle edge cases and be "
            "structured for unit testing."
        ),
        agent=writer,
        output_file=GENERATED_CODE_FILE_PATH,
    )


def _get_write_tests_task(write_code_task: Task) -> Task:
    """Create the Tester task fresh each run, using Writer output as context."""
    return Task(
        description=(
            "You will receive Python source code written by the writer agent (in context). "
            "Write a complete pytest suite that covers:\n"
            "  • Happy-path behaviour for every public function\n"
            "  • Edge cases: None inputs, empty strings, zero, negative numbers\n"
            "  • Boundary values\n"
            "  • Expected exceptions (use pytest.raises)\n\n"
            "Instructions:\n"
            "- Return ONLY valid Python test code.\n"
            "- Do not include markdown fences, prose, or explanations.\n"
            "- The file should be named `test_suite.py`."
        ),
        expected_output=(
            "A complete pytest file saved to output/test_suite.py that thoroughly validates the "
            "provided generated code, including happy path, null inputs, boundary values, and type "
            "error scenarios."
        ),
        agent=tester,
        output_file=TEST_SUITE_FILE_PATH,
        context=[write_code_task],
    )


def build_crew() -> Crew:
    """
    Builds the complete AutonomousDev crew with all three agents. Tasks are created fresh each run
    so they always read the latest output files. Tester and Red Team run after Writer completes.
    """
    _ensure_output_directory()

    write_code_task = _get_write_code_task()
    write_tests_task = _get_write_tests_task(write_code_task)
    red_team_task = get_red_team_task(write_code_task)

    print("\n── Crew Debug ──")
    print("Total agents: 3")
    print(f"  Agent 1: {writer.role}")
    print(f"  Agent 2: {tester.role}")
    print(f"  Agent 3: {red_team.role}")
    print(f"  Task  1: {str(write_code_task.description)[:50]}")
    print(f"  Task  2: {str(write_tests_task.description)[:50]}")
    print(f"  Task  3: {str(red_team_task.description)[:50]}")
    print("────────────────\n")

    return Crew(
        agents=[writer, tester, red_team],
        tasks=[write_code_task, write_tests_task, red_team_task],
        process=Process.sequential,
        verbose=True,
    )


def run_pipeline(ticket: str) -> dict[str, Any]:
    """
    Runs the complete AutonomousDev pipeline.
    Writer → Tester → Red Team sequentially.
    """
    try:
        crew = build_crew()
        result = crew.kickoff(inputs={"ticket": ticket})

        if os.path.exists(GENERATED_CODE_FILE_PATH):
            _write_file(
                GENERATED_CODE_FILE_PATH, _strip_markdown_fences(_read_file(GENERATED_CODE_FILE_PATH))
            )
        if os.path.exists(TEST_SUITE_FILE_PATH):
            _write_file(
                TEST_SUITE_FILE_PATH, _strip_markdown_fences(_read_file(TEST_SUITE_FILE_PATH))
            )

        return {
            "status": "success",
            "result": _extract_output_text(result),
            "output_file": "output/generated_code.py",
            "test_file": "output/test_suite.py",
            "vuln_report": "output/vuln_report.json",
        }
    except FileNotFoundError as error:
        import traceback

        traceback.print_exc()
        return {
            "status": "error",
            "result": None,
            "error": str(error),
        }
    except Exception as error:  # pylint: disable=broad-except
        import traceback

        traceback.print_exc()
        return {
            "status": "error",
            "result": None,
            "error": str(error),
        }

def main() -> None:
    """Kick off the full pipeline and print outputs."""
    ticket = DEMO_TICKET
    if len(sys.argv) > 1 and sys.argv[1].strip():
        ticket = " ".join(sys.argv[1:]).strip()

    LOGGER.info("Starting AutonomousDev pipeline…")
    result = run_pipeline(ticket=ticket)
    print(result)


if __name__ == "__main__":
    main()