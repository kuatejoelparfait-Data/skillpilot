from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from devpilot.cli import app

runner = CliRunner()

def test_list_command():
    mock_loader = MagicMock()
    mock_loader.return_value.list_all.return_value = {
        "engineering": {"skills": ["code-reviewer"], "free": True, "locked": False},
        "marketing": {"skills": ["seo-audit"], "free": False, "locked": True},
    }
    with patch("devpilot.cli.SkillLoader", mock_loader):
        with patch("devpilot.cli.Config") as mock_cfg:
            mock_cfg.return_value.is_premium.return_value = False
            result = runner.invoke(app, ["list"])
    assert result.exit_code == 0

def test_search_command():
    mock_loader = MagicMock()
    mock_loader.return_value.search.return_value = [
        {"skill": "code-reviewer", "category": "engineering"}
    ]
    with patch("devpilot.cli.SkillLoader", mock_loader):
        result = runner.invoke(app, ["search", "code"])
    assert result.exit_code == 0

def test_activate_bad_key():
    with patch("devpilot.cli.Config"):
        with patch("devpilot.cli.validate_license", return_value=False):
            result = runner.invoke(app, ["activate", "BAD-KEY"])
    assert result.exit_code != 0
