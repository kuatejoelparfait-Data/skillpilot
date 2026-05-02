import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".devpilot"
CONFIG_FILE = CONFIG_DIR / "config.json"

class Config:
    def __init__(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(json.dumps({}))
        self._data = json.loads(CONFIG_FILE.read_text())

    def _save(self):
        CONFIG_FILE.write_text(json.dumps(self._data, indent=2))

    def set_license(self, key: str):
        self._data["license"] = key
        self._save()

    def get_license(self) -> str | None:
        return self._data.get("license")

    def is_premium(self) -> bool:
        return bool(self._data.get("license"))
