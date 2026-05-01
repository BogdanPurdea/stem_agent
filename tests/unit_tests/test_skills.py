"""Unit tests for the skills loader and parser."""

from __future__ import annotations
from stem_agent.skills import (
    SkillInfo,
    _parse_frontmatter,
    load_skills,
    skills_description,
    load_skill_from_directory,
)


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------


def test_parse_frontmatter_valid() -> None:
    text = """---
name: "test-skill"
description: 'A skill for testing'
author: agent
---
# Content
"""
    result = _parse_frontmatter(text)
    assert result == {
        "name": "test-skill",
        "description": "A skill for testing",
        "author": "agent",
    }


def test_parse_frontmatter_missing() -> None:
    text = "# Just some markdown"
    assert _parse_frontmatter(text) == {}


def test_parse_frontmatter_malformed() -> None:
    text = """---
invalid frontmatter no colon
---
"""
    assert _parse_frontmatter(text) == {}


# ---------------------------------------------------------------------------
# Skills loader
# ---------------------------------------------------------------------------


def test_skills_loader_empty_dir(tmp_path) -> None:
    """An empty directory returns no skills."""
    assert load_skills(str(tmp_path)) == []


def test_skills_loader_finds_skill(tmp_path) -> None:
    """A valid SKILL.md with frontmatter is discovered."""
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A test skill.\n---\n\n# Test\n"
    )
    result = load_skills(str(tmp_path))
    assert len(result) == 1
    assert result[0].name == "test-skill"
    assert "test skill" in result[0].description.lower()


def test_skills_loader_fallback_name(tmp_path) -> None:
    """If name is missing from frontmatter, use folder name."""
    skill_dir = tmp_path / "folder_name"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\ndescription: only desc\n---\n")

    result = load_skills(str(tmp_path))
    assert result[0].name == "folder_name"


def test_skills_loader_nested_directories(tmp_path) -> None:
    """Ensure os.walk correctly finds nested skills."""
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    (nested / "SKILL.md").write_text("---\nname: nested-skill\n---\n")

    result = load_skills(str(tmp_path))
    assert len(result) == 1
    assert result[0].name == "nested-skill"


def test_load_skill_from_directory_missing(tmp_path) -> None:
    assert load_skill_from_directory(str(tmp_path)) is None


def test_skills_description_empty() -> None:
    assert skills_description([]) == "(no skills discovered)"


def test_skills_description_with_items() -> None:
    items = [SkillInfo(name="a", description="desc a", file_path="/x")]
    desc = skills_description(items)
    assert "**a**" in desc
