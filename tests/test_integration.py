from devpilot.core.skills import SkillLoader, FREE_CATEGORIES

def test_skills_synced():
    """Vérifie que les skills ont bien été copiés dans les catégories."""
    loader = SkillLoader()
    cats = loader.categories()
    assert len(cats) >= 9, f"Expected 9+ categories, got {len(cats)}: {cats}"

def test_total_skills_count():
    loader = SkillLoader()
    total = sum(len(loader.list_category(c)) for c in loader.categories())
    assert total >= 200, f"Expected 200+ skills, got {total}"

def test_free_categories_accessible():
    loader = SkillLoader()
    for cat in FREE_CATEGORIES:
        skills = loader.list_category(cat)
        assert len(skills) > 0, f"No skills in free category: {cat}"

def test_premium_categories_exist():
    loader = SkillLoader()
    premium_cats = [c for c in loader.categories() if c not in FREE_CATEGORIES]
    assert len(premium_cats) >= 6, f"Expected 6+ premium categories, got {premium_cats}"

def test_load_real_skill():
    loader = SkillLoader()
    content = loader.load("tdd", is_premium_user=False)
    assert len(content) > 50, "Skill content seems too short"

def test_search_returns_results():
    loader = SkillLoader()
    results = loader.search("review")
    assert len(results) >= 1, "Expected at least 1 result for 'review'"
