"""Centralised configuration for the STEM Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass(frozen=True)
class StemConfig:
    """Configuration for the STEM Agent — override via environment variables."""

    # LLM ------------------------------------------------------------------
    model: str = field(
        default_factory=lambda: os.getenv("STEM_AGENT_MODEL", "openai:gpt-4o")
    )

    # Safeguards -----------------------------------------------------------
    circuit_breaker_threshold: int = field(
        default_factory=lambda: int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "3"))
    )

    # Skills ---------------------------------------------------------------
    skills_dir: str = field(
        default_factory=lambda: os.getenv(
            "STEM_SKILLS_DIR",
            os.path.join(os.path.dirname(__file__), os.pardir, "skills"),
        )
    )

    # Search ---------------------------------------------------------------
    tavily_api_key: str | None = field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY")
    )

    # Ollama ---------------------------------------------------------------
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )


# Singleton — import this from anywhere
CONFIG = StemConfig()
