from devpilot.core.skills import SkillLoader


def test_skills_synced():
    loader = SkillLoader()
    cats = loader.categories()
    assert len(cats) >= 9, f"Expected 9+ categories, got {len(cats)}: {cats}"


def test_total_skills_count():
    loader = SkillLoader()
    total = sum(len(loader.list_category(c)) for c in loader.categories())
    assert total >= 200, f"Expected 200+ skills, got {total}"


def test_all_categories_non_empty():
    loader = SkillLoader()
    for cat in loader.categories():
        skills = loader.list_category(cat)
        assert len(skills) > 0, f"Category '{cat}' is empty"


def test_load_real_skill():
    loader = SkillLoader()
    content = loader.load("tdd")
    assert len(content) > 50, "Skill content seems too short"


def test_search_returns_results():
    loader = SkillLoader()
    results = loader.search("review")
    assert len(results) >= 1, "Expected at least 1 result for 'review'"


def test_find_returns_category():
    loader = SkillLoader()
    result = loader.find("tdd")
    assert result is not None
    cat, path = result
    assert len(cat) > 0
    assert path.exists()
