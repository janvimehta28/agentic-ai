"""Run generated Python code safely with syntax checks first."""

from __future__ import annotations

import ast
import os
import subprocess
from dataclasses import asdict, dataclass
from typing import Any, Dict

from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

EXECUTION_TIMEOUT_SECONDS = 10
TEMP_DIRECTORY = os.path.join(os.sep, "tmp")
TEMP_FILE_NAME = "test_exec.py"
TEMP_FILE_PATH = os.path.join(TEMP_DIRECTORY, TEMP_FILE_NAME)
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
E2B_API_KEY_ENV = "E2B_API_KEY"


@dataclass
class SandboxExecutionResult:
    """Structured response for sandbox execution attempts."""

    status: str
    output: str
    error: str


def _validate_syntax(code: str) -> SandboxExecutionResult | None:
    """Validate Python syntax and return an error result if invalid."""
    try:
        ast.parse(code)
    except SyntaxError as error:
        return SandboxExecutionResult(
            status=STATUS_ERROR,
            output="",
            error=f"Syntax validation failed: {error}",
        )
    return None


def _run_with_e2b(code: str) -> SandboxExecutionResult:
    """Execute code using E2B when an API key is available."""
    from e2b_code_interpreter import Sandbox

    sandbox = Sandbox(api_key=os.getenv(E2B_API_KEY_ENV))
    execution = sandbox.run_code(code)
    stderr_text = "\n".join(execution.logs.stderr) if execution.logs.stderr else ""
    stdout_text = "\n".join(execution.logs.stdout) if execution.logs.stdout else ""

    if execution.error:
        return SandboxExecutionResult(
            status=STATUS_ERROR,
            output=stdout_text,
            error=str(execution.error),
        )

    return SandboxExecutionResult(
        status=STATUS_SUCCESS,
        output=stdout_text,
        error=stderr_text,
    )


def _run_with_subprocess(code: str) -> SandboxExecutionResult:
    """Execute code locally in a temporary file with timeout protection."""
    os.makedirs(TEMP_DIRECTORY, exist_ok=True)
    with open(TEMP_FILE_PATH, "w", encoding="utf-8") as temp_file:
        temp_file.write(code)

    try:
        result = subprocess.run(
            ["python", TEMP_FILE_PATH],
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT_SECONDS,
            check=False,
        )
        if result.returncode != 0:
            return SandboxExecutionResult(
                status=STATUS_ERROR,
                output=result.stdout,
                error=result.stderr.strip() or "Execution failed with a non-zero exit code.",
            )
        return SandboxExecutionResult(
            status=STATUS_SUCCESS,
            output=result.stdout,
            error=result.stderr.strip(),
        )
    except subprocess.TimeoutExpired:
        return SandboxExecutionResult(
            status=STATUS_ERROR,
            output="",
            error=f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS} seconds.",
        )
    except Exception as error:  # pylint: disable=broad-except
        return SandboxExecutionResult(
            status=STATUS_ERROR,
            output="",
            error=f"Local sandbox execution failed: {error}",
        )


@tool("sandbox_tool")
def sandbox_tool(code: str) -> Dict[str, Any]:
    """Validate syntax, then execute Python code in E2B or locally."""
    syntax_error = _validate_syntax(code)
    if syntax_error is not None:
        return asdict(syntax_error)

    if os.getenv(E2B_API_KEY_ENV):
        try:
            return asdict(_run_with_e2b(code))
        except Exception as error:  # pylint: disable=broad-except
            return asdict(
                SandboxExecutionResult(
                    status=STATUS_ERROR,
                    output="",
                    error=f"E2B execution failed: {error}",
                )
            )

    return asdict(_run_with_subprocess(code))
