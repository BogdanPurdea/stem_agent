"""Centralised configuration for the STEM Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class StemConfig:
    """All tuneable knobs in one place.  Override via environment variables."""

    # LLM ------------------------------------------------------------------
    model: str = field(
        default_factory=lambda: os.getenv("STEM_AGENT_MODEL", "ollama:gemma4")
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

    # Ollama ---------------------------------------------------------------
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
    )


# Singleton — import this from anywhere
CONFIG = StemConfig()
