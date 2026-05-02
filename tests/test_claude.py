from unittest.mock import patch, MagicMock
from devpilot.core.claude import ClaudeClient

def test_run_returns_response():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Analysis complete")]
    )
    with patch("devpilot.core.claude.anthropic.Anthropic", return_value=mock_client):
        client = ClaudeClient(api_key="sk-ant-test")
        result = client.run(skill_prompt="Review this", user_input="def foo(): pass")
    assert "Analysis complete" in result

def test_missing_api_key_raises():
    try:
        ClaudeClient(api_key="")
        assert False, "Should raise ValueError"
    except ValueError:
        pass
