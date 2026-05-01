"""Local SKILL.md loader.

Scans a configurable directory for SKILL.md files, parses YAML frontmatter
and returns lightweight summaries that the Plan node can inject into its
LLM prompt.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from stem_agent.configuration import CONFIG


@dataclass(frozen=True)
class SkillInfo:
    """Lightweight representation of a discovered skill."""

    name: str
    description: str
    file_path: str


# Simple regex for YAML frontmatter between --- fences
_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---", re.DOTALL
)


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Extract key: value pairs from YAML frontmatter (minimal parser)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().strip('"').strip("'")
            value = value.strip().strip('"').strip("'")
            if key and value:
                result[key] = value
    return result


def load_skills(directory: str | None = None) -> list[SkillInfo]:
    """Scan *directory* (default: CONFIG.skills_dir) for SKILL.md files.

    Returns a list of :class:`SkillInfo` with name and description extracted
    from the YAML frontmatter.  Files without valid frontmatter are skipped.
    """
    skills_dir = directory or CONFIG.skills_dir
    skills_dir = os.path.abspath(skills_dir)

    if not os.path.isdir(skills_dir):
        return []

    found: list[SkillInfo] = []
    for root, _dirs, files in os.walk(skills_dir):
        for fname in files:
            if fname.upper() == "SKILL.MD":
                full_path = os.path.join(root, fname)
                try:
                    with open(full_path, encoding="utf-8") as fh:
                        content = fh.read()
                except OSError:
                    continue

                meta = _parse_frontmatter(content)
                name = meta.get("name", os.path.basename(root))
                description = meta.get("description", "No description.")
                found.append(
                    SkillInfo(name=name, description=description, file_path=full_path)
                )
    return found


def skills_description(skills: list[SkillInfo] | None = None) -> str:
    """Return a human-readable summary of discovered skills."""
    if skills is None:
        skills = load_skills()
    if not skills:
        return "(no skills discovered)"
    lines = [f"- **{s.name}**: {s.description}" for s in skills]
    return "\n".join(lines)
