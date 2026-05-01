"""Node for loading full skill content into the state context."""

from __future__ import annotations

from stem_agent.skills import get_skill_by_name
from stem_agent.state import StemState


def load_skills(state: StemState) -> dict:
    """Read the skill manifest and load the full markdown content for each selected skill."""
    manifest = state.get("skill_manifest") or []
    if not manifest:
        return {"skills_content": "(no specialized skills required)"}

    loaded_skills: list[str] = []
    for skill_name in manifest:
        skill_info = get_skill_by_name(skill_name)
        if skill_info:
            try:
                with open(skill_info.file_path, encoding="utf-8") as f:
                    content = f.read()
                
                # Strip frontmatter for the agent's prompt
                import re
                content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
                
                loaded_skills.append(f"## {skill_info.name}\n{content.strip()}")
            except Exception as e:
                loaded_skills.append(f"## {skill_name}\nError loading skill: {e}")
        else:
            loaded_skills.append(f"## {skill_name}\nSkill documentation not found.")

    return {"skills_content": "\n\n---\n\n".join(loaded_skills)}
