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
import sys

from crewai import Crew, Process, Task

from agents.writer import writer
from agents.tester import tester

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


# ── Task specification ────────────────────────────────────────────────────────
# Change this string to any coding problem you want the crew to solve.
TASK_SPECIFICATION = """
Write a Python module called `calculator.py` that implements the following functions:
- add(a, b)        → returns a + b
- subtract(a, b)   → returns a - b
- multiply(a, b)   → returns a * b
- divide(a, b)     → returns a / b, raises ZeroDivisionError if b == 0

All inputs should accept int or float. Add full type hints and docstrings.
"""


# ── Task 1: Write the code ────────────────────────────────────────────────────
write_code_task = Task(
    description=(
        "You are given the following task specification:\n\n"
        f"{TASK_SPECIFICATION}\n\n"
        "Produce the complete Python source code. "
        "Return ONLY the code inside a fenced ```python block."
    ),
    expected_output=(
        "A single fenced ```python code block containing the complete, "
        "executable Python module described in the specification."
    ),
    agent=writer,
)

# ── Task 2: Write the tests ───────────────────────────────────────────────────
# KEY FIX: `context=[write_code_task]` passes the writer's output to the tester.
# Without this line the tester agent either never runs or has no code to test.
write_tests_task = Task(
    description=(
        "You will receive Python source code written by the writer agent (in context). "
        "Write a complete pytest suite that covers:\n"
        "  • Happy-path behaviour for every public function\n"
        "  • Edge cases: None inputs, empty strings, zero, negative numbers\n"
        "  • Boundary values\n"
        "  • Expected exceptions (use pytest.raises)\n\n"
        "Return ONLY the test code inside a fenced ```python block. "
        "The file should be named `test_solution.py`."
    ),
    expected_output=(
        "A single fenced ```python code block containing a complete pytest suite "
        "that can be run with `pytest test_solution.py` against the writer's code."
    ),
    agent=tester,
    context=[write_code_task],   # ← THIS IS THE FIX
)


# ── Assemble the crew ─────────────────────────────────────────────────────────
crew = Crew(
    agents=[writer, tester],
    tasks=[write_code_task, write_tests_task],  # order matters for sequential
    process=Process.sequential,                 # writer finishes → tester starts
    verbose=True,                               # shows agent banners in terminal
)


def main() -> None:
    """Kick off the crew and print both outputs."""
    LOGGER.info("Starting multi-agent coding crew…")
    try:
        result = crew.kickoff()
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.exception("Crew failed with an unexpected error.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("CREW FINISHED — FINAL OUTPUT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()