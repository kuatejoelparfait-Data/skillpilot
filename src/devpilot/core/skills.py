from pathlib import Path


def _default_skills_root() -> Path:
    try:
        from importlib.resources import files
        return Path(str(files("devpilot").joinpath("skills")))
    except Exception:
        return Path(__file__).parent.parent / "skills"


class SkillLoader:
    def __init__(self, skills_root: Path | None = None):
        self._root = skills_root or _default_skills_root()

    def categories(self) -> list[str]:
        return sorted([d.name for d in self._root.iterdir() if d.is_dir()])

    def list_category(self, category: str) -> list[str]:
        d = self._root / category
        if not d.exists():
            return []
        return sorted([f.stem for f in d.glob("*.md")])

    def list_all(self) -> dict:
        return {
            cat: {"skills": self.list_category(cat)}
            for cat in self.categories()
        }

    def find(self, name: str) -> tuple[str, Path] | None:
        for cat in self.categories():
            path = self._root / cat / f"{name}.md"
            if path.exists():
                return cat, path
        return None

    def load(self, name: str, category: str | None = None) -> str:
        if category:
            path = self._root / category / f"{name}.md"
            if not path.exists():
                raise ValueError(f"Skill '{name}' introuvable dans '{category}'.")
        else:
            result = self.find(name)
            if not result:
                raise ValueError(f"Skill '{name}' introuvable. Lance: devpilot search {name}")
            _, path = result
        return path.read_text(encoding="utf-8")

    def search(self, keyword: str) -> list[dict]:
        keyword = keyword.lower()
        results = []
        for cat in self.categories():
            for skill in self.list_category(cat):
                if keyword in skill.lower():
                    results.append({"skill": skill, "category": cat})
        return results
