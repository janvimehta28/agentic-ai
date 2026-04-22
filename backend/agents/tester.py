"""Define the Tester Agent that generates pytest suites for code under test."""

from __future__ import annotations

import logging
import os

from crewai import Agent, LLM
from dotenv import load_dotenv

from tools.sandbox_tool import sandbox_tool   # ← ADD THIS (see explanation below)

load_dotenv()

LOGGER = logging.getLogger(__name__)

GROQ_API_KEY_ENV = "GROQ_API_KEY_TESTER"
GROQ_MODEL = "groq/llama-3.3-70b-versatile"

TESTER_ROLE = "QA Engineer"
TESTER_GOAL = (
    "Write a comprehensive pytest suite for Python code produced by the writer agent. "
    "You will receive the full source code as context. "
    "Cover: happy paths, None/empty inputs, boundary values, type errors, and "
    "any edge cases implied by the implementation. "
    "Always return your final answer as a fenced ```python code block. "
    "Import only from the standard library and pytest — never from the internet."
)
TESTER_BACKSTORY = (
    "You are a meticulous QA engineer with deep expertise in pytest, hypothesis-based "
    "property testing, and code coverage analysis. You assume every function is broken "
    "until tests prove otherwise. You read the implementation carefully before writing "
    "tests so you never test the wrong function signature. "
    "You parametrize tests wherever possible to maximise coverage with minimal code. "
    "You always add a docstring to every test function explaining what it verifies."
)

_LLM_TEMPERATURE = 0.1   # Even lower than writer — tests must be deterministic
_LLM_MAX_TOKENS = 4096


def _get_groq_api_key() -> str:
    """Fetch and validate the required Groq API key."""
    api_key = os.getenv(GROQ_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            "Missing GROQ_API_KEY in your .env file. "
            "Create an API key at https://console.groq.com/keys and set "
            "GROQ_API_KEY=<your_key>."
        )
    return api_key


def _create_llm() -> LLM:
    """Create a Groq-backed CrewAI LLM with clear error reporting."""
    try:
        return LLM(
            model=GROQ_MODEL,
            api_key=_get_groq_api_key(),
            temperature=_LLM_TEMPERATURE,
            max_tokens=_LLM_MAX_TOKENS,
        )
    except Exception as error:  # pylint: disable=broad-except
        LOGGER.exception("Failed to initialize Groq LLM for tester agent.")
        raise RuntimeError(f"Groq API initialization failed: {error}") from error


tester = Agent(
    role=TESTER_ROLE,
    goal=TESTER_GOAL,
    backstory=TESTER_BACKSTORY,
    verbose=True,
    allow_delegation=False,
    max_iter=5,
    # Give the tester the sandbox so it can actually RUN the tests it writes
    tools=[sandbox_tool],
    llm=_create_llm(),
)