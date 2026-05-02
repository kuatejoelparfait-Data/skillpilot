from pathlib import Path
from devpilot.core.skills import SkillLoader


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


def test_load_skill(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    content = loader.load("my-skill", category="engineering")
    assert "engineering skill prompt" in content


def test_load_skill_with_category(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    content = loader.load("my-skill", category="marketing")
    assert "marketing skill prompt" in content


def test_load_missing_skill_raises(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    try:
        loader.load("nonexistent-skill")
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_search_skills(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    results = loader.search("skill")
    assert len(results) > 0


def test_find_skill(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    result = loader.find("my-skill")
    assert result is not None
    cat, path = result
    assert cat in ["engineering", "marketing", "commands"]


def test_list_all(tmp_path):
    loader = SkillLoader(skills_root=_make_fake_skills(tmp_path))
    all_data = loader.list_all()
    assert "engineering" in all_data
    assert "skills" in all_data["engineering"]
