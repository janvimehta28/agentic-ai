"""Define the Writer Agent that generates production-quality Python code."""

from __future__ import annotations

import logging
import os

from crewai import Agent, LLM
from dotenv import load_dotenv

from tools.sandbox_tool import sandbox_tool

load_dotenv()

LOGGER = logging.getLogger(__name__)

GROQ_API_KEY_ENV = "GROQ_API_KEY"
GROQ_MODEL = "groq/llama-3.3-70b-versatile"

WRITER_ROLE = "Senior Software Engineer"
WRITER_GOAL = (
    "Write clean, modular, well-documented Python code from a task specification. "
    "The code must be syntactically valid, executable, and structured so that a "
    "separate QA agent can easily write unit tests for it. "
    "Always return your final answer as a fenced ```python code block. "
    "Do NOT include example usage or __main__ blocks unless explicitly asked."
)
WRITER_BACKSTORY = (
    "You are an expert Python developer with 10 years of experience. You write "
    "production-quality code on the first attempt. You never use vague variable "
    "names. You always handle edge cases explicitly (None inputs, empty collections, "
    "type mismatches, boundary values). You structure your code so that every "
    "function does exactly one thing and can be tested in isolation. "
    "You add Google-style docstrings to every public function. "
    "You annotate every function signature with Python type hints."
)

# ── LLM temperature: 0.2 keeps code deterministic but not robotic ────────────
_LLM_TEMPERATURE = 0.2
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
        LOGGER.exception("Failed to initialize Groq LLM for writer agent.")
        raise RuntimeError(f"Groq API initialization failed: {error}") from error


writer = Agent(
    role=WRITER_ROLE,
    goal=WRITER_GOAL,
    backstory=WRITER_BACKSTORY,
    verbose=True,
    allow_delegation=False,
    # max_iter caps the agent's internal reasoning loops — prevents infinite tool calls
    max_iter=5,
    tools=[sandbox_tool],
    llm=_create_llm(),
)