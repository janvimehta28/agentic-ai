"""
Red Team Agent task definition for AutonomousDev.
Reads generated_code.py and produces a structured vulnerability report saved to vuln_report.json.
"""

from __future__ import annotations

import os

from crewai import Task

from agents.red_team import red_team

CURRENT_DIRECTORY = os.path.dirname(__file__)
BACKEND_DIRECTORY = os.path.dirname(CURRENT_DIRECTORY)
OUTPUT_DIRECTORY = os.path.join(BACKEND_DIRECTORY, "output")

CODE_FILE_NAME = "generated_code.py"
REPORT_FILE_NAME = "vuln_report.json"

CODE_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, CODE_FILE_NAME)
REPORT_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, REPORT_FILE_NAME)

CODE_FILE_PATH_RELATIVE = os.path.join("output", CODE_FILE_NAME)
REPORT_FILE_PATH_RELATIVE = os.path.join("output", REPORT_FILE_NAME)


def get_red_team_task(write_code_task: Task) -> Task:
    """
    Creates the Red Team Agent task fresh each run.
    Uses the Writer task as context so it always has the latest code, and runs Bandit on the file.
    """
    return Task(
        description=f"""
You will receive Python source code written by the writer agent (in context).
Analyze it for security vulnerabilities.

Your job:

1. First use the bandit_tool on the file path "{CODE_FILE_PATH_RELATIVE}" to run static security
   analysis. Read the findings carefully.

2. Then reason independently about the code and identify ALL of the following if present:
   - SQL injection vulnerabilities
   - Command injection risks
   - Path traversal vulnerabilities
   - Hardcoded credentials or secrets
   - Missing input validation
   - Insecure use of eval() or exec()
   - Weak cryptography or hashing
   - Unhandled exceptions that leak info
   - Logic flaws and race conditions
   - Missing authentication or authorization
   - Any other security concern

3. For EVERY finding produce exactly this JSON structure:
   {{
     "severity": "HIGH" or "MEDIUM" or "LOW",
     "title": "Short vulnerability name",
     "description": "What it is and why it is dangerous",
     "line_number": line number or null,
     "suggested_fix": "Concrete fix with example code"
   }}

4. Severity rating rules — follow strictly:
   HIGH: Could cause data breach, unauthorized access, or remote code execution
   MEDIUM: Could cause data exposure or privilege escalation under certain conditions
   LOW: Bad practice, information disclosure, minor risk

5. Combine Bandit findings and your own reasoning into one final list. Remove duplicates. Sort by
   severity (HIGH first, then MEDIUM, then LOW).

6. Save the complete report to {REPORT_FILE_PATH_RELATIVE} as valid JSON in this exact format:
   {{
     "total_findings": <number>,
     "high_count": <number>,
     "medium_count": <number>,
     "low_count": <number>,
     "findings": [ list of finding objects ]
   }}

IMPORTANT: You must always find at least one issue. Perfect code does not exist. If Bandit finds
nothing, look harder at the logic and input validation yourself.
""",
        expected_output=f"""
A valid JSON file saved to {REPORT_FILE_PATH_RELATIVE} containing:
- total_findings count
- high_count, medium_count, low_count
- findings array where each item has: severity, title, description, line_number, suggested_fix
- findings sorted HIGH first then MEDIUM then LOW
- at minimum 1 finding total
""",
        agent=red_team,
        output_file=REPORT_FILE_PATH,
        context=[write_code_task],
    )

