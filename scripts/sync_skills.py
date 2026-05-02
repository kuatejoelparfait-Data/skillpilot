#!/usr/bin/env python3
"""
Sync all skills from claude-skills library into devpilot/src/devpilot/skills/.
Run from the root of the claude-skills repo: python devpilot/scripts/sync_skills.py
"""
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
SKILLS_OUT = Path(__file__).parent.parent / "src" / "devpilot" / "skills"

MAPPINGS = {
    "engineering": (REPO_ROOT / "engineering", "*/SKILL.md"),
    "engineering-team": (REPO_ROOT / "engineering-team", "*/SKILL.md"),
    "marketing": (REPO_ROOT / "marketing-skill", "*/SKILL.md"),
    "product": (REPO_ROOT / "product-team", "*/SKILL.md"),
    "strategy": (REPO_ROOT / "c-level-advisor", "*/SKILL.md"),
    "project-management": (REPO_ROOT / "project-management", "*/SKILL.md"),
    "compliance": (REPO_ROOT / "ra-qm-team", "*/SKILL.md"),
    "business": (REPO_ROOT / "business-growth", "*/SKILL.md"),
    "finance": (REPO_ROOT / "finance", "*/SKILL.md"),
    "commands": (REPO_ROOT / "commands", "*.md"),
}

def sync():
    total = 0
    for category, (base, pattern) in MAPPINGS.items():
        out_dir = SKILLS_OUT / category
        out_dir.mkdir(parents=True, exist_ok=True)
        for skill_file in base.glob(pattern):
            if skill_file.name == "SKILL.md":
                skill_name = skill_file.parent.name
            else:
                skill_name = skill_file.stem
            dest = out_dir / f"{skill_name}.md"
            shutil.copy2(skill_file, dest)
            print(f"  [{category}] {skill_name}")
            total += 1
    print(f"\nSynced {total} skills.")

if __name__ == "__main__":
    sync()
