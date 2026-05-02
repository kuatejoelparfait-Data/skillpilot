from pathlib import Path
from devpilot.core.skills import SkillLoader, FREE_CATEGORIES

def _make_fake_skills(tmp_path: Path) -> Path:
    for cat in ["engineering", "marketing", "commands"]:
        d = tmp_path / cat
        d.mkdir(parents=True)
        (d / "my-skill.md").write_text(f"# {cat} skill prompt")
    return tmp_path

def test_list_all_categories(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    cats = loader.categories()
    assert "engineering" in cats
    assert "marketing" in cats

def test_list_skills_in_category(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    skills = loader.list_category("engineering")
    assert "my-skill" in skills

def test_load_free_skill_without_license(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    content = loader.load("my-skill", is_premium_user=False)
    assert "engineering skill prompt" in content

def test_load_premium_skill_without_license_raises(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    try:
        loader.load("my-skill", category="marketing", is_premium_user=False)
        assert False, "Should raise PermissionError"
    except PermissionError:
        pass

def test_search_skills(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    results = loader.search("skill")
    assert len(results) > 0
