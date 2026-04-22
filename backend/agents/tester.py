"""Define the Tester Agent that generates pytest suites for code under test."""

from __future__ import annotations

import logging
import os

from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)
GROQ_API_KEY_ENV = "GROQ_API_KEY"
TESTER_ROLE = "QA Engineer"
TESTER_GOAL = (
    "Write a comprehensive pytest suite for generated Python code. "
    "Assume the implementation is fragile until tests prove otherwise."
)
TESTER_BACKSTORY = (
    "You are a meticulous QA engineer. You assume the code is broken until proven "
    "otherwise. You design tests for happy paths, null inputs, boundary values, and "
    "type errors."
)
GROQ_MODEL = "groq/llama-3.3-70b-versatile"


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
    tools=[],
    llm=_create_llm(),
)
