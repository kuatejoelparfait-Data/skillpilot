from pathlib import Path
from unittest.mock import patch
from devpilot.core.config import Config

def test_config_dir_created(tmp_path):
    with patch("devpilot.core.config.CONFIG_DIR", tmp_path / ".devpilot"):
        with patch("devpilot.core.config.CONFIG_FILE", tmp_path / ".devpilot/config.json"):
            c = Config()
            assert (tmp_path / ".devpilot").exists()

def test_save_and_load_license(tmp_path):
    cfg_dir = tmp_path / ".devpilot"
    cfg_file = cfg_dir / "config.json"
    with patch("devpilot.core.config.CONFIG_DIR", cfg_dir):
        with patch("devpilot.core.config.CONFIG_FILE", cfg_file):
            c = Config()
            c.set_license("DEVPILOT-ABCD1234-2026")
            assert c.get_license() == "DEVPILOT-ABCD1234-2026"

def test_is_premium_false_without_license(tmp_path):
    cfg_dir = tmp_path / ".devpilot"
    with patch("devpilot.core.config.CONFIG_DIR", cfg_dir):
        with patch("devpilot.core.config.CONFIG_FILE", cfg_dir / "config.json"):
            c = Config()
            assert c.is_premium() is False
