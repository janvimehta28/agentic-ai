"""Define the code-generation task assigned to the Writer Agent."""

from __future__ import annotations

import os

from crewai import Task

from agents.writer import writer

OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_FILE_NAME = "generated_code.py"
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE_NAME)
TASK_DESCRIPTION = (
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
    """
        IMPORTANT: Match the complexity of your output to the 
        complexity of the ticket. A simple task needs simple code. 
        Do not over-engineer. Do not add unnecessary abstractions, 
        logging, or error handling that the ticket did not ask for..
"""
)
EXPECTED_OUTPUT = (
    "A complete, executable Python file saved to /output/generated_code.py with proper "
    "type hints, docstrings, and inline comments. The code must handle edge cases and "
    "be structured for unit testing."
)

write_code_task = Task(
    description=TASK_DESCRIPTION,
    expected_output=EXPECTED_OUTPUT,
    agent=writer,
    output_file=OUTPUT_FILE_PATH,
)
