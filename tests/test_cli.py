from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from devpilot.cli import app

runner = CliRunner()


def test_list_command():
    mock_loader = MagicMock()
    mock_loader.return_value.list_all.return_value = {
        "engineering": {"skills": ["code-reviewer"]},
        "marketing": {"skills": ["seo-audit"]},
    }
    with patch("devpilot.cli.SkillLoader", mock_loader):
        with patch("devpilot.cli._installed_skills", return_value=[]):
            result = runner.invoke(app, ["list"])
    assert result.exit_code == 0


def test_search_command():
    mock_loader = MagicMock()
    mock_loader.return_value.search.return_value = [
        {"skill": "code-reviewer", "category": "engineering"}
    ]
    with patch("devpilot.cli.SkillLoader", mock_loader):
        with patch("devpilot.cli._installed_skills", return_value=[]):
            result = runner.invoke(app, ["search", "code"])
    assert result.exit_code == 0


def test_info_missing_skill():
    mock_loader = MagicMock()
    mock_loader.return_value.find.return_value = None
    with patch("devpilot.cli.SkillLoader", mock_loader):
        result = runner.invoke(app, ["info", "nonexistent"])
    assert result.exit_code != 0


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "skillpilot" in result.output


def test_install_missing_skill():
    mock_loader = MagicMock()
    mock_loader.return_value.load.side_effect = ValueError("Skill not found")
    with patch("devpilot.cli.SkillLoader", mock_loader):
        result = runner.invoke(app, ["install", "nonexistent"])
    assert result.exit_code != 0
