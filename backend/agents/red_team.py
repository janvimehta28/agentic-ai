"""
Red Team Agent for AutonomousDev. Analyzes generated code for security vulnerabilities, logic flaws,
and dangerous patterns using Bandit and LLM reasoning.
"""

from __future__ import annotations

import logging
import os

from crewai import Agent, LLM
from dotenv import load_dotenv

from tools.bandit_tool import bandit_tool

load_dotenv()

LOGGER = logging.getLogger(__name__)

GROQ_API_KEY_ENV = "GROQ_API_KEY"
GROQ_MODEL = "groq/llama-3.3-70b-versatile"

RED_TEAM_ROLE = "Security Reviewer"
RED_TEAM_GOAL = (
    "Analyze the provided Python code like an attacker would. Find every security vulnerability, "
    "logic flaw, injection risk, and dangerous pattern. Assume all code is insecure until proven "
    "otherwise. Return a structured report with severity ratings and concrete fix suggestions for "
    "every finding."
)
RED_TEAM_BACKSTORY = (
    "You are a senior security engineer and penetration tester with 15 years of experience "
    "breaking production systems. You think like an attacker, not a defender. You never give code "
    "the benefit of the doubt. You have found critical vulnerabilities in Fortune 500 companies. "
    "You know every OWASP Top 10 vulnerability by heart. You always find at least one issue "
    "because perfect code does not exist. You rate findings ruthlessly — if it could cause data "
    "loss or unauthorized access it is HIGH, period."
)

_LLM_TEMPERATURE = 0.1
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
        LOGGER.exception("Failed to initialize Groq LLM for red team agent.")
        raise RuntimeError(f"Groq API initialization failed: {error}") from error


red_team = Agent(
    role=RED_TEAM_ROLE,
    goal=RED_TEAM_GOAL,
    backstory=RED_TEAM_BACKSTORY,
    llm=_create_llm(),
    tools=[bandit_tool],
    verbose=True,
    allow_delegation=False,
    max_iter=5,
)

